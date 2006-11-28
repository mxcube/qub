###############################################################################
###############################################################################
####################                                       ####################
####################         Miscallenous Dialog           ####################
####################                                       ####################
###############################################################################
###############################################################################
import qt
import qtcanvas
import math
import os.path
from Qub.Objects.QubPixmapDisplay import QubPixmapDisplay
from Qub.Objects.QubPixmapDisplay import QubPixmapZoomPlug
from Qub.Objects.QubDrawingManager import QubPointDrawingMgr,QubLineDrawingManager,Qub2PointSurfaceDrawingManager
from Qub.Objects.QubDrawingCanvasTools import QubCanvasTarget,QubCanvasEllipse
from Qub.Widget.QubWidgetSet import QubSlider,QubColorToolMenu
from Qub.Icons.QubIcons import loadIcon
from Qub.Objects.QubDrawingEvent import QubMoveNPressed1Point

####################################################################
##########                                                ##########
##########             QubMeasureListDialog               ##########
##########                                                ##########
####################################################################
class QubMeasureListDialog(qt.QDialog):
    class _ItemList(qt.QListViewItem) :
        def __init__(self,aListView,aDrawingMgr) :
            qt.QListViewItem.__init__(self,aListView)
            self.__drawingMgr = aDrawingMgr

        def drawingMgr(self) :
            return self.__drawingMgr
        
    def __init__(self,*args,**keys) :
        """
        *args = Dialog Param
        1 -> parent
        2 -> name
        3 -> modal
        4 -> fl
        """
        qt.QDialog.__init__(self,*args)

        self.__canvas = keys.get('canvas',None)
        self.__matrix = keys.get('matrix',None)
        self.__eventMgr = keys.get('eventMgr',None)
        
        self.__tools = [('point',QubPointDrawingMgr,QubCanvasTarget,self.__endPointDrawing),
                        ('distance',QubLineDrawingManager,qtcanvas.QCanvasLine,self.__endDistanceDrawing),
                        ('rectangle',Qub2PointSurfaceDrawingManager,qtcanvas.QCanvasRectangle,self.__endSurfaceDrawing)]
        
        self.__ToolIdSelected = 0
        self.__lastdrawingMgr = None
        self.__mesID = 0
        
        if len(args) < 2:
            self.setName("MeasureWindow")


        MeasureWindowLayout = qt.QVBoxLayout(self,11,6,"MeasureWindowLayout")

        layout2 = qt.QHBoxLayout(None,0,6,"layout2")
        spacer1 = qt.QSpacerItem(210,20,qt.QSizePolicy.Expanding,qt.QSizePolicy.Minimum)
        layout2.addItem(spacer1)

        self.__measureTool = qt.QToolButton(self,"__measureTool")
        listPopupMenu = self.__createPopMenu(self.__measureTool)
        self.__measureTool.setAutoRaise(True)
        self.__measureTool.setPopup(listPopupMenu)
        self.__measureTool.setPopupDelay(0)
        self.__toolSelect(0)
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
        
    def setXPixelSize(self,size) :
        try:
            self.__xPixelSize = abs(size)
        except:
            self.__xPixelSize = 0
                
    def setYPixelSize(self,size) :
        try:
            self.__yPixelSize = abs(size)
        except:
            self.__yPixelSize = 0
            
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
        try :
            if self.__lastdrawingMgr is not None :
                self.__lastdrawingMgr.stopDrawing()
            self.__lastdrawingMgr = self.__tools[self.__ToolIdSelected][1](self.__canvas,self.__matrix)
            
            if self.__ToolIdSelected == 0:
                self.__lastdrawingMgr.setDrawingEvent(QubMoveNPressed1Point)
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

    def __getDistanceString(self,dist) :
        for unit,unitString in [(1e-3,'m'),(1e-6,'\xb5'),(1e-9,'n'),(1e-12,'p')] :
            tmpDist = dist / unit
            if 1. < tmpDist < 1000. :
                return "%.2f %s" % (tmpDist,unitString)
        return "%.2f" % dist

    def __getSurfaceString(self,surface) :
        print 'surface',surface
        for unit,unitString in [(1e-6,'m'),(1e-12,'\xb5'),(1e-18,'n'),(1e-24,'p')] :
            tmpDist = surface / unit
            print 'tmpDist',tmpDist
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
##########               QubSaveImageDialog               ##########
##########                                                ##########
####################################################################
class QubSaveImageDialog(qt.QDialog):
    class _Image2Pixmap(QubPixmapZoomPlug) :
        def __init__(self,receiver,buttonFile) :
            QubPixmapZoomPlug.__init__(self,receiver)
            self.__inPollFlag = False
            self.__lastImage = None
            self.__buttonFile = buttonFile
            
        def setPixmap(self,pixmap,image) :
            self.__inPollFlag = False
            QubPixmapZoomPlug.setPixmap(self,pixmap,image)
            if not self.__buttonFile.isEnabled() :
                self.__buttonFile.setEnabled(True)
            self.__lastImage = image
            return True # One Shot 

        def refresh(self) :
            if self._mgr is not None and not self.__inPollFlag :
                self.__inPollFlag = True
                self._mgr.plug(self)
                self._mgr.refresh()

        def setInPoll(self) :
            self.__inPollFlag = True
            
        def getImage(self) :
            return self.__lastImage
    """
    Dialog to take a snapshot of the falcon via device server
    and to save it in different format
    "parent" is supposed to be the brick itself in order to acces its
    "pixmap" attribute
    """
    def __init__(self,parent = None,name = '') :
        qt.QDialog.__init__(self, parent, name)
        
        self.resize(350, 350)
        
        self.__parent = parent

        vlayout = qt.QVBoxLayout(self)
        vlayout.setMargin(10)
        
        self.__ImView = QubPixmapDisplay(self)
        self.__ImView.setScrollbarMode("Fit2Screen")

        vlayout.addWidget(self.__ImView)
       
        iconSet = qt.QIconSet(loadIcon("fileopen.png"))
        self.__buttonFile = qt.QPushButton(iconSet, "", self)
        self.__buttonFile.setEnabled(False)
        self.connect(self.__buttonFile, qt.SIGNAL("clicked()"), 
                        self.openFile)
        self.__imagePlug = QubSaveImageDialog._Image2Pixmap(self.__ImView,self.__buttonFile)
                        
        iconSet = qt.QIconSet(loadIcon("snapshot.png"))
        self.__snapButton = qt.QPushButton(iconSet, "", self)
        self.connect(self.__snapButton, qt.SIGNAL("clicked()"),self.__imagePlug.refresh)
           
        hlayout = qt.QHBoxLayout(vlayout)
        hlayout.addWidget(self.__snapButton)
        hlayout.addSpacing(10)
        hlayout.addWidget(self.__buttonFile)

    def openFile(self):
        filename = qt.QFileDialog.getSaveFileName( ".", "*;;*.png;;*.jpg", self, "selectFile",
                                                    "Choose a filename to save under")
        

        if filename :
            (radix, ext) = os.path.splitext(str(filename))

            image = self.__imagePlug.getImage()

            if ext.lower() == ".png" :
                image.save(filename, "PNG")
            elif ext.lower() == ".jpeg" or ext.lower() ==".jpg" :
                image.save(filename, "JPEG")
            else :
                dialog = qt.QErrorMessage(self.__parent)
                dialog.message('File format not managed')
                dialog.exec_loop()
            
    def setImage2Pixmap(self,image2pixmap) :
        self.__imagePlug.setInPoll()
        image2pixmap.plug(self.__imagePlug)

    def refresh(self) :
        self.__imagePlug.refresh()


####################################################################
##########                                                ##########
##########        QubBrightnessContrastDialog             ##########
##########                                                ##########
####################################################################        
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

    def setContrastLimits(self, contrastMin, contrastMax):
        self.__contrastMin = contrastMin
        self.__contrastMax = contrastMax
        
        self.setContrast(self.__contrast)
        self.contrastChanged(self.__contrast)
        
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

    def setBrightnessLimits(self, brightnessMin, brightnessMax):
        self.__brightnessMin = brightnessMin
        self.__brightnessMax = brightnessMax
        
        self.setBrightness(self.__brightness)
        self.BrightnessChanged(self.__brightness)

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
        
