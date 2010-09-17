###############################################################################
###############################################################################
####################                                       ####################
####################         Miscallenous Dialog           ####################
####################                                       ####################
###############################################################################
###############################################################################
import weakref
import logging
import qt
import qtcanvas
import qttable
import math
import os.path
import itertools
import numpy
import Qwt5 as qwt
import sys

from Qub.Objects.QubPixmapDisplay import QubPixmapDisplay
from Qub.Objects.QubPixmapDisplay import QubPixmapZoomPlug

from Qub.Objects.QubDrawingManager import QubPointDrawingMgr
from Qub.Objects.QubDrawingManager import QubLineDrawingMgr
from Qub.Objects.QubDrawingManager import Qub2PointSurfaceDrawingMgr
from Qub.Objects.QubDrawingManager import QubPolygoneDrawingMgr

from Qub.Objects.QubDrawingCanvasTools import QubCanvasTarget
from Qub.Objects.QubDrawingCanvasTools import QubCanvasEllipse
from Qub.Objects.QubDrawingCanvasTools import QubCanvasAngle
from Qub.Objects.QubDrawingCanvasTools import QubCanvasCloseLinePolygone

from Qub.Objects.QubDrawingEvent import QubMoveNPressed1Point

from Qub.Widget.QubWidgetSet import QubSlider,QubColorToolMenu

from Qub.Icons.QubIcons import loadIcon

from Qub.Tools import QubImageSave

from Qub.Print.QubPrintPreview import getPrintPreviewDialog

from Qub.Widget.Graph.QubGraph import QubGraphView
from Qub.Widget.Graph.QubGraphCurve import QubGraphCurve

from Qub.Widget.QubWidgetFromUI import QubWidgetFromUI

try:
    from Qub.CTools.pixmaptools import Stat
except ImportError:
    Stat = None

####################################################################
##########                                                ##########
##########             QubMeasureListDialog               ##########
##########                                                ##########
####################################################################
## @brief Measurement tools on view
#
#this dialog must be linked with a Canvas,and an event manager
#such as :
# - QubPixmapDisplay
#
#This tool provide measurment such as:
#    - point
#    - distance
#    - surface (rectangle)
#    - angle
#
#@see Qub::Objects::QubPixmapDisplay::QubPixmapDisplay

class QubMeasureListDialog(qt.QDialog):
    ## @brief this class is use to manage drawing manager in the QListViewItem
    #@see QListViewItem
    class _ItemList(qt.QListViewItem) :
        def __init__(self,aListView,aDrawingMgr) :
            qt.QListViewItem.__init__(self,aListView)
            self.__drawingMgr = aDrawingMgr # !< the drawing manager

        def drawingMgr(self) :
            return self.__drawingMgr

    ##@param args  params are equivalent of a Dialog constructor
    # -# parent
    # -# name
    # -# modal
    # -# fl
    #@param keys this dico should contain
    # - 'canvas' this key is mandatory
    # - 'eventMgr' this key is mandatory
    # - 'matrix' this key is optional
    #@see QCanvas
    #@see QWMatrix
    #@see Qub::Objects::QubEventMgr::QubEventMgr
    def __init__(self,parent = None,name = 'MeasureWindow',
                 canvas = None,matrix = None,
                 eventMgr = None,drawingObjectLayer = None,**keys) :
        qt.QDialog.__init__(self,parent,name)

        self.__canvas = canvas
        self.__matrix = matrix
        self.__eventMgr = eventMgr
        self.__drawingObjectLayer = drawingObjectLayer

        ## Description tools table
        # (name,DrawingManager,DrawingObject,end draw callback)
        self.__tools = [('point',QubPointDrawingMgr,QubCanvasTarget,self.__endPointDrawing),
                        ('distance',QubLineDrawingMgr,qtcanvas.QCanvasLine,self.__endDistanceDrawing),
                        ('rectangle',Qub2PointSurfaceDrawingMgr,qtcanvas.QCanvasRectangle,self.__endSurfaceDrawing),
                        ('angle',QubPolygoneDrawingMgr,QubCanvasAngle,self.__endAngleDrawing),
                        ('polygon',QubPolygoneDrawingMgr,QubCanvasCloseLinePolygone,self.__defaultEnd)]

        self.__ToolIdSelected = 1
        self.__lastdrawingMgr = None
        self.__mesID = 0

        MeasureWindowLayout = qt.QVBoxLayout(self,11,6,"MeasureWindowLayout")

        layout2 = qt.QHBoxLayout(None,0,6,"layout2")
        spacer1 = qt.QSpacerItem(210,20,qt.QSizePolicy.Expanding,qt.QSizePolicy.Minimum)
        layout2.addItem(spacer1)

        self.__measureTool = qt.QToolButton(self,"__measureTool")
        listPopupMenu = self.__createPopMenu(self.__measureTool)
        self.__measureTool.setAutoRaise(True)
        self.__measureTool.setPopup(listPopupMenu)
        self.__measureTool.setPopupDelay(0)
        self.__toolSelect(self.__ToolIdSelected)
        layout2.addWidget(self.__measureTool)

        self.__activeButton = qt.QPushButton(self,"__activeButton")
        self.__activeButton.setText('Start')
        self.connect(self.__activeButton,qt.SIGNAL('clicked()'),
                     self.__startMeasure)

        layout2.addWidget(self.__activeButton)
        MeasureWindowLayout.addLayout(layout2)

        self.__measureList = qt.QListView(self,"__measureList")
        self.__measureList.addColumn(self.__tr("name"))
        self.__measureList.addColumn(self.__tr("measure"))
        self.__measureList.setSelectionMode(qt.QListView.Extended)
        self.__measurePopUp = qt.QPopupMenu(self.__measureList)
        self.__measurePopUp.insertItem('remove',self.__deleteCBK)

        colormenu = QubColorToolMenu(self.__measureList)
        self.connect(colormenu, qt.PYSIGNAL("colorSelected"),
                     self.__colorChanged)
        self.__measurePopUp.insertItem('colors',colormenu)

        self.connect(self.__measureList,qt.SIGNAL('rightButtonPressed(QListViewItem*,const QPoint &,int)'),
                     self.__measurePopUpDisplay)
        MeasureWindowLayout.addWidget(self.__measureList)

        self.resize(qt.QSize(347,251).expandedTo(self.minimumSizeHint()))
        self.clearWState(qt.Qt.WState_Polished)

        self.__xPixelSize = 0
        self.__yPixelSize = 0
        self.__defaultColor = qt.Qt.black

    ##@brief set horizontal pixel size (scale)
    #@param size pixel size in meter
    def setXPixelSize(self,size) :
        try:
            self.__xPixelSize = abs(size)
        except:
            self.__xPixelSize = 0

    ##@brief set vertical pixel size (scale)
    #@param size pixel size in meter
    def setYPixelSize(self,size) :
        try:
            self.__yPixelSize = abs(size)
        except:
            self.__yPixelSize = 0

    ##@brief set the default color of the drawing measure
    #@param color qt.QColor
    #@see QColor
    def setDefaultColor(self,color) :
        self.__defaultColor = color

    def __tr(self,s,c = None):
        return qt.qApp.translate("MeasureWindow",s,c)

    def __createPopMenu(self,parent) :
        popMenu = qt.QPopupMenu(parent)

        for i,tool in enumerate(self.__tools) :
            popMenu.insertItem(tool[0],i)

        self.connect(popMenu, qt.SIGNAL("activated(int )"),
                     self.__toolSelect)
        return popMenu

    def __toolSelect(self,idTool) :
        self.__ToolIdSelected = idTool
        self.__measureTool.setText(self.__tools[self.__ToolIdSelected][0])

    def __startMeasure(self) :
        try:
            if self.__lastdrawingMgr is not None :
                self.__lastdrawingMgr.stopDrawing()
            self.__lastdrawingMgr = self.__tools[self.__ToolIdSelected][1](self.__canvas,self.__matrix)
            if self.__ToolIdSelected == 0:
                self.__lastdrawingMgr.setDrawingEvent(QubMoveNPressed1Point)
            elif self.__ToolIdSelected == 1:
                self.__followMullot = self.__tools[0][1](self.__canvas,self.__matrix)
                self.__followMullot.addDrawingObject(self.__tools[0][2](self.__canvas))
                self.__followMullot.setDrawingEvent(QubMoveNPressed1Point)
                self.__followMullot.setExclusive(False)
                self.__followMullot.setColor(self.__defaultColor)
                self.__eventMgr.addDrawingMgr(self.__followMullot)
                self.__followMullot.startDrawing()
            self.__lastdrawingMgr.setAutoDisconnectEvent(True)
            drawingobject = self.__tools[self.__ToolIdSelected][2](self.__canvas)
            self.__lastdrawingMgr.addDrawingObject(drawingobject)
            self.__eventMgr.addDrawingMgr(self.__lastdrawingMgr)
            self.__lastdrawingMgr.startDrawing()
            self.__lastdrawingMgr.setEndDrawCallBack(self.__tools[self.__ToolIdSelected][3])
            anItemList = QubMeasureListDialog._ItemList(self.__measureList,self.__lastdrawingMgr)
            anItemList.setText(0,'Mes %d' % self.__mesID)
            self.__lastdrawingMgr.setColor(self.__defaultColor)
            self.__lastdrawingMgr.setActionInfo('Drawing Mesure %d' % self.__mesID)
            self.__mesID += 1

            if self.__drawingObjectLayer:
                self.__lastdrawingMgr.setZ(self.__drawingObjectLayer)
        except:
            import traceback
            traceback.print_exc()

    def __endPointDrawing(self,drawingMgr) :
        anItem = self.__getItemWithDrawingObject(drawingMgr)
        if self.__lastdrawingMgr == drawingMgr :
            self.__lastdrawingMgr = None
        if anItem is not None :
            anItem.setText(1,"Pos (%d,%d)" % drawingMgr.point())

    def __endDistanceDrawing(self,drawingMgr) :
        anItem = self.__getItemWithDrawingObject(drawingMgr)
        if self.__lastdrawingMgr == drawingMgr :
            self.__lastdrawingMgr = None
        if anItem is not None :
            x1,y1,x2,y2 = anItem.drawingMgr().points()
            width = abs(x1 - x2)
            height = abs(y1 - y2)
            if(self.__xPixelSize is not None and self.__xPixelSize and
               self.__yPixelSize is not None and self.__yPixelSize) :
                dist = self.__getDistanceString(math.sqrt(((width * self.__xPixelSize) ** 2) +
                                                          ((height * self.__yPixelSize) ** 2)))

                anItem.setText(1,"distance -> %sm" % dist)
            else :
                anItem.setText(1,'distance -> %d pixel' % math.sqrt(width ** 2 + height ** 2))
        self.__followMullot = None

    def __endSurfaceDrawing(self,drawingMgr) :
        anItem = self.__getItemWithDrawingObject(drawingMgr)
        if self.__lastdrawingMgr == drawingMgr :
            self.__lastdrawingMgr = None
        if anItem is not None :
            width = anItem.drawingMgr().width()
            height = anItem.drawingMgr().height()
            if(self.__xPixelSize is not None and self.__xPixelSize and
               self.__yPixelSize is not None and self.__yPixelSize) :
                distwidth = self.__getDistanceString(width * self.__xPixelSize)
                distheight = self.__getDistanceString(height * self.__yPixelSize)
                surface = self.__getSurfaceString(width * self.__xPixelSize * height * self.__yPixelSize)
                anItem.setText(1,"distance (x,y) -> (%sm,%sm), surface %sm2" % (distwidth,distheight,surface))
            else :
                anItem.setText(1,'distance (x,y) -> (%d,%d) pixel' % (width,height))

    def __endAngleDrawing(self,drawingMgr) :
        anItem = self.__getItemWithDrawingObject(drawingMgr)
        if self.__lastdrawingMgr == drawingMgr :
            self.__lastdrawingMgr = None
        if anItem is not None :
            points = []
            points.extend(drawingMgr.points())
            jx,jy = points.pop(0)
            vect = [(x - jx,y - jy) for x,y in points]
            (x1,y1),(x2,y2) = vect
            if(self.__xPixelSize is not None and self.__xPixelSize and
               self.__yPixelSize is not None and self.__yPixelSize) :
                x1 *= self.__xPixelSize;x2 *= self.__xPixelSize
                y1 *= self.__yPixelSize;y2 *= self.__yPixelSize

            scalar = x1 * x2 + y1 * y2
            dist1 = math.sqrt(x1 **2 + y1 **2)
            dist2 = math.sqrt(x2 **2 + y2 ** 2)
            angle = math.acos(scalar/(dist1*dist2))
            anItem.setText(1,"angle -> %f deg" % (angle * 180 / math.pi))

    def __defaultEnd(self,drawingMgr) :
        anItem = self.__getItemWithDrawingObject(drawingMgr)
        if self.__lastdrawingMgr == drawingMgr :
            self.__lastdrawingMgr = None

    def __getDistanceString(self,dist) :
        for unit,unitString in [(1e-3,'m'),(1e-6,'\xb5'),(1e-9,'n'),(1e-12,'p')] :
            tmpDist = dist / unit
            if 1. < tmpDist < 1000. :
                return "%.2f %s" % (tmpDist,unitString)
        return "%.2f" % dist

    def __getSurfaceString(self,surface) :
        for unit,unitString in [(1e-6,'m'),(1e-12,'\xb5'),(1e-18,'n'),(1e-24,'p')] :
            tmpDist = surface / unit
            if 0.01 <= tmpDist < 1000. :
                return "%.2f %s" % (tmpDist,unitString)
        return "%.2f" % surface

    def __getItemWithDrawingObject(self,drawingMgr) :
        Item = self.__measureList.firstChild()
        while Item :
            if Item.drawingMgr() == drawingMgr :
                break
            Item = Item.nextSibling()
        return Item

    def __deleteCBK(self,item) :
        for item in self.__getSelectedIterator() :
            item.drawingMgr().hide()
            self.__measureList.takeItem(item)
    def __colorChanged(self,color) :
        for item in self.__getSelectedIterator() :
            item.drawingMgr().setColor(color)

    def __getSelectedIterator(self) :
        Item = self.__measureList.firstChild()
        while Item :
            NextItem = Item.nextSibling()
            if Item.isSelected() :
                yield Item
            Item = NextItem


    def __measurePopUpDisplay(self,item,point,columnid) :
        self.__measurePopUp.exec_loop(point)

    def closeEvent(self,closeEvent)  :
        self.hide()
        self.__lastdrawingMgr = None

####################################################################
##########                                                ##########
##########               QubSaveImageWidget               ##########
##########                                                ##########
####################################################################
##@brief this widget is use to save an image
#
#With this tool, you can save an image in JPEG or PNG
class QubSaveImageWidget(qt.QWidget):
    OUTPUT_FORMATS = ('png', 'jpeg','svg')
    ##@brief this is the plug for the QubImage2Pixmap Object
    #@see Qub::Objects::QubImage2Pixmap::QubImage2Pixmap
    class _Image2Pixmap(QubPixmapZoomPlug) :
        def __init__(self,dialog,receiver,buttonFile) :
            QubPixmapZoomPlug.__init__(self,receiver)
            self.__inPollFlag = False
            self.__lastImage = None
            self.__buttonFile = buttonFile
            self.__dialog = weakref.ref(dialog)
            self.__dataZoom = None
            self.__snapFlag = False

        def setPixmap(self,pixmap,image) :
            self.__inPollFlag = False
            if self.__dataZoom :
                zoomx,zoomy = self.__dataZoom.zoom()
                zoom = min(zoomx,zoomy)
                imZoomed = image.scale(image.width() * zoom,image.height() * zoom)
            else:
                imZoomed = image
            QubPixmapZoomPlug.setPixmap(self,pixmap,imZoomed)
            if self.__dialog:
                dialog = self.__dialog()
                if dialog and dialog.vectorDrawing :
                    dialog.vectorDrawing.setZoom(float(pixmap.width()) / image.width())
                    dialog.vectorDrawing.setSize(pixmap.width(),pixmap.height())
            if not self.__buttonFile.isEnabled() :
                self.__buttonFile.setEnabled(True)
            self.__lastImage = image
            if self.__snapFlag:
                self.__snapFlag = False
                try:
                    dialog = self.__dialog()
                    if dialog:
                        dialog.snapCBK()
                except:
                    import traceback
                    traceback.print_exc()
            return True # One Shot

        def refresh(self,withSnap = False) :
            self.__snapFlag = self.__snapFlag or withSnap
            if self._mgr is not None and not self.__inPollFlag :
                self.__inPollFlag = True
                mgr = self._mgr()
                if mgr:
                    mgr.plug(self)
                    mgr.refresh()

        def setInPoll(self) :
            self.__inPollFlag = True

        def setDataZoom(self,zoom) :
            self.__dataZoom = zoom

        def getImage(self) :
            return self.__lastImage

    class _Vector(qtcanvas.QCanvasRectangle) :
        def __init__(self,srccanvas,matrix,canvas) :
            qtcanvas.QCanvasRectangle.__init__(self,canvas)
            self.__srczoom = matrix and matrix.m11() or 1
            self.__items = []
            self.__zoom = 1
            try:
                for item in srccanvas.allItems() :
                    if item.isVisible() :
                        if hasattr(item,'setScrollView') : # remove standalone items
                            continue
                        newObject = item.__class__(item)
                        newObject.setCanvas(None)
                        self.__items.append(newObject)
            except AttributeError,err:
                pass
        def setZoom(self,zoom) :
            self.__zoom = zoom

        def getVectorZoom(self) :
            return self.__srczoom

        def draw(self,p) :
            zoom = self.__zoom / self.__srczoom
            nwm = qt.QWMatrix(p.worldMatrix())
            nwm.scale(zoom,zoom)
            np = qt.QPainter(p.device())
            np.setWorldMatrix(nwm)
            for item in self.__items :
                item.draw(np)

        def getItems(self) :
            return self.__items
    ##@brief Dialog to take a snapshot and to save it in different format
    #@param parent is supposed to be the brick itself in order to acces its
    #@param name the name of the widget dialog
    def __init__(self,parent=None,name='Save Image',canvas = None,matrix = None) :
        qt.QWidget.__init__(self,parent,name)
        self.vectorDrawing = None
        self.__canvas = canvas
        self.__matrix = matrix

        self.resize(350, 350)
        self.setIcon(loadIcon('save.png'))

        vlayout = qt.QVBoxLayout(self)
        vlayout.setMargin(10)

        self.__ImView = QubPixmapDisplay(self)
        self.__ImView.setScrollbarMode("Fit2Screen")

        vlayout.addWidget(self.__ImView)
                  ####### SNAP SHOT SETTINGS #######
        box1 = qt.QHGroupBox("Snapshot settings",self)

        grid1 = qt.QWidget(box1)
        qt.QGridLayout(grid1, 4, 3, 0, 2)

        label1 = qt.QLabel("File prefix:",grid1)
        grid1.layout().addWidget(label1, 1, 0)
        self.__filePrefix = qt.QLineEdit(grid1)
        grid1.layout().addMultiCellWidget(self.__filePrefix,1,1,1,2)

        label2 = qt.QLabel("Directory:",grid1)
        grid1.layout().addWidget(label2, 0, 0)
        self.__fileDirectory = qt.QLineEdit(grid1)
        grid1.layout().addWidget(self.__fileDirectory, 0, 1)

        self.__browseButton = qt.QToolButton(grid1)
        self.__browseButton.setTextLabel("Browse")
        self.__browseButton.setUsesTextLabel(True)
        self.__browseButton.setTextPosition(qt.QToolButton.BesideIcon)
        qt.QObject.connect(self.__browseButton,qt.SIGNAL("clicked()"),self.__browseButtonClicked)
        grid1.layout().addWidget(self.__browseButton, 0, 2)

        label3 = qt.QLabel("File index:",grid1)
        grid1.layout().addWidget(label3, 2, 0)
        self.__fileIndex = qt.QLineEdit(grid1)
        self.__fileIndex.setValidator(qt.QIntValidator(self))
        grid1.layout().addWidget(self.__fileIndex, 2, 1)

        self.__resetButton = qt.QToolButton(grid1)
        self.__resetButton.setTextLabel("Reset")
        self.__resetButton.setUsesTextLabel(True)
        self.__resetButton.setTextPosition(qt.QToolButton.BesideIcon)
        qt.QObject.connect(self.__resetButton,qt.SIGNAL("clicked()"),self.__resetButtonClicked)
        grid1.layout().addWidget(self.__resetButton, 2, 2)

        label4 = qt.QLabel("Format:",grid1)
        grid1.layout().addWidget(label4, 3, 0)
        self.__imageFormat = qt.QComboBox(grid1)
        grid1.layout().addMultiCellWidget(self.__imageFormat,3,3,1,2)
        for t in QubSaveImageWidget.OUTPUT_FORMATS:
            self.__imageFormat.insertItem(t)

        vlayout.addWidget(box1)
                     ####### END SETTINGS #######
        iconSet = qt.QIconSet(loadIcon("save.png"))
        self.__buttonFile = qt.QPushButton(iconSet, "", self)
        self.__buttonFile.setEnabled(False)
        qt.QObject.connect(self.__buttonFile, qt.SIGNAL("clicked()"),self.snapCBK)
        self.__imagePlug = QubSaveImageWidget._Image2Pixmap(self,self.__ImView,self.__buttonFile)

        iconSet = qt.QIconSet(loadIcon("snapshot.png"))
        self.__snapButton = qt.QPushButton(iconSet, "", self)
        qt.QObject.connect(self.__snapButton, qt.SIGNAL("clicked()"),self.__refresh)

        self.__vectorCheck = qt.QCheckBox(self)
        self.__vectorCheck.setText('vector')
        qt.QObject.connect(self.__vectorCheck,qt.SIGNAL("toggled(bool)"),self.__drawVector)

        hlayout = qt.QHBoxLayout(vlayout)
        hlayout.addWidget(self.__snapButton)
        hlayout.addSpacing(10)
        hlayout.addWidget(self.__buttonFile)
        hlayout.addSpacing(10)
        hlayout.addWidget(self.__vectorCheck)

                         ####### INIT #######
        self.__filePrefix.setText("snapshot")
        self.__fileDirectory.setText("/tmp")
        self.__fileIndex.setText("1")
        index = list(QubSaveImageWidget.OUTPUT_FORMATS).index('png')
        self.__imageFormat.setCurrentItem(index)

    def takeSnap(self) :
        self.__imagePlug.refresh(True)

    ##@brief Called when the Save button is pressed
    def snapCBK(self):
        directory = self.__fileDirectory.text().latin1()
        prefix = self.__filePrefix.text().latin1()
        index,valid = self.__fileIndex.text().toInt()
        format = self.__imageFormat.currentText().ascii()
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except OSError,diag:
                logging.getLogger().error("QubSaveImageDialog: error trying to create the directory %s (%s)" % (directory,str(diag)))
                return
            else:
                logging.getLogger().info("QubSaveImageDialog: created the directory %s" % directory)

        path = os.path.join(directory, prefix)
        filename = path + '_%d%s%s' % (index, os.path.extsep, format)

        self.__fileIndex.setText('%d' % (index + 1))

        if format == 'png' or format == 'jpeg' or format == 'svg' :
            QubImageSave.save(filename,self.__imagePlug.getImage(),
                              self.__vectorCheck.isOn() and self.vectorDrawing and self.vectorDrawing.getItems() or None,
                              self.vectorDrawing and self.vectorDrawing.getVectorZoom() or 1,format.upper())
        else:                           # TODO
            pass
    ##@brief set caption prefix
    def setCaptionPrefix(self,prefix) :
        self.setCaption(prefix)
    ##@brief set the data zoom.
    #the image can be already zoomed before image2pixmap module. With this first zoom, we calculate the whole zoom needed
    def setDataZoom(self,zoom) :
        self.__imagePlug.setDataZoom(zoom)
    ##You have to call this methode at least one to link
    #the save image dialogue to QubImage2Pixmap Object
    #@see Qub::Objects::QubImage2Pixmap::QubImage2Pixmap
    def setImage2Pixmap(self,image2pixmap) :
        self.__imagePlug.setInPoll()
        image2pixmap.plug(self.__imagePlug)

    ##@brief set the save path
    def setSavePath(self,path) :
        self.__fileDirectory.setText(path)
    ## It use the refresh the old image with the current
    def refresh(self) :
        self.__imagePlug.refresh()

    def __drawVector(self,aFlag) :
        if aFlag :
            self.__refresh()
            self.vectorDrawing.show()
        else:
            self.vectorDrawing.hide()

    def __refresh(self) :
        for item in self.__ImView.canvas().allItems() :
            item.setCanvas(None)
        self.vectorDrawing = None
        if self.__vectorCheck.isOn() :
            self.vectorDrawing = QubSaveImageWidget._Vector(self.__canvas,self.__matrix,self.__ImView.canvas())
            self.vectorDrawing.show()
        self.__imagePlug.refresh()

    def __browseButtonClicked(self) :
        get_dir = qt.QFileDialog(self)
        s=self.font().pointSize()
        f = get_dir.font()
        f.setPointSize(s)
        get_dir.setFont(f)
        get_dir.updateGeometry()
        d=get_dir.getExistingDirectory(self.__fileDirectory.text(),self,"",
                                       "Select a directory",True,False)
        if d is not None and len(d)>0:
            self.__fileDirectory.setText(d)

    def __resetButtonClicked(self):
        self.__fileIndex.setText('1')

####################################################################
##########                                                ##########
##########               QubSaveImageDialog               ##########
##########                                                ##########
####################################################################
##@brief this dialogue is use to save an image
#
#With this tool, you can save an image in JPEG or PNG
#@see QubSaveImageWidget
class QubSaveImageDialog(qt.QDialog) :
    def __init__(self,parent=None,name='Save Image',canvas = None,matrix = None) :
        qt.QDialog.__init__(self,parent,name)
        self.__saveImage = QubSaveImageWidget(self,name,canvas,matrix)
        layout = qt.QHBoxLayout(self)
        layout.addWidget(self.__saveImage)
        self.resize(350, 350)

    def __nonzero__(self) :
        return True

    def __getattr__(self, attr):
        if not attr.startswith("__") :
            try:
                return getattr(self.__saveImage,attr)
            except AttributeError,err:
                raise AttributeError,'QubSaveImageDialog instance has not attribute %s' % attr
        else:
                raise AttributeError,'QubSaveImageDialog instance has not attribute %s' % attr
####################################################################
##########                                                ##########
##########                QubDataStatWidget               ##########
##########                                                ##########
####################################################################
##@brief widget to display statistique of data
#
from Qub.Widget.QubDataStat import Histogram
class QubDataStatWidget(Histogram) :
    def __init__(self,parent = None,name = '',f = 0) :
        Histogram.__init__(self,parent,name,f)
        self.setIcon(loadIcon("histogram.png"))
        self.__data = None
        self.__roi = None
        nbChannelWidget = self.child('__numberOfChannels')
        nbChannelWidget.setValidator(qt.QIntValidator(nbChannelWidget))
        nbChannelWidget.setText('10')
        qt.QObject.connect(nbChannelWidget,qt.SIGNAL('returnPressed ()'),self.__refreshIdle)
        qt.QObject.connect(nbChannelWidget,qt.SIGNAL('lostFocus ()'),self.__refreshIdle)

        for widgetName in ['__minHisto','__maxHisto'] :
            widget = self.child(widgetName)
            widget.setValidator(qt.QDoubleValidator(widget))
            qt.QObject.connect(widget,qt.SIGNAL('returnPressed ()'),self.__refreshIdle)
            qt.QObject.connect(widget,qt.SIGNAL('lostFocus ()'),self.__refreshIdle)


        ####### PRINT ACTION #######
        from Qub.Widget.QubActionSet import QubPrintPreviewAction
        printAction = QubPrintPreviewAction(name="print",group="admin")
        printAction.previewConnect(getPrintPreviewDialog())

        graphFrame = self.child('__graphFrame')
        self.__graph = QubGraphView(parent = graphFrame,actions = [printAction])
        layout = graphFrame.layout()
        layout.insertWidget(1,self.__graph)
        self.__curve = QubGraphCurve('Data Statistic')
        self.__curve.attach(self.__graph)
        self.__curve.setStyle(self.__curve.Sticks)
        self.__curve.setPen(qt.QPen(qt.Qt.red,2))

        self.__zoom = qwt.QwtPlotZoomer(self.__graph.xBottom,self.__graph.yRight,
                                        qwt.QwtPicker.DragSelection,
                                        qwt.QwtPicker.AlwaysOff,
                                        self.__graph.canvas())
        self.__zoom.setMousePattern([qwt.QwtEventPattern.MousePattern(qt.Qt.LeftButton, qt.Qt.NoButton),
                                     qwt.QwtEventPattern.MousePattern(qt.Qt.MidButton, qt.Qt.NoButton),
                                     qwt.QwtEventPattern.MousePattern(qt.Qt.RightButton, qt.Qt.NoButton),
                                     qwt.QwtEventPattern.MousePattern(qt.Qt.LeftButton, qt.Qt.ShiftButton),
                                     qwt.QwtEventPattern.MousePattern(qt.Qt.MidButton, qt.Qt.ShiftButton),
                                     qwt.QwtEventPattern.MousePattern(qt.Qt.RightButton, qt.Qt.ShiftButton)])
        self.__zoom.setRubberBandPen(qt.QPen(qt.Qt.blue))
        qt.QObject.connect(self.__zoom,qt.SIGNAL('zoomed(const QwtDoubleRect&)'),self.__zoomed)

        self.__idle = qt.QTimer(self)
        self.connect(self.__idle,qt.SIGNAL('timeout()'),self.__refresh)

    def show(self) :
        QubWidgetFromUI.show(self)
        self.setMinimumSize(self.sizeHint())
        self.__zoom.setZoomBase()
        self.__refreshIdle()

    def setData(self,data) :
        self.__data = data
        self.__refreshIdle()

    def setDataRoi(self,x,y,width,height) :
        self.__roi = (x,y,width,height)
        self.__refreshIdle()

    def __refreshIdle(self) :
        if self.isVisible() and not self.__idle.isActive() :
            self.__idle.start(0)

    def __refresh(self) :
        self.__idle.stop()
        if self.isVisible() and self.__data is not None:
            if self.__roi is not None:
                x,y,width,height = self.__roi
                if x < 0: x = 0
                if y < 0 : y = 0
                data = self.__data[y:y + height,x:x + width]
            else:
                data = self.__data

            height,width = data.shape
            nbPixel = height * width
            integralVal = data.sum()
            average = float(integralVal) / nbPixel
            minVal,maxVal = data.min(),data.max()
            stdDeviation = data.std()

            for value,childName in [(height,'__heightLE'),(width,'__widthLE'),
                                    (minVal,'__minValLE'),(maxVal,'__maxValLE'),
                                    (integralVal,'__integralLE'),(average,'__averageLE'),
                                    (nbPixel,'__nbPixelLE'),(stdDeviation,'__stdDevLE')] :
                childWidget = self.child(childName)
                if isinstance(value,int):
                    childWidget.setText('%d' % value)
                else:
                    childWidget.setText('%.2f' % value)

            minHistoWidget = self.child('__minHisto')
            stringVal = minHistoWidget.text()
            minHisto,ok = stringVal.toFloat()
            if not ok: minHisto = minVal

            maxHistoWidget = self.child('__maxHisto')
            stringVal = maxHistoWidget.text()
            maxHisto,ok = stringVal.toFloat()
            if not ok: maxHisto = maxVal

            nbChannelWidget = self.child('__numberOfChannels')
            stringVal = nbChannelWidget.text()
            bins,ok = stringVal.toInt()

            if ok:
                if Stat:
                    YHisto,XHisto = Stat.histo(data,bins,minHisto,maxHisto)
                else:
                    YHisto,XHisto = numpy.histogram(data,bins = bins,range=[minHisto,maxHisto])
                self.__curve.setData(XHisto,YHisto)
                self.__graph.replot()

    def __zoomed(self,rect) :
        if rect == self.__zoom.zoomBase() :
            self.__graph.setAxisAutoScale(self.__graph.xBottom)
            self.__graph.replot()
            self.__zoom.setZoomBase()

##@brief the data statistique dialog
#
#@see QubDataStatWidget
class QubDataStatDialog(qt.QDialog) :
    def __init__(self,parent=None,name='Data stat',canvas = None,matrix = None) :
        qt.QDialog.__init__(self,parent,name)
        self.__dataStat = QubDataStatWidget(self,name)
        layout = qt.QHBoxLayout(self)
        layout.addWidget(self.__dataStat)

    def show(self) :
        qt.QDialog.show(self)
        self.setMinimumSize(self.sizeHint())

    def __nonzero__(self) :
        return True

    def __getattr__(self, attr):
        if not attr.startswith("__") :
            try:
                return getattr(self.__dataStat,attr)
            except AttributeError,err:
                raise AttributeError,'QubDataStatDialog instance has not attribute %s' % attr
        else:
                raise AttributeError,'QubDataStatDialog instance has not attribute %s' % attr

####################################################################
##########                                                ##########
##########        QubBrightnessContrastDialog             ##########
##########                                                ##########
####################################################################
##@brief Brightness and contrast control for falcon device
#The popup dialog display two slider:
# -# for the brightness
# -# for the contrast
class QubBrightnessContrastDialog(qt.QDialog):
    def __init__(self, parent):
        qt.QDialog.__init__(self, parent)

        """
        variables
        """
        self.__camera = None

        self.__contrast = 0
        self.__contrastMin = 0
        self.__contrastMax = 200

        self.__brightness = 0
        self.__brightnessMin = 0
        self.__brightnessMax = 255

        """
        widget
        """
        vlayout = qt.QVBoxLayout(self)
        vlayout.setMargin(10)

        """
        contrast updater
        """
        self.contrastLabel = qt.QLabel("Contrast:", self)
        vlayout.addWidget(self.contrastLabel)

        self.contrastSlider = QubSlider(self.__contrastMin,
                                        self.__contrastMax,
                                        10, self.__contrast,
                                        qt.Qt.Horizontal,self)
        self.contrastSlider.setMinimumWidth(100)
        self.connect(self.contrastSlider, qt.PYSIGNAL("sliderChanged"),
                     self.setContrast)
        vlayout.addWidget(self.contrastSlider)

        vlayout.addSpacing(10)

        """
        brightness updater
        """
        self.brightLabel = qt.QLabel("Brightness:", self)
        vlayout.addWidget(self.brightLabel)

        self.brightnessSlider = QubSlider(self.__brightnessMin,
                                           self.__brightnessMax,
                                           10, self.__brightness,
                                           qt.Qt.Horizontal, self)
        self.connect(self.brightnessSlider, qt.PYSIGNAL("sliderChanged"),
                     self.setBrightness)
        vlayout.addWidget(self.brightnessSlider)

    ##@brief set the constrast range
    def setContrastLimits(self, contrastMin, contrastMax):
        self.__contrastMin = contrastMin
        self.__contrastMax = contrastMax

        self.setContrast(self.__contrast)
        self.contrastChanged(self.__contrast)
    ##@brief set the contrast
    #
    #Callback of the contrast slider
    #@param contrast must be between contrastMax and contrastMin
    #@see setContrastLimits
    def setContrast(self, contrast):
        self.__contrast = contrast
        if contrast < self.__contrastMin:
            self.__contrast = self.__contrastMin
        if contrast > self.__contrastMax:
            self.__contrast = self.__contrastMax

        if self.__camera is not None:
            self.__camera.setContrast(self.__contrast)

    def contrastChanged(self, contrast):
        self.__contrast = contrast

        if contrast < self.__contrastMin:
            self.__contrast = self.__contrastMin

        if contrast > self.__contrastMax:
            self.__contrast = self.__contrastMax

        self.contrastSlider.setValue(self.__contrast)

    ##@brief set the brightness range
    def setBrightnessLimits(self, brightnessMin, brightnessMax):
        print "_)&*(*)&(*&()&*_()*&_&*()*&_)(*&_*&()*&_)&*(*_)(&*_&*()&*_)&*(_************"
        self.__brightnessMin = brightnessMin
        self.__brightnessMax = brightnessMax

        self.setBrightness(self.__brightness)
        self.BrightnessChanged(self.__brightness)


    ##@brief set the brightness
    #
    #Callback of the brightness slider
    #@param brightness must be between brightnessMax and brightnessMin
    #@see setBrightnessLimits
    def setBrightness(self, brightness):
        self.__brightness = brightness
        if brightness < self.__brightnessMin:
            self.__brightness = self.__brightnessMin
        if brightness > self.__brightnessMax:
            self.__brightness = self.__brightnessMax

        if self.__camera is not None:
            self.__camera.setBrightness(self.__brightness)

    def brightnessChanged(self, brightness):
        self.__brightness = brightness
        if brightness < self.__brightnessMin:
            self.__brightness = self.__brightnessMin
        if brightness > self.__brightnessMax:
            self.__brightness = self.__brightnessMax

        self.brightnessSlider.setValue(self.__brightness)
    ##@brief set the camera hardware object
    #
    #You have to call this methode at least one to set the hardware object
    #for a full init of this dialog
    def setCamera(self, camera):
        self.__camera = camera

        if self.__camera is not None:
            self.contrastChanged(self.__camera.getContrast())
            self.brightnessChanged(self.__camera.getBrightness())

    def show(self):
        if self.__camera is not None:
            self.contrastChanged(self.__camera.getContrast())
            self.brightnessChanged(self.__camera.getBrightness())

        qt.QDialog.show(self)






































####################################################################
##########                                                ##########
##########             QubImageTuningDialog               ##########
##########                                                ##########
####################################################################
##@brief Brightness and contrast control for falcon device
#The popup dialog displays N sliders if attribute is avaliable:
# - for the brightness
# - for the contrast
# - for the gain
# - for the gamma

#TODO : 
# - connect qlineedit display of % to allow changing by typing a number.

class QubBrightnessContrastDialog(qt.QDialog):

    def __init__(self, parent):
        qt.QDialog.__init__(self, parent)

        """
        variables
        """
        self.__camera = None

        self.__brightness = 0
        self.__brightnessMin = 0
        self.__brightnessMax = 123
        self.__brightnessExists = False

        self.__contrast = 0
        self.__contrastMin = 0
        self.__contrastMax = 123
        self.__contrastExists = False

        self.__gain = 0
        self.__gainMin = 3.14
        self.__gainMax = 123
        self.__gainExists = False

        self.__gamma = 0
        self.__gammaMin = 0
        self.__gammaMax = 123
        self.__gammaExists = False


        print "--init of QubImageTuningDialog"

        """
        widget
        """
        vlayout = qt.QVBoxLayout(self, -1, 0, "layoutOfQubImageTuningDialog")


        """
        BRIGHTNESS updater
        """
        # print "--QubDialog.py--init--self.__brightnessMax=", self.__brightnessMax
        self.brightnessUpdaterLayout = qt.QHBoxLayout(vlayout, -1, "brightnessUpdaterLayout")
        self.brightnessUpdaterLayout.addSpacing(5)

        '''label'''
        self.brightnessLabel = qt.QLabel("Brightness:", self)
        self.brightnessUpdaterLayout.addWidget(self.brightnessLabel)

        '''Slider'''
        self.brightnessSlider = QubSlider(self.__brightnessMin,
                                    self.__brightnessMax,
                                    5, self.__brightness,
                                    qt.Qt.Horizontal,self)
        self.connect(self.brightnessSlider, qt.PYSIGNAL("sliderChanged"),
                     self.setBrightness)
        self.brightnessSlider.setMinimumWidth(100)
        self.brightnessUpdaterLayout.addWidget(self.brightnessSlider)

        '''Value in percentage'''
        self.brightnessPCValue = qt.QLineEdit("%d"%int(self.__brightness), self)
        self.brightnessUpdaterLayout.addWidget(self.brightnessPCValue)
        self.brightnessPCValue.setFixedWidth(30)
        self.brightnessPCLabel = qt.QLabel("%", self)
        self.brightnessUpdaterLayout.addWidget(self.brightnessPCLabel)
        self.brightnessUpdaterLayout.addSpacing(10)

        '''abs value'''
        self.brightnessAbsLabel = qt.QLabel("[%s/%s]"%(self.__brightness, self.__brightnessMax), self)
        self.brightnessUpdaterLayout.addWidget(self.brightnessAbsLabel)
        self.brightnessAbsLabel.setFixedWidth(100)

        vlayout.addLayout(self.brightnessUpdaterLayout)
        vlayout.addSpacing(1)


        """
        CONTRAST updater
        """
        # print "--QubDialog.py--init--self.__contrastMax=", self.__contrastMax
        self.contrastUpdaterLayout = qt.QHBoxLayout(vlayout, -1, "contrastUpdaterLayout")
        self.contrastUpdaterLayout.addSpacing(5)

        '''label'''
        self.contrastLabel = qt.QLabel("Contrast:", self)
        self.contrastUpdaterLayout.addWidget(self.contrastLabel)

        '''Slider'''
        self.contrastSlider = QubSlider(self.__contrastMin,
                                    self.__contrastMax,
                                    5, self.__contrast,
                                    qt.Qt.Horizontal,self)
        self.connect(self.contrastSlider, qt.PYSIGNAL("sliderChanged"),
                     self.setContrast)
        self.contrastSlider.setMinimumWidth(100)
        self.contrastUpdaterLayout.addWidget(self.contrastSlider)

        '''Value in percentage'''
        self.contrastPCValue = qt.QLineEdit("%d"%int(self.__contrast), self)
        self.contrastUpdaterLayout.addWidget(self.contrastPCValue)
        self.contrastPCValue.setFixedWidth(30)
        self.contrastPCLabel = qt.QLabel("%", self)
        self.contrastUpdaterLayout.addWidget(self.contrastPCLabel)
        self.contrastUpdaterLayout.addSpacing(10)

        '''abs value'''
        self.contrastAbsLabel = qt.QLabel("[%s/%s]"%(self.__contrast, self.__contrastMax), self)
        self.contrastUpdaterLayout.addWidget(self.contrastAbsLabel)
        self.contrastAbsLabel.setFixedWidth(100)

        vlayout.addLayout(self.contrastUpdaterLayout)
        vlayout.addSpacing(1)


        """
        GAIN updater
        """
        # print "--QubDialog.py--init--self.__gainMax=", self.__gainMax
        self.gainUpdaterLayout = qt.QHBoxLayout(vlayout, -1, "gainUpdaterLayout")
        self.gainUpdaterLayout.addSpacing(5)

        '''label'''
        self.gainLabel = qt.QLabel("Gain:", self)
        self.gainUpdaterLayout.addWidget(self.gainLabel)

        '''Slider'''
        self.gainSlider = QubSlider(self.__gainMin,
                                    self.__gainMax,
                                    5, self.__gain,
                                    qt.Qt.Horizontal, self)
        self.connect(self.gainSlider, qt.PYSIGNAL("sliderChanged"), self.setGain)
        self.gainSlider.setMinimumWidth(100)
        self.gainUpdaterLayout.addWidget(self.gainSlider)

        '''Value in percentage'''
        self.gainPCValue = qt.QLineEdit("%d"%int(self.__gain), self)
        self.gainUpdaterLayout.addWidget(self.gainPCValue)
        self.gainPCValue.setFixedWidth(30)
        self.gainPCLabel = qt.QLabel("%", self)
        self.gainUpdaterLayout.addWidget(self.gainPCLabel)
        self.gainUpdaterLayout.addSpacing(10)

        '''abs value'''
        self.gainAbsLabel = qt.QLabel("[%s/%s]"%(self.__gain, self.__gainMax), self)
        self.gainUpdaterLayout.addWidget(self.gainAbsLabel)
        self.gainAbsLabel.setFixedWidth(100)

        vlayout.addLayout(self.gainUpdaterLayout)
        vlayout.addSpacing(1)

        """
        GAMMA updater
        """
        # print "--QubDialog.py--init--self.__gammaMax=", self.__gammaMax
        self.gammaUpdaterLayout = qt.QHBoxLayout(vlayout, -1, "gammaUpdaterLayout")
        self.gammaUpdaterLayout.addSpacing(5)

        '''label'''
        self.gammaLabel = qt.QLabel("Gamma:", self)
        self.gammaUpdaterLayout.addWidget(self.gammaLabel)

        '''Slider'''
        self.gammaSlider = QubSlider(self.__gammaMin,
                                    self.__gammaMax,
                                    5, self.__gamma,
                                    qt.Qt.Horizontal,self)
        self.connect(self.gammaSlider, qt.PYSIGNAL("sliderChanged"),
                     self.setGamma)
        self.gammaSlider.setMinimumWidth(100)
        self.gammaUpdaterLayout.addWidget(self.gammaSlider)

        '''Value in percentage'''
        self.gammaPCValue = qt.QLineEdit("%d"%int(self.__gamma), self)
        self.gammaUpdaterLayout.addWidget(self.gammaPCValue)
        self.gammaPCValue.setFixedWidth(30)
        self.gammaPCLabel = qt.QLabel("%", self)
        self.gammaUpdaterLayout.addWidget(self.gammaPCLabel)
        self.gammaUpdaterLayout.addSpacing(10)

        '''abs value'''
        self.gammaAbsLabel = qt.QLabel("[%s/%s]"%(self.__gamma, self.__gammaMax), self)
        self.gammaUpdaterLayout.addWidget(self.gammaAbsLabel)
        self.gammaAbsLabel.setFixedWidth(100)

        vlayout.addLayout(self.gammaUpdaterLayout)
        vlayout.addSpacing(10)

        self.disableControls()

    def disableControls(self):
        if not self.__brightnessExists:
            pass
        if not self.__contrastExists:
            self.contrastLabel.setEnabled(False)
            self.contrastSlider.setEnabled(False)
            self.contrastPCValue.setEnabled(False)
            self.contrastPCLabel.setEnabled(False)
            self.contrastAbsLabel.setEnabled(False)

        if not self.__gainExists:
            pass

        if not self.__gammaExists:
            pass


    '''
    CONTRAST
    '''
    ##@brief set the gain range
    def setContrastLimits(self, contrastMin, contrastMax):
        # not called ?
        print "----------------------Set Contrast Limits  ???????-----------------"
        self.__contrastMin = contrastMin
        self.__contrastMax = contrastMax

        self.setContrast(self.__contrast)
        self.contrastChanged(self.__contrast)

    ##@brief set the contrast
    #
    #Callback of the contrast slider
    #@param contrast must be between contrastMax and contrastMin
    #@see setContrastLimits
    def setContrast(self, contrast):
        self.__contrast = contrast
        if contrast < self.__contrastMin:
            self.__contrast = self.__contrastMin
        if contrast > self.__contrastMax:
            self.__contrast = self.__contrastMax

        if self.__contrastMax==0:
            self.__contrastPC = 0
        else:
            self.__contrastPC = int(self.__contrast*100/float(self.__contrastMax))

        if self.__camera is not None:
            self.__camera.setContrast(self.__contrast)
            self.contrastPCValue.setText(str(self.__contrastPC))
            self.contrastAbsLabel.setText("[%s/%s]"%(int(round(self.__contrast)), self.__contrastMax))

    def contrastChanged(self, contrast):
        print "--QubDialog.py--contrastChanged--", contrast
        self.__contrast = contrast

        # if self.__camera is not None:
        #     self.__contrastMin =self.__camera.device.get_attribute_config('contrast').min_value

        try:
            self.__contrastMax = float(self.__contrastMax)
        except:
            self.__contrastMax = 123

        try:
            self.__contrastMin = float(self.__contrastMin)
        except:
            self.__contrastMin = 0


        if contrast < self.__contrastMin:
            self.__contrast = self.__contrastMin
        if contrast > self.__contrastMax:
            self.__contrast = self.__contrastMax

        self.__contrastPC = int(self.__contrast*100/float(self.__contrastMax))
        self.contrastPCValue.setText(str(self.__contrastPC))

        self.contrastSlider.setValue(self.__contrast)
        self.contrastSlider.setMaxValue(float(self.__contrastMax))
        self.contrastAbsLabel.setText("[%s/%s]"%(int(round(self.__contrast)), self.__contrastMax))



    '''
    BRIGHTNESS
    '''
    ##@brief set the brightness range
    def setBrightnessLimits(self, brightnessMin, brightnessMax):
        # not called ?
        sys.exit(-1)
        print "----------------------Set Brightness Limits  ???????-----------------"
        self.__brightnessMin = brightnessMin
        self.__brightnessMax = brightnessMax



        self.setBrightness(self.__brightness)
        self.brightnessChanged(self.__brightness)

    ##@brief set the brightness
    #
    #Callback of the brightness slider
    #@param brightness must be between brightnessMax and brightnessMin
    #@see setBrightnessLimits
    def setBrightness(self, brightness):
        self.__brightness = brightness
        if brightness < self.__brightnessMin:
            self.__brightness = self.__brightnessMin
        if brightness > self.__brightnessMax:
            self.__brightness = self.__brightnessMax

        if self.__brightnessMax==0:
            self.__brightnessPC = 0
        else:
            self.__brightnessPC = int(self.__brightness*100/float(self.__brightnessMax))

        if self.__camera is not None:
            self.__camera.setBrightness(self.__brightness)
            self.brightnessPCValue.setText(str(self.__brightnessPC))
            self.brightnessAbsLabel.setText("[%s/%s]"%(int(round(self.__brightness)), self.__brightnessMax))

    def brightnessChanged(self, brightness):
        print "--QubDialog.py--brightnessChanged--", brightness
        self.__brightness = brightness

        if self.__camera is not None:
            self.__brightnessMin =self.__camera.device.get_attribute_config('brightness').min_value

        try:
            self.__brightnessMax = float(self.__brightnessMax)
        except:
            self.__brightnessMax = 123

        try:
            self.__brightnessMin = float(self.__brightnessMin)
        except:
            self.__brightnessMin = 0


        if brightness < self.__brightnessMin:
            self.__brightness = self.__brightnessMin
        if brightness > self.__brightnessMax:
            self.__brightness = self.__brightnessMax

        self.__brightnessPC = int(self.__brightness*100/float(self.__brightnessMax))

        self.brightnessPCValue.setText(str(self.__brightnessPC))

        self.brightnessSlider.setValue(self.__brightness)
        self.brightnessSlider.setMinValue(float(self.__brightnessMin))
        self.brightnessSlider.setMaxValue(float(self.__brightnessMax))
        self.brightnessAbsLabel.setText("[%s/%s]"%(int(round(self.__brightness)), self.__brightnessMax))



    '''
    GAIN
    '''
    ##@brief set the gain range
    def setGainLimits(self, gainMin, gainMax):
        # not called ?
        print "----------------------Set Gain Limits ???????-----------------"
        self.__gainMin = gainMin
        self.__gainMax = gainMax
        self.setGain(self.__gain)
        self.gainChanged(self.__gain)

    ##@brief set the gain
    #
    #Callback of the gain slider
    #@param gain must be between gainMax and gainMin
    #@see setGainLimits
    def setGain(self, gain):
        self.__gain = gain
        if gain < self.__gainMin:
            self.__gain = self.__gainMin
        if gain > self.__gainMax:
            self.__gain = self.__gainMax

        if self.__gainMax==0:
            self.__gainPC = 0
        else:
            self.__gainPC = int(self.__gain*100/float(self.__gainMax))

        if self.__camera is not None:
            self.__camera.setGain(self.__gain)
            self.gainPCValue.setText(str(self.__gainPC))
            self.gainAbsLabel.setText("[%s/%s]"%(int(round(self.__gain)), self.__gainMax))

    def gainChanged(self, gain):
        self.__gain = gain

        try:
            self.__gainMax = float(self.__gainMax)
        except:
            self.__gainMax = 123

        try:
            self.__gainMin = float(self.__gainMin)
        except:
            self.__gainMin = 1

        if gain < self.__gainMin:
            self.__gain = self.__gainMin
        if gain > self.__gainMax:
            self.__gain = self.__gainMax

        self.__gainPC = int(self.__gain*100/float(self.__gainMax))
        self.gainPCValue.setText(str(self.__gainPC))

        self.gainSlider.setValue(self.__gain)
        self.gainSlider.setMinValue(float(self.__gainMin))
        self.gainSlider.setMaxValue(float(self.__gainMax))
        self.gainAbsLabel.setText("[%s/%s]"%(int(round(self.__gain)), self.__gainMax))


    '''
    GAMMA
    '''
    ##@brief set the gamma range
    def setGammaLimits(self, gammaMin, gammaMax):
        # not called ?
        print "----------------------Set Gamma Limits ???????-----------------"
        self.__gammaMin = gammaMin
        self.__gammaMax = gammaMax

        self.setGamma(self.__gamma)
        self.gammaChanged(self.__gamma)

    ##@brief set the gamma
    #
    #Callback of the gamma slider
    #@param gamma must be between gammaMax and gammaMin
    #@see setGammaLimits
    def setGamma(self, gamma):
        self.__gamma = gamma
        if gamma < self.__gammaMin:
            self.__gamma = self.__gammaMin
        if gamma > self.__gammaMax:
            self.__gamma = self.__gammaMax

        if self.__gammaMax==0:
            self.__gammaPC = 0
        else:
            self.__gammaPC = int(self.__gamma*100/float(self.__gammaMax))

        if self.__camera is not None:
            self.__camera.setGamma(self.__gamma)
            self.gammaPCValue.setText(str(self.__gammaPC))
            self.gammaAbsLabel.setText("[%s/%s]"%(int(round(self.__gamma)), self.__gammaMax))

    def gammaChanged(self, gamma):
        print "--QubDialog.py--gammaChanged--", gamma

        self.__gamma = gamma

        if self.__camera is not None:
            self.__gammaMin =self.__camera.device.get_attribute_config('gamma').min_value

        try:
            self.__gammaMax = float(self.__gammaMax)
        except:
            self.__gammaMax = 123

        try:
            self.__gammaMin = float(self.__gammaMin)
        except:
            self.__gammaMin = 0

        if gamma < self.__gammaMin:
            self.__gamma = self.__gammaMin
        if gamma > self.__gammaMax:
            self.__gamma = self.__gammaMax

        self.__gammaPC = int(self.__gamma*100/float(self.__gammaMax))
        self.gammaPCValue.setText(str(self.__gammaPC))

        self.gammaSlider.setValue(self.__gamma)
        self.gammaSlider.setMaxValue(float(self.__gammaMax))
        self.gammaSlider.setMinValue(float(self.__gammaMin))
        self.gammaAbsLabel.setText("[%s/%s]"%(int(round(self.__gamma)), self.__gammaMax))


    '''
    CHECK ATTRIBUTES OF CAMERA.
    '''
    ##@brief Check if Attributes existance and configuration.
    def checkCameraAttributes(self):
        self.checkAttributesExistance()
        self.gatherAttributesMaxValues()


    def checkAttributesExistance(self):
        self.__brightnessExists = self.__camera.brightnessExists()
        self.__contrastExists   = self.__camera.contrastExists()
        self.__gainExists       = self.__camera.gainExists()
        self.__gammaExists      = self.__camera.gammaExists()

    ##@brief Gathers maximum values for attributes.
    #
    # Max values have to be defined in "Attribute config" panel of Jive.
    def gatherAttributesMaxValues(self):
        if self.__brightnessExists:
            (self.__brightnessMin, self.__brightnessMax) = self.__camera.getBrightnessMinMax()

        if self.__contrastExists:
            (self.__contrastMin, self.__contrastMax) = self.__camera.getContrastMinMax()

        if self.__gainExists:
            (self.__gainMin, self.__gainMax) = self.__camera.getGainMinMax()

        if self.__gammaExists:
            # self.__gammaMax = self.__camera.device.attribute_query("Gamma").max_value
            (self.__gammaMin, self.__gammaMax) = self.__camera.getGammaMinMax()


    ##@brief set the camera hardware object
    #
    #You have to call this methode at least one to set the hardware object
    #for a full init of this dialog
    def setCamera(self, camera):
        self.__camera = camera

        if self.__camera is not None:
            print "--QubDialog.py--CAMERA SET"
            self.checkCameraAttributes()

            if self.__contrastExists:
                self.contrastChanged(self.__camera.getContrast())

            if self.__brightnessExists:
                self.brightnessChanged(self.__camera.getBrightness())

            if self.__gainExists:
                self.gainChanged(self.__camera.getGain())

            if self.__gammaExists:
                self.gammaChanged(self.__camera.getGamma())

    def show(self):
        if self.__camera is not None:
            print "--QubDialog.py----show"

            if self.__brightnessExists:
                self.brightnessChanged(self.__camera.getBrightness())

            if self.__contrastExists:
                self.contrastChanged(self.__camera.getContrast())

            if self.__gainExists:
                self.gainChanged(self.__camera.getGain())

            if self.__gammaExists:
                self.gammaChanged(self.__camera.getGamma())

        qt.QDialog.show(self)



























##@brief a class to display a quick image view
#
#This class can also drive a scrollView
class QubQuickView(qt.QLabel) :
    def __init__(self,parent = None,name = "Quick view",autoclose = False,**keys) :
        flags = qt.Qt.WStyle_StaysOnTop | qt.Qt.WStyle_Customize | qt.Qt.WStyle_NoBorder | qt.Qt.WStyle_Tool | qt.Qt.WX11BypassWM
        if autoclose: flags |= qt.Qt.WDestructiveClose
        qt.QLabel.__init__(self,parent,name,flags)
        self.__width = 128
        self.__height = 128
        self.__pixmap = None
        self.__image = None
        self.__dirtyFlag = True
        self.__scrollView = None
        self.__curentRect = None
        self.__popUpMode = False
        self.__grabMouseOnFirstDraw = False
        self.setMouseTracking(True)

    ##@brief define the max size of the quick view
    def setMaximumImageSize(self,w,h) :
        self.__width,self.__height = w,h

    ##@brief set the image to display
    def setImage(self,image) :
        self.__image = image
        self.__dirtyFlag = True
        if self.isShown() :
            self.update()

    ##@brief set the scrollview to control
    def setScrollView(self,scrollView) :
        self.__scrollView = weakref.ref(scrollView)
        if scrollView:
            qt.QObject.connect(scrollView,qt.SIGNAL('contentsMoving(int,int)'),self.__update_rectangle)

    ##@brief redraw
    def paintEvent(self,paintEvent) :
        if self.__grabMouseOnFirstDraw:
            self.grabMouse()
            self.__grabMouseOnFirstDraw = False

        if self.__dirtyFlag :
            self.__dirtyFlag = False
            self.__pixmap = qt.QPixmap(self.__image.smoothScale(self.__width,self.__height,self.__image.ScaleMin))
            self.setFixedSize(self.__pixmap.size())

        paint = qt.QPainter(self)
        paintRect = paintEvent.rect()
        paint.drawPixmap(paintRect.x(),paintRect.y(),self.__pixmap,
                         paintRect.x(),paintRect.y(),paintRect.width(),paintRect.height())

        if self.__scrollView :
            scrollView = self.__scrollView()
            if scrollView:
                rect,_ = self.__getViewRect(scrollView)
                paint.setPen(qt.QPen(qt.Qt.red,1))
                paint.drawRect(rect)
                self.__curentRect = rect

    def __update_rectangle(self,x,y) :
        if self.__curentRect is not None:
            rect,_ = self.__getViewRect(self.__scrollView(),x,y)
            rect = rect.unite(self.__curentRect)
            self.update(rect)

    def __getViewRect(self,scrollView,x = None,y = None) :
        if self.__dirtyFlag :
            self.__dirtyFlag = False
            self.__pixmap = qt.QPixmap(self.__image.smoothScale(self.__width,self.__height,self.__image.ScaleMin))
            self.setFixedSize(self.__pixmap.size())

        if x is None:
            x,y = scrollView.contentsX(),scrollView.contentsY()
        width,height = scrollView.contentsWidth(),scrollView.contentsHeight()
        rect = qt.QRect(x,y,min(width,scrollView.visibleWidth()),min(height,scrollView.visibleHeight()))
        matrix = qt.QWMatrix(self.__pixmap.width() / float(width),0,
                             0,self.__pixmap.height() / float(height),0,0)
        return matrix.map(rect),matrix

    def mouseReleaseEvent(self,mouseReleaseEvent) :
        if self.__popUpMode :
            self.__popUpMode = False
            self.releaseMouse ()
            self.close()

    def mouseMoveEvent(self,mouseMoveEvent) :
        if mouseMoveEvent.state() == qt.Qt.LeftButton:
            if self.__scrollView is not None:
                scrollView = self.__scrollView()
                if scrollView :
                    rect,matrix = self.__getViewRect(scrollView)
                    x,y = mouseMoveEvent.x(),mouseMoveEvent.y()
                    rect.moveCenter(qt.QPoint(x,y))
                    if rect.x() < 0 : rect.setX(0)
                    if rect.y() < 0 : rect.setY(0)
                    if rect.x() + rect.width() > self.__pixmap.width() :
                        rect.setX(self.__pixmap.width() - rect.width())
                    if rect.y() + rect.height() > self.__pixmap.height() :
                        rect.setY(self.__pixmap.height() - rect.height())
                    rect = matrix.invert()[0].map(rect)
                    scrollView.setContentsPos(rect.x(),rect.y())

    ##@brief show like a popUp window on the parent position x,y
    def popAt(self,x = -1,y = -1) :
        qt.QLabel.show(self)
        self.__popUpMode = True
        self.__grabMouseOnFirstDraw = True
        if self.__scrollView is not None and x != -1 :
            scrollView = self.__scrollView()
            if scrollView:
                rect,matrix = self.__getViewRect(scrollView)
                center = rect.center()
                x -= center.x()
                y -= center.y()
                self.move(x,y)
##@brief widget to display several info table
#
class QubInfoTableWidget(qt.QTabWidget) :
    def __init__(self,parent = None,name = '',iconName = None) :
        qt.QTabWidget.__init__(self,parent,name)
        self.__counterInfo = QubInfoBaseTableWidget(self)
        self.addTab(self.__counterInfo,'counter')
        self.__motorInfo = QubInfoBaseTableWidget(self)
        self.addTab(self.__motorInfo,'motors')
        self.__miscInfo = QubInfoBaseTableWidget(self)
        self.addTab(self.__miscInfo,'misc.')

    def setInfo(self,info):
        try:
            counter_mne = info.pop('counter_mne').split()
            counter_pos = info.pop('counter_pos').split()
            self.__counterInfo.setInfo(dict(zip(counter_mne,counter_pos)))
            motor_mne = info.pop('motor_mne').split()
            motor_pos = info.pop('motor_pos').split()
            self.__motorInfo.setInfo(dict(zip(motor_mne,motor_pos)))
        except KeyError:
            pass
        except AttributeError:
            pass
        self.__miscInfo.setInfo(info)

##@brief widget to display dictionnary info in a table
#
#display info in table in two column (key,value)
class QubInfoBaseTableWidget(qttable.QTable):
    def __init__(self,parent = None,name = '',iconName = None) :
        qttable.QTable.__init__(self,0,2,parent,name)
        self.__info = None
        self.horizontalHeader().hide()
        self.setColumnStretchable(0,True)
        self.setColumnStretchable(1,True)
        self.setSelectionMode(qttable.QTable.NoSelection)
        if iconName:
            self.setIcon(loadIcon('%s.png' % iconName))

    def setInfo(self,info) :
        self.__info = info
        self.__refresh()

    def show(self) :
        qttable.QTable.show(self)
        self.__refresh()

    def __refresh(self) :
        if self.isShown() :
            self.removeRows(range(self.numRows()))
            try:
                for i,(key,val) in enumerate(self.__info.iteritems()) :
                    self.insertRows(i)
                    self.setRowReadOnly(i,True)
                    try:
                        self.setText(i,0,str(key))
                        self.setText(i,1,str(val))
                    except:
                        self.setText(i,0,unicode(key,'latin1'))
                        self.setText(i,1,unicode(val,'latin1'))
            except AttributeError: pass

##@brief dialog use to diaply table info
#
#@see QubInfoTableWidget
class QubInfoTableDialog(qt.QDialog) :
    ##@brief constructor
    #
    #@param parent parent widget
    #@param name widget name
    #@param iconName a file name without extention of a pixmap in the Qub Icon library
    def __init__(self,parent = None,name = 'Info Dialog',iconName = None) :
        qt.QDialog.__init__(self,parent,name)
        self.setCaption(name)
        if iconName:
            self.setIcon(loadIcon('%s.png' % iconName))

        self.__infoTable = QubInfoTableWidget(self,'tInfo')
        layout = qt.QHBoxLayout(self)
        layout.addWidget(self.__infoTable)

    def show(self) :
        qt.QDialog.show(self)
        self.setMinimumSize(self.sizeHint())

    def setInfo(self,info) :
        self.__infoTable.setInfo(info)


