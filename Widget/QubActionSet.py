import weakref
import qt
import qtcanvas
import sys
import math

from Qub.Tools.QubWeakref import createWeakrefMethod

from Qub.Widget.QubAction import QubAction, QubImageAction, QubToggleImageAction
from Qub.Widget.QubWidgetSet import QubColorToolButton, QubColorToolMenu

from Qub.Icons.QubIcons import loadIcon

from Qub.Objects.QubDrawingManager import QubAddDrawing
from Qub.Objects.QubDrawingManager import QubPointDrawingMgr
from Qub.Objects.QubDrawingManager import QubLineDrawingMgr
from Qub.Objects.QubDrawingManager import Qub2PointSurfaceDrawingMgr
from Qub.Objects.QubDrawingManager import QubContainerDrawingMgr


from Qub.Objects.QubDrawingCanvasTools import QubCanvasEllipse
from Qub.Objects.QubDrawingCanvasTools import QubCanvasBeam
from Qub.Objects.QubDrawingCanvasTools import QubCanvasScale
from Qub.Objects.QubDrawingCanvasTools import QubCanvasHomotheticRectangle
from Qub.Objects.QubDrawingCanvasTools import QubCanvasHLine
from Qub.Objects.QubDrawingCanvasTools import QubCanvasVLine


from Qub.Objects.QubDrawingEvent import QubFollowMouseOnClick
from Qub.Objects.QubDrawingEvent import QubMoveNPressed1Point

from Qub.Widget.QubGraph import QubGraphView,QubGraphCurve

from Qub.Widget.QubMdi import QubMdiCheckIfParentIsMdi

from Qub.Print.QubPrintPreview import getPrintPreviewDialog

###############################################################################
###############################################################################
####################                                       ####################
####################         Miscallenous Actions          ####################
####################                                       ####################
###############################################################################
###############################################################################


###############################################################################
####################           QubToolButtonAction         ####################
###############################################################################
class QubToolButtonAction(QubAction):
    """
    This action send a signal "ButtonPressed" when user hit the button
    It creates a pushbutton in the toolbar/contextmenu or statusbar
    """
    def __init__(self,**keys):
        """
        Constructor method
        label .. :  label is used as tooltip and as string in contextmenu
        name ... :  string name of the action. Will be used to get the
                    QToolButton icon file
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None).
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu.
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it.
        index .. :  Position of the selection widget of the action in its
                    group.
        
        Store in self._label the pushbutton label
        """
        QubAction.__init__(self,**keys)
        
        self._item  = None
        self._label = keys.get('label','')
        
    def addToolWidget(self, parent):
        """
        create default pushbutton (with a label) in the toolbar of the view.
        """
        if self._widget is None:
            self._widget = qt.QToolButton(parent)
            self._widget.setAutoRaise(True)
            icon = qt.QIconSet(loadIcon("%s.png"%self._name))
            self._widget.setIconSet(icon)
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.sendSignal)
            qt.QToolTip.add(self._widget, self._label)
            
        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        self._menu = menu
        icon = qt.QIconSet(loadIcon("%s.png"%self._name))
        self._item = menu.insertItem(icon, qt.QString("%s"%self._label),
                                      self.sendSignal)
        
    def addStatusWidget(self, parent):
        """
        create pushbutton in the statusbar of the view
        """
        if self._widget is None:
            self._widget = qt.QPushButton(self._label, parent, "addtoppbutton")
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.sendSignal)
            qt.QToolTip.add(self._widget, self._label)
            
        return self._widget
         
    def sendSignal(self):
        """
        User have hit toolbar/contextmenu or statusbar pushbutton
        send "ButtonPressed" signal
        """ 
        self.emit(qt.PYSIGNAL("ButtonPressed"), ())

###############################################################################
####################             QubButtonAction           ####################
###############################################################################
class QubButtonAction(QubAction):
    """
    This action send a signal "ButtonPressed" when user hit the button
    It creates a pushbutton in the toolbar/contextmenu or statusbar
    """
    def __init__(self,**keys):
        QubAction.__init__(self,**keys)
        self._item  = None
        
    def addToolWidget(self, parent):
        """
        create default pushbutton (with a label) in the toolbar of the view.
        """
        if self._widget is None:
            self._widget = qt.QPushButton(self._label, parent, "addtoppbutton")
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.sendSignal)
            qt.QToolTip.add(self._widget, self._label)
            
        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        self._menu = menu
        self._item = menu.insertItem(qt.QString(self._label),
                                      self.sendSignal)
        
    def addStatusWidget(self, parent):
        """
        create pushbutton in the statusbar of the view
        """
        if self._widget is None:
            self._widget = qt.QPushButton(self._label, parent, "addtoppbutton")
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.sendSignal)
            qt.QToolTip.add(self._widget, self._label)
            
        return self._widget
         
    def sendSignal(self):
        """
        User have hit toolbar/contextmenu or statusbar pushbutton
        send "ButtonPressed" signal
        """ 
        self.emit(qt.PYSIGNAL("ButtonPressed"), ())

  
###############################################################################
###############################################################################
####################                                       ####################
####################            Print Actions              ####################
####################                                       ####################
###############################################################################
###############################################################################

###############################################################################
####################          QubPrintPreviewAction        ####################
###############################################################################
class QubPrintPreviewAction(QubAction):
    """
    This action send the pixmap of its associated view to a PrinPreview Widget.
    It creates a pushbutton in the toolbar/contextmenu.
    It uses the "getPPP" method of the "view" to get the pixmap.
    """
    def __init__(self,**keys):
        QubAction.__init__(self,**keys)

        self._preview = None
        
        self._item = None
        
    def addToolWidget(self, parent):
        """
        create print preview pushbutton in the toolbar of the view
        """
        if self._widget is None:
            self._widget = qt.QToolButton(parent, "addtoppbutton")
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("addpreview.png")))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.addPixmapToPP)
            qt.QToolTip.add(self._widget, "add this window to print preview")
            
        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        iconSet = qt.QIconSet(loadIcon("addpreview.png"))
        self._menu = menu
        self._item = menu.insertItem(iconSet, qt.QString("Print preview"),
                                      self.addPixmapToPP)
        
    def addStatusWidget(self, parent):
        """
        create print preview pushbutton in the toolbar of the view
        """
        if self._widget is None:
            self._widget = qt.QToolButton(parent, "addtoppbutton")
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("addpreview.png")))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.addPixmapToPP)
            qt.QToolTip.add(self._widget, "add this window to print preview")

        return self._widget
         
    def addPixmapToPP(self):
        """
        if the print preview widget parameter is set, show the print preview
        widget and send it the pixmap of the associated view
        """ 
        if self._preview is not None:
            view = self._view and self._view() or None
            if view is not None:
                if hasattr(view, "getPPP"):
                    self._preview.show()
                    if hasattr(view,'canvas') and isinstance(view.canvas(),qtcanvas.QCanvas) :
                        self._preview.addCanvasVectorNPixmap(view.canvas(),view.getPPP())
                    else:
                        self._preview.addPixmap(view.getPPP())
                elif hasattr(view,"getGraph") : # QwtPlot
                    self._preview.addGraph(view.getGraph())
                    self._preview.show()

    def viewConnect(self, view):
        """
        register the view.
        This action will call the "getPPP" method of the view and send it
        to the print preview widget
        """
        self._view = weakref.ref(view)

    def previewConnect(self, preview):
        self._preview = preview

  
###############################################################################
###############################################################################
####################                                       ####################
####################      Actions form QubImageView        ####################
####################                                       ####################
###############################################################################
###############################################################################

###############################################################################
####################          QubSeparatorAction           ####################
###############################################################################
class QubSeparatorAction(QubAction):
    """
    """
    def __init__(self,name="sep",**keys):
        QubAction.__init__(self,name=name**keys)

    def addToolWidget(self, parent):
        """
        create widget for the view toolbar
        """
                
        if self._widget is None:
            self._widget = qt.QFrame(parent)
            self._widget.setFrameShape(qt.QFrame.VLine)
            self._widget.setFrameShadow(qt.QFrame.Sunken)
            #rect = self._widget.rect()
            #rect.setY(rect.y()+2)
            #self._widget.setFrameRect(rect)
        
        return self._widget

###############################################################################
#                          QubZoomRectangle                                   #
###############################################################################
class QubZoomRectangle(QubToggleImageAction) :    
    def __init__(self,name='zoomrect',**keys) :
        QubToggleImageAction.__init__(self,name=name,**keys)
        
        self.__drawingMgr = None
        
    def viewConnect(self,qubImage) :
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__drawingMgr = Qub2PointSurfaceDrawingMgr(qubImage.canvas(),
                                                       qubImage.matrix())
        zoomrect = qtcanvas.QCanvasRectangle(qubImage.canvas())
        pen = zoomrect.pen()
        pen.setStyle(qt.Qt.DashLine)
        pen.setWidth(2)
        zoomrect.setPen(pen)
        self.__drawingMgr.addDrawingObject(zoomrect)
        qubImage.addDrawingMgr(self.__drawingMgr)

        self.__drawingMgr.setColor(qubImage.foregroundColor())
        
        self.__drawingMgr.setEndDrawCallBack(self.rectangleChanged)

    def setColor(self,color) :
        """   
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        """
        self.__drawingMgr.setColor(color)

    def initSelection(self,ox,oy,width,height) :
        if self.__drawingMgr is not None :
            self.__drawingMgr.setRect(ox,oy,width,height)
            self.rectangleChanged(self.__drawingMgr)
        
    def rectangleChanged(self, drawingMgr):
        rect =  drawingMgr.rect()     
        self.emit(qt.PYSIGNAL("RectangleSelected"), 
                  (rect.x(), rect.y(), 
                   rect.width(),rect.height()))

    def _setState(self,aFlag) :
        if aFlag :
            self.__drawingMgr.show()
            """
            keep this connection to allow color changed by action
            QubForegroundColorAction
            """
            qubImage = self._qubImage()
            if qubImage:
                self.signalConnect(qubImage)
                self.__drawingMgr.setColor(qubImage.foregroundColor())
        else:
            qubImage = self._qubImage()
            if qubImage :
                self.signalDisconnect(qubImage)
            self.__drawingMgr.hide()

        self.emit(qt.PYSIGNAL("Actif"),(aFlag,))
        

###############################################################################
####################            QubLineSelection           ####################
###############################################################################
class QubLineDataSelectionAction(QubToggleImageAction):
    def __init__(self,parent = None,name='line',graphLegend='Line Selection',autoConnect=True,**keys):
        QubToggleImageAction.__init__(self,parent=parent,name=name,autoConnect=autoConnect,**keys)
        import Numeric
        self._points = None
        self._data = None
        self._line = None
        self._lineWidth = 1
        self._zoom = None
        self._idle = qt.QTimer()
        qt.QObject.connect(self._idle,qt.SIGNAL('timeout()'),self._refreshGraph)
        mdiManager,mainWindow = QubMdiCheckIfParentIsMdi(parent)
        if mdiManager:
            self._graph = QubGraphView(mdiManager,name = graphLegend)
            self._graph.setIcon(loadIcon("%s.png" % name))
            mdiManager.addNewChildOfMainWindow(mainWindow,self._graph)
        else:
            self._graph = QubGraphView(parent,name = graphLegend)

        self._curve = QubGraphCurve(self._graph,graphLegend,Numeric.arange(1))
        self._graph.setCurve(self._curve)
        self._graph.setMode('follow_curve')

                                     ####### PRINT ACTION #######
        self.__printAction = QubPrintPreviewAction(name="print",group="admin")
        self.__printAction.previewConnect(getPrintPreviewDialog())
        self._graph.addAction([self.__printAction])

    def viewConnect(self,qubImage) :
        QubToggleImageAction.viewConnect(self,qubImage)
        self._line,_ = QubAddDrawing(qubImage,QubLineDrawingMgr,qtcanvas.QCanvasLine)
        self._line.setEndDrawCallBack(self._lineSelect)
        self._initDrawing()

    def changeLineWidth(self,width) :
        self._lineWidth = width
        self._initDrawing()

    ##brief set the caption prefix of the window graph
    def setCaptionPrefix(self,captionPrefix) :
        self._graph.setCaption(captionPrefix)
        
    ##@brief set the data array
    def setData(self,data) :
        self._data = data
        self._refreshIdle()

    ##@brief set Data Zoom
    def setDataZoom(self,zoom) :
        self._zoom = zoom
        
    ##@brief set the forground color of the line
    def setColor(self, color):
        self._line.setColor(color)

    def _setState(self,aFlag) :
        if aFlag :
            self._line.startDrawing()
        else:
            self._line.stopDrawing()
            self._line.hide()
            self._points = None         # desactive refresh

    def _initDrawing(self) :
        qubImage = self._qubImage()
        if qubImage:
            self._line.setPen(qt.QPen(qubImage.foregroundColor(),self._lineWidth,qt.Qt.SolidLine))

    def _lineSelect(self,drawingMgr) :
        self._points = drawingMgr.points()
        self._refreshIdle()

    def _refreshIdle(self) :
        if not self._idle.isActive() :
            self._idle.start(0)

    def _refreshGraph(self) :
        import Numeric
        from Qub.CTools import datafuncs
        self._idle.stop()
        if self._points and self._data is not None:
            if self._zoom: xzoom,yzoom = self._zoom.zoom()
            else: xzoom,yzoom = 1,1
            
            startx,starty,endx,endy = [round(zoom * pos) / zoom for zoom,pos in zip ([xzoom,yzoom,xzoom,yzoom],self._points)]
            distx,disty = endx - startx,endy - starty
            nbLine = self._lineWidth

            #ANGLE CALC WITH SCALAR
            X,Y = (endx - startx,endy - starty)
            dist = math.sqrt(X ** 2 + Y ** 2)
            try:
                angle = math.acos(X / dist)
            except ZeroDivisionError:
                angle = 0
            if endy - starty < 0 : angle = -angle

            if abs(distx) > abs(disty) :
                if self._zoom :
                    _,yzoom = self._zoom.zoom()
                    if yzoom < 1. :
                        nbLine = (1 / yzoom) * self._lineWidth
                ys = range(int(math.ceil(starty)),int(math.floor(starty + nbLine)),1)
                if int(starty) != starty: ys.insert(0,starty)
                if int(starty + nbLine) != (starty + nbLine): ys.append(starty + nbLine)
                xs = Numeric.arange(startx,startx + int(math.ceil(math.sqrt(distx ** 2 + disty ** 2))),1)
                abscis = xs
                lines = Numeric.array([[x,y] for y in ys for x in xs])
            else:
                if self._zoom:
                    xzoom,_ = self._zoom.zoom()
                    if xzoom < 1.:
                        nbLine = (1 / xzoom) * self._lineWidth
                xs = range(int(math.ceil(startx)),int(math.floor(startx + nbLine)),1)
                if int(startx) != startx: xs.insert(0,startx)
                if int(startx + nbLine) != (startx + nbLine): xs.append(startx + nbLine)
                ys = Numeric.arange(starty,starty + int(math.ceil(math.sqrt(distx ** 2 + disty ** 2))),1)
                angle -= math.pi / 2
                abscis = ys
                lines = Numeric.array([[x,y] for x in xs for y in ys])

            rotation = Numeric.array([[math.cos(-angle),-math.sin(-angle)],
                                     [math.sin(-angle),math.cos(-angle)]])
            translation = Numeric.array([startx,starty])

            lines = lines - translation
            lines = Numeric.matrixmultiply(lines,rotation)
            lines = lines + translation

            
            inter_result = datafuncs.interpol([range(self._data.shape[0]),range(self._data.shape[1])],self._data,lines,0)
            inter_result.shape = inter_result.shape[0] / len(abscis),len(abscis)
                        
            average = Numeric.zeros(len(inter_result[0]))
            for line in inter_result:
                average = average + line
            average = average / len(inter_result)

            self._curve.setData(abscis,average)
            self._graph.replot()
            self._graph.show()
            self._graph.raiseW()

###############################################################################
#######              QubHLineDataSelectionAction                        #######
###############################################################################
##@brief Action acting on QubImage widget
#Horizontal Data selection line
class QubHLineDataSelectionAction(QubToggleImageAction):
    def __init__(self,parent=None,name='hline',graphLegend='Horizontal Line Selection',autoConnect=True,**keys):
        QubToggleImageAction.__init__(self,parent = parent,name=name,autoConnect=autoConnect,**keys)
        import Numeric
        self._line = None
        self._helpLine = None
        self._data = None
        self._lineWidth = 1
        self._columnId,self._lineId = -1,-1
        self._zoom = None
        self._captionPrefix = None
        self._idle = qt.QTimer()
        qt.QObject.connect(self._idle,qt.SIGNAL('timeout()'),self._refreshGraph)
        mdiManager,mainWindow = QubMdiCheckIfParentIsMdi(parent)
        if mdiManager:
            self._graph = QubGraphView(mdiManager,name = graphLegend)
            self._graph.setIcon(loadIcon("%s.png" % name))
            mdiManager.addNewChildOfMainWindow(mainWindow,self._graph)
        else:
            self._graph = QubGraphView(parent,name = graphLegend)
        self._curve = QubGraphCurve(self._graph,graphLegend,Numeric.arange(1))
        self._graph.setCurve(self._curve)
        self._graph.setMode('follow_curve')

                                     ####### PRINT ACTION #######
        self.__printAction = QubPrintPreviewAction(name="print",group="admin")
        self.__printAction.previewConnect(getPrintPreviewDialog())
        self._graph.addAction([self.__printAction])

    def viewConnect(self, qubImage):
        QubToggleImageAction.viewConnect(self, qubImage)
        self._line,_ = QubAddDrawing(qubImage,QubPointDrawingMgr,QubCanvasHLine)
        self._line.setEventName('HLineDataSelection')
        self._line.setExceptExclusiveListName(['HLineDataSelection_help','VLineDataSelection','VLineDataSelection_help'])
        self._line.setEndDrawCallBack(self._lineSelect)
        self._line.setDrawingEvent(QubFollowMouseOnClick)

        self._helpLine,_ = QubAddDrawing(qubImage,QubPointDrawingMgr,QubCanvasHLine)
        self._helpLine.setDrawingEvent(QubMoveNPressed1Point)
        self._helpLine.setEventName('HLineDataSelection_help')
        self._helpLine.setExceptExclusiveListName(['HLineDataSelection','VLineDataSelection','VLineDataSelection_help'])

        self._initDrawing()
            
    def changeLineWidth(self,width) :
        self._lineWidth = width
        self._initDrawing()
        
    ##brief set the caption prefix of the window graph
    def setCaptionPrefix(self,captionPrefix) :
         self._captionPrefix = captionPrefix
    ##@brief set the data array
    def setData(self,data) :
        self._data = data
        self._refreshIdle()
    ##@brief set Data Zoom
    def setDataZoom(self,zoom) :
        self._zoom = zoom
    ##@brief set the forground color of the line
    def setColor(self, color):
        self._line.setColor(color)
        self._helpLine.setColor(color)
        
    def _setState(self,aFlag):
        for line in [self._line,self._helpLine] :
            if aFlag:
                line.startDrawing()
            else:
                line.stopDrawing()
                line.hide()
                self._lineId = -1      # desactive refresh
                
    def _initDrawing(self) :
        qubImage = self._qubImage()
        if qubImage:
            self._line.setPen(qt.QPen(qubImage.foregroundColor(),self._lineWidth,qt.Qt.SolidLine))
            self._helpLine.setPen(qt.QPen(qubImage.foregroundColor(),self._lineWidth,qt.Qt.DashLine))
        
    def _lineSelect(self,drawingMgr) :
        self._columnId,self._lineId = drawingMgr.point()
        self._refreshIdle()
        
    def _refreshIdle(self) :
        if not self._idle.isActive() :
            self._idle.start(0)

    def _refreshGraph(self) :
        import Numeric
        self._idle.stop()
        if self._lineId >= 0 and self._data is not None:
            nbLine,yzoom = self._lineWidth,1
            if self._zoom :
                _,yzoom = self._zoom.zoom()
                if yzoom < 1.:
                    nbLine = (1 / yzoom) * self._lineWidth
            if int(nbLine) != nbLine:
                 startPos = round(yzoom * self._lineId) / yzoom
                 endPos = startPos + nbLine
                 try :
                     lines = [x for x in Numeric.take(self._data,range(int(startPos),int(endPos) + 1))]
                 except IndexError,err:
                     return

                 startFrac = math.ceil(startPos) - startPos
                 lines[0] = lines[0] * startFrac
                 endFrac = endPos - math.floor(endPos)
                 lines[-1] = lines[-1] * endFrac
		 caption = '%s (start,end lines : %.2f,%.2f)' % (self._captionPrefix,startPos,endPos)
            else:
                 if nbLine > 1:
                      caption = '%s (start,end lines : %d,%d)' % (self._captionPrefix,self._lineId,self._lineId + nbLine - 1)
                 else:
                      caption = '%s (line : %d)' % (self._captionPrefix,self._lineId)
                 try :
                     lines = [x for x in Numeric.take(self._data,range(self._lineId,self._lineId + nbLine))]
                 except IndexError,err:
                     return
                 
            yVales = Numeric.zeros(len(lines[0]))
            for line in lines :
                 yVales = yVales + line
            yVales = yVales / nbLine
            self._curve.setData(Numeric.arange(len(yVales)),yVales)
            self._graph.replot()
            self._graph.show()
            self._graph.raiseW()
            self._graph.setCaption(caption)

###############################################################################
#######              QubVLineDataSelectionAction                        #######
###############################################################################
class QubVLineDataSelectionAction(QubHLineDataSelectionAction):
     def __init__(self,parent=None,name='vline',graphLegend='Vertical Line Selection',autoConnect=True,**keys):
         QubHLineDataSelectionAction.__init__(self,parent = parent,name=name,graphLegend=graphLegend,autoConnect=autoConnect,**keys)

     def viewConnect(self,qubImage) :
         QubToggleImageAction.viewConnect(self, qubImage)
         self._line,_ = QubAddDrawing(qubImage,QubPointDrawingMgr,QubCanvasVLine)
         self._line.setEventName('VLineDataSelection')
         self._line.setExceptExclusiveListName(['VLineDataSelection_help','HLineDataSelection','HLineDataSelection_help'])
         self._line.setEndDrawCallBack(self._lineSelect)
         self._line.setDrawingEvent(QubFollowMouseOnClick)
         
         self._helpLine,_ = QubAddDrawing(qubImage,QubPointDrawingMgr,QubCanvasVLine)
         self._helpLine.setDrawingEvent(QubMoveNPressed1Point)
         self._helpLine.setEventName('VLineDataSelection_help')
         self._helpLine.setExceptExclusiveListName(['VLineDataSelection','HLineDataSelection','HLineDataSelection_help'])
          
         self._initDrawing()

     def _refreshGraph(self) :
         import Numeric
         self._idle.stop()
         if self._columnId >= 0 and self._data is not None:
             nbCol,xzoom = self._lineWidth,1
             if self._zoom :
                 xzoom,_ = self._zoom.zoom()
                 if xzoom < 1.:
                     nbCol = (1 / xzoom) * self._lineWidth
             if int(nbCol) != nbCol:
                 startPos = round(xzoom * self._columnId) / xzoom
                 endPos = startPos + nbCol
                 try:
                     columns = [x for x in Numeric.transpose(Numeric.take(self._data,range(int(startPos),int(endPos) + 1),axis = 1))]
                 except IndexError,err:
                     return
                 startFrac = math.ceil(startPos) - startPos
                 columns[0] = columns[0] * startFrac
                 endFrac = endPos - math.floor(endPos)
                 columns[-1] = columns[-1] * endFrac
                 caption = '%s (start,end columns : %.2f,%.2f)' % (self._captionPrefix,startPos,endPos)
             else:
                 if nbCol > 1:
                     caption = '%s (start,end columns : %d,%d)' % (self._captionPrefix,self._columnId,self._columnId + nbCol - 1)
                 else:
                     caption = '%s (column : %d)' % (self._captionPrefix,self._columnId)
                 try:
                     columns = [x for x in Numeric.transpose(Numeric.take(self._data,range(self._columnId,self._columnId + nbCol),axis = 1))]
                 except IndexError,err:
                     return
             xVales = Numeric.zeros(len(columns[0]))
             for column in columns :
                 xVales = xVales + column
             xVales = xVales / nbCol
             self._curve.setData(Numeric.arange(len(xVales)),xVales)
             self._graph.replot()
             self._graph.show()
             self._graph.raiseW()
             self._graph.setCaption(caption)

###############################################################################
#####################          QubCircleSelection        ######################
###############################################################################
class QubCircleSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select a circle and send its (center, radius) parameters using
    PYSIGNAL("CircleSelected")
    """
    def __init__(self,name='circle',**keys):
        QubToggleImageAction.__init__(self,name=name,**keys)

        self.__rectCoord = qt.QRect(0, 0, 1, 1)
        self.__x0 = 0
        self.__y0 = 0
        self.__radius = 0
    
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__circle = QubCanvasEllipse( self.__rectCoord.width(),
                                         self.__rectCoord.height(),
                                         self._qubImage.canvas()
                                         )
        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """   
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        """
        self.__circle.setPen(qt.QPen(color))
        self.__circle.update()

    def _setState(self, bool):
        """
        Draw or Hide circle canvas item
        """
        self.__state = bool
        if self.__circle is not None:
            if self.__state:
                self.signalConnect(self._qubImage)
                self.setColor(self._qubImage.foregroundColor())
                self.__circle.show()
            else:
                self.signalDisconnect(self._qubImage)
                self.__circle.hide()
            
            self.__circle.update()

    def mousePress(self, event):
        """
        Update upper-left corner position of the rectangle and sets its
        width and height to 1
        """ 
        (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), event.y())
        self.__x0 = x
        self.__y0 = y
        self.__rectCoord.setRect(x, y, 1, 1)
        self.viewportUpdate()
    
    def mouseMove(self, event):
        """
        Upper-left corner of the rectangle has been fixed when mouse press,
        Updates now the width and height to follow the mouse position
        """
        if event.state() == qt.Qt.LeftButton:
            (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), 
                                                           event.y())
            
            dx = x - self.__x0
            dy = y - self.__y0
            radius = math.sqrt( pow(dx,2) + pow(dy,2) )
            w = radius * 2.0
            h = radius * 2.0
            xc = self.__x0 - radius
            yc = self.__y0 - radius
            self.__rectCoord.setRect(xc, yc, w, h)
            self.__radius = radius
            self.viewportUpdate()
            
    def mouseRelease(self, event):
        """
        Rectangle selection is finished, send corresponding signal
        with coordinates (center and radius)
        """
        self.emit(qt.PYSIGNAL("CircleSelected"), 
                  (self.__x0, self.__y0, self.__radius))
        
        self.viewportUpdate()
        
    def viewportUpdate(self):
        """
        Draw Circle either if qubImage pixmap has been updated or
        rectangle coordinates have been changed by the user
        """
        rect = self._qubImage.matrix().map(self.__rectCoord)
        (x,y) = self._qubImage.matrix().map(self.__x0, self.__y0)

        self.__circle.setSize(rect.width(), rect.height())
        self.__circle.move(x, y)
        
        self.__circle.update()            






###############################################################################
#####################          QubDiscSelection        ######################
###############################################################################
class QubDiscSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select a disc and send its (center, radius) parameters using
    PYSIGNAL("DiscSelected")
    """
    def __init__(self,name='disc',**keys):
        QubToggleImageAction.__init__(self,name=name,**keys)

        self.__rectCoord = qt.QRect(0, 0, 1, 1)
        self.__x0 = 0
        self.__y0 = 0
        self.__radius = 0
    
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__disc = qtcanvas.QCanvasEllipse( self.__rectCoord.width(),
                                         self.__rectCoord.height(),
                                         self._qubImage.canvas()
                                         )
        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """   
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        """
        self.__disc.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__disc.setPen(qt.QPen(color))
        self.__disc.update()

    def _setState(self, bool):
        """
        Draw or Hide disc canvas item
        """
        self.__state = bool
        if self.__disc is not None:
            if self.__state:
                self.signalConnect(self._qubImage)
                self.setColor(self._qubImage.foregroundColor())
                self.__disc.show()
            else:
                self.signalDisconnect(self._qubImage)
                self.__disc.hide()
            
            self.__disc.update()

    def mousePress(self, event):
        """
        Update upper-left corner position of the rectangle and sets its
        width and height to 1
        """
        print "mousePress %d,%d" % (event.x(), event.y())
        (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), event.y())
        self.__x0 = x
        self.__y0 = y
        self.__rectCoord.setRect(x, y, 1, 1)
        self.viewportUpdate()
    
    def mouseMove(self, event):
        """
        Upper-left corner of the rectangle has been fixed when mouse press,
        Updates now the width and height to follow the mouse position
        """
        if event.state() == qt.Qt.LeftButton:
            (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), 
                                                           event.y())
            
            dx = x - self.__x0
            dy = y - self.__y0
            radius = math.sqrt( pow(dx,2) + pow(dy,2) )
            w = radius * 2.0
            h = radius * 2.0
            xc = self.__x0 - radius
            yc = self.__y0 - radius
            self.__radius = radius
            self.__rectCoord.setRect(xc, yc, w, h)
            self.viewportUpdate()
            
    def mouseRelease(self, event):
        """
        Rectangle selection is finished, send corresponding signal
        with coordinates
        """
        self.emit(qt.PYSIGNAL("DiscSelected"), 
                  (self.__x0, self.__y0, self.__radius))
        
        self.viewportUpdate()
        
    def viewportUpdate(self):
        """
        Draw Disc either if qubImage pixmap has been updated or
        rectangle coordinates have been changed by the user
        """
        rect = self._qubImage.matrix().map(self.__rectCoord)
        (x,y) = self._qubImage.matrix().map(self.__x0, self.__y0)

        self.__disc.setSize(rect.width(), rect.height())
        self.__disc.move(x, y)
        
        self.__disc.update()            



###############################################################################
####################            QubZoomListAction          ####################
###############################################################################
class QubZoomListAction(QubAction):
    """
    This class add a zoom facility for QubImageView as a list of zoom factor:
    keepROI .. : keep the ROI of the zoom
    zoomValList : list of zoom , be default zoom list is [0.1, 0.25, 0.5, 0.75, 1, 2, 3, 4, 5]
    initZoom : zoom value at init
    """
    def __init__(self,zoomValList=[0.1, 0.25, 0.5, 0.75, 1, 2, 3, 4, 5],
                 initZoom=1,keepROI=False,**keys):
        """
        Constructor method
        Initialyse variables
        """
        QubAction.__init__(self,**keys)

        self._zoomValList = zoomValList
        self._initZoom = initZoom
        
        self._keepROI = keepROI

        self._zoomVal = 1

        self._item = None
        
        self._qubImage = None

        self._listPopupMenu = None

        self.__lastIdSelected = 0
        
        self._actionZoomMode = None
        
    def viewConnect(self, qubImage):
        """
        connect actio0n with the QubImage object on which it will be applied
        """
        self._qubImage = weakref.ref(qubImage)
              
    def changeZoomList(self,zoomValList,defaultzoom) :
        """
        zoomValList : list of zoom
        initZoom : zoom vlaue at init
        """
        self._zoomValList = zoomValList[:]
        self._initZoom = defaultzoom
        if self._listPopupMenu is not None :
            self._listPopupMenu,idDefaultZoom = self._createPopMenu(self._listPopupMenu.parentWidget())
            self._widget.setPopup(self._listPopupMenu)
            self._widget.setText(qt.QString('%d%%' % int(self._zoomValList[idDefaultZoom] * 100)))
            
    def setZoomOnFullImage(self,flag) :
        if self._keepROI == flag :
            self._keepROI = not flag
            qubImage = self._qubImage and self._qubImage() or None
            if qubImage is not None :
                qubImage.setZoom(self._zoomVal, self._zoomVal,self._keepROI)

    def addToolWidget(self, parent):
        """
        Creates widgets to be added in the toolbar
        """

        """
        menu to select zoom value
        """
        self._listPopupMenu,idDefaultZoom = self._createPopMenu(parent)
        """
        tool button to use selected zoom value
        """
        self._widget = qt.QToolButton(parent)
        self._widget.setAutoRaise(True)
        self._widget.setPopup(self._listPopupMenu)
        self._widget.setPopupDelay(0)
        self._widget.setText(qt.QString('%d%%' % int(self._zoomValList[idDefaultZoom] * 100)))
        
        qt.QToolTip.add(self._widget, "Zoom List")
                                     
        return self._widget
        
    def addMenuWidget(self, menu):
        self._menu = menu
        
        if self._item is None:
            qstr = qt.QString("%d%%"%(int(self._zoomVal*100)))
            self._item = menu.insertItem(qstr, self._listPopupMenu)
            menu.connectItem(self._item, self._listPopupMenu.exec_loop)

    def _createPopMenu(self,parent) :
        popMenu = qt.QPopupMenu(parent)
        idDefaultZoom = 0
        for i,zoomVal in enumerate(self._zoomValList) :
            popMenu.insertItem('%d%%' % int(zoomVal * 100), i)
            if zoomVal == self._initZoom :
                idDefaultZoom = i
                self.__lastIdSelected = idDefaultZoom
        self.connect(popMenu, qt.SIGNAL("activated(int )"),
                     self._applyZoomFromList)
        return (popMenu,idDefaultZoom)
 
    def _applyZoomFromList(self, index):
            """
            Calculate zoom value from array
            """        
            try:
                if self._actionZoomMode is not None :
                    self._actionZoomMode.setState(False)
                self._applyZoom(self._zoomValList[index])
                self.__lastIdSelected = index
            except :
                import traceback
                traceback.print_exc()
    
    def _applyZoom(self, zoomVal):
        qubImage = self._qubImage and self._qubImage() or None
        if qubImage is not None:
            """
            set wait cursor as changing zoom factor could take some times
            """
            qubImage.setCursor(qt.QCursor(qt.Qt.WaitCursor))

            """
             zoom value
            """
            self._zoomVal = zoomVal

            """
            update zoom value as percentage in toolbar and menu widget
            """   
            self.writeStrValue("%d%%"%(int(self._zoomVal*100)))    

            """
            calculate and display new pixmap not centered
            """
            qubImage.setZoom(self._zoomVal, self._zoomVal,self._keepROI)
            """
            restore cursor
            """
            qubImage.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
    
    def zoom(self) :
        try:
            return self._zoomValList[self.__lastIdSelected]
        except:
            return 1
        
    def writeStrValue(self, strVal):
            """
            update zoom value in toolbar and menu widget
            """        
            qstr = qt.QString(strVal)
            self._widget.setText(qstr)
            if self._item is not None:
                self._menu.changeItem(self._item, qstr)

    def setActionZoomMode(self,anActionZoomMode) :
        """link Action zoom list with ActionZoomMod (QubZoomAction)
        """
        self._actionZoomMode = anActionZoomMode

###############################################################################
####################              QubZoomAction            ####################
###############################################################################
class QubZoomAction(QubAction):
    """
    This class add a zoom facility for QubImageView as a list:
        + fit to screen (keep image ratio)
        + fill screen (do not keep image ratio)
    This action can be linked to a ZoomListAction object in order to
    see the exact value of the zoom. Use "setList" method with the
    ZoomListAction object as parameter to do that
    """
    def __init__(self,keepROI=False,**keys):
        """
        Constructor method
        Initialyse variables
        """
        QubAction.__init__(self,**keys)
        
        self._selIndex = 0
        self._selName  = "Fit2Screen"
        
        self._toolName = ["Fit2Screen", "FillScreen"]
        self._toolIcon = {}
        self._toolIcon["Fit2Screen"] = qt.QIconSet(loadIcon("zfit.png"))
        self._toolIcon["FillScreen"] = qt.QIconSet(loadIcon("zfill.png"))
        
        self._item = None
        self._qubImage = None
        self._sigConnected = False
        self._name = "Zoom tools"

        self._keepROI = keepROI

    def viewConnect(self, qubImage):
        """
        connect action with the QubImage object on which it will be applied
        """
        self._qubImage = weakref.ref(qubImage)
        
    def addToolWidget(self, parent):
        """
        Creates widgets to be added in the toolbar
        """

        """
        menu to select zoom tool
        """
        self._toolPopupMenu = qt.QPopupMenu(parent)
        for i in range(len(self._toolName)):
            self._toolPopupMenu.insertItem(self._toolIcon[self._toolName[i]],
                                           qt.QString(self._toolName[i]),i)
        self.connect(self._toolPopupMenu, qt.SIGNAL("activated(int )"),
                        self._selectToolFromList)
        
        """
        ToolButton to set or not selected zoom tool
        """
        self._widget = qt.QToolButton(parent, "%s"%self._name)
        self._widget.setIconSet(self._toolIcon[self._selName])
        self._widget.setAutoRaise(True)
        self._widget.setToggleButton(True)
        self._widget.setPopup(self._toolPopupMenu)
        self._widget.setPopupDelay(0)
        self.connect(self._widget, qt.SIGNAL("toggled(bool)"),self.setState)
        qt.QToolTip.add(self._widget, "%s"%self._name)

        return self._widget
        
    def addMenuWidget(self, menu):
        self._menu = menu
        
        if self._item is None:
            icon = self._toolIcon[self._selName]
            self._item = menu.insertItem(icon, qt.QString(self._selName),
                                         self._toolPopupMenu)
            menu.connectItem(self._item, self._toolPopupMenu.exec_loop)
                
    def setState(self, state):
        """
        "state" is True or False.
        Set toolbar, contextmenu or statusbar widgets of the action to
        the "state" value.
        Call the internal method _setState which manage the behavior.
        """
        if self._widget is not None:
            self._widget.setOn(state)
        
        if self._item is not None:
            self._menu.setItemChecked(self._item, state)
        
        self._setState(state)
        
    def _setState(self, state):
        """
        manage behavior of the action toolbutton according to the "state" value
        """
        self.__state = state
        qubImage = self._qubImage and self._qubImage() or None
        if qubImage is not None:
            if state:
                qubImage.setScrollbarMode(self._selName)
                
                """
                update zoom value on the ZoomListAction  object if needed
                and link update zoom value to the view resize event
                """
                if self._listAction is not None:
                                       
                    if self._selName == "Fit2Screen":
                        if self._sigConnected == False:
                            self.connect(qubImage,
                                         qt.PYSIGNAL("ViewportUpdated"),
                                         self._updateZoomValue)
                            self._sigConnected = True
                    else:
                        if self._sigConnected == True:
                            self.disconnect(qubImage,
                                            qt.PYSIGNAL("ViewportUpdated"),
                                            self._updateZoomValue)
                            self._sigConnected = False
            else:
                qubImage.setScrollbarMode("Auto")
                if self._listAction is not None :
                    zoom = self._listAction.zoom()
                    qubImage.setZoom(zoom,zoom,self._keepROI)
                    self._updateZoomValue()
                    
                if self._sigConnected == True:
                    self.disconnect(qubImage,
                                    qt.PYSIGNAL("ViewportUpdated"),
                                    self._updateZoomValue)
                    self._sigConnected = False
                

        
    def _selectToolFromList(self, index):
        """
        change zoom tool
        set it to on automatically
        """
        self._selIndex = index
        self._selName = self._toolName[index]
        
        if self._widget is not None:                
            self._widget.setIconSet(self._toolIcon[self._selName])
            if self._item is not None:
                self._menu.changeItem(self._item, self._toolIcon[self._selName],
                                      qt.QString(self._selName))
            
            self.setState(1)
        
    def setList(self, listAction):
        self._listAction = listAction
        
    def _updateZoomValue(self):
        """
        when a new zoom tool is selected or when image view is resized,
        update zoom value in the ZoomStrListAction object if necessary
        """
        qubImage = self._qubImage and self._qubImage() or None
        if qubImage and self._listAction is not None:
            (zoomx, zoomy) = qubImage.zoom().zoom()
            if zoomx == zoomy:
                strVal = "%d%%"%(int(zoomx*100))
            else:
                strVal = "???"
                    
            self._listAction.writeStrValue(strVal)
        


###############################################################################
####################        QubForegroundColorAction       ####################
###############################################################################
class QubForegroundColorAction(QubAction):
    """
    This action allow to select a color.
    When the color is selected, it call the "setForegroundColor" method of
    the "view()" to wich it is connected.
    """
    def __init__(self, view=None,**keys):
        QubAction.__init__(self,**keys)
        
        self._view = view and weakref.ref(view) or None
        
        self._colorMenu = None
        
        if view is not None:
            self.viewConnect(view)

    def viewConnect(self, view):
        """
        reference the "QubView.view()" object in order to its
        "setForegroundColor" method
        """
        self._view = weakref.ref(view)
       
    def addToolWidget(self, parent):
        """
        Creates action widget to put in "group" dockarea of the "toolbar"
        Return this widget.
        """
        if self._widget is None:
            self._widget = QubColorToolButton(parent)
            self.connect(self._widget, qt.PYSIGNAL("colorSelected"),
                         self.colorChanged)
            qt.QToolTip.add(self._widget, "change color pen for selections")
        
        return self._widget
             
    def addMenuWidget(self, menu):
        """
        This method should be reimplemented.
        Creates item in contextmenu "menu" for the action.
        """
        self._menu = menu
        if self._item is None:
            if self._colorMenu is None:
                self._colorMenu = QubColorToolMenu(menu)
                self.connect(self._colorMenu, qt.PYSIGNAL("colorSelected"),
                             self.colorChanged)
                    
            self._item = menu.insertItem(self._colorMenu.iconSet,
                                         qt.QString("Color"), self._colorMenu)
            menu.connectItem(self._item, self._colorMenu.exec_loop)

    def colorChanged(self, color):
        view = self._view and self._view() or None
        if view is not None:
            view.setForegroundColor(color)
        
        if self._item is not None:
            self._menu.changeItem(self._item, self._colorMenu.iconSet,
                                  qt.QString("Color"))
                                  
    def setColor(self, color="Black"):
        try:
            qcolor = qt.QColor(color)
        except:
            print "Color %s does not exist"%color
        else:
            if self._widget is not None:
                self._widget.setColor(qcolor)
            
            if self._item is not None:
                self._colorMenu.setColor(qcolor)

            view = self._view and self._view() or None
            if view is not None:
                view.setForegroundColor(qcolor)
                                                  
####################################################################
##########                                                ##########
##########                 QubPositionAction               ##########
##########                                                ##########
####################################################################
class QubPositionAction(QubImageAction):
    def __init__(self,autoConnect=True,**keys):
        QubImageAction.__init__(self,autoConnect=autoConnect,**keys)
        
    def addStatusWidget(self, parent):
        if self._widget is None:
            self._widget = qt.QWidget(parent)
            
            hlayout = qt.QHBoxLayout(self._widget)

            xlabel = qt.QLabel("X:", self._widget)
            hlayout.addWidget(xlabel)
            
            self._xLabel = qt.QLabel("x", self._widget)
            font = self._xLabel.font()
            font.setBold(True)
            self._xLabel.setFont(font)
            minsize = self._xLabel.sizeHint()
            self._xLabel.setMinimumSize(minsize)
            hlayout.addWidget(self._xLabel)
            
            hlayout.addSpacing(5)
                   
            ylabel = qt.QLabel("Y:", self._widget)
            hlayout.addWidget(ylabel)
            
            self._yLabel = qt.QLabel("x", self._widget)
            self._yLabel.setFont(font)
            self._yLabel.setMinimumSize(minsize)
            hlayout.addWidget(self._yLabel)
                        
        return self._widget

    def viewConnect(self, view):
        QubImageAction.viewConnect(self,view)
        from Qub.Objects.QubDrawingEvent import QubDrawingEvent
        class _MouseFollow(QubDrawingEvent) :
            def __init__(self,cnt) :
                QubDrawingEvent.__init__(self,False)
                self.__cnt = cnt
            def mouseMove(self,x,y) :
                self.__cnt.mouseFollow(x,y)
        self.__event = _MouseFollow(self)
        view.addDrawingEvent(self.__event)
        
    def mouseFollow(self,x,y) :
        qubImage = self._qubImage and self._qubImage() or None
        if qubImage: (x, y) = qubImage.matrix().invert()[0].map(x,y)
    
        self._xLabel.setText(str(x))
        self._yLabel.setText(str(y))
        
####################################################################
##########                                                ##########
##########            QubDataPositionValueAction          ##########
##########                                                ##########
####################################################################
class QubDataPositionValueAction(QubPositionAction):
    def __init__(self,autoConnect=True,**keys) :
        QubPositionAction.__init__(self,autoConnect=autoConnect,**keys)
        self.__valueLabel = None
        self.__data = None
        
    def setData(self,data) :
        self.__data = data
        
    def addStatusWidget(self,parent) :
        QubPositionAction.addStatusWidget(self,parent)
        valueLabel = qt.QLabel("\tZ:",self._widget)
        layout = self._widget.layout()
        layout.addWidget(valueLabel)
        self.__valueLabel = qt.QLabel("x",self._widget)
        font = self.__valueLabel.font()
        font.setBold(True)
        self.__valueLabel.setFont(font)
        layout.addWidget(self.__valueLabel)
        return self._widget

    def mouseFollow(self,x,y) :
        QubPositionAction.mouseFollow(self,x,y)
        qubImage = self._qubImage and self._qubImage() or None
        if not qubImage: return
        matrix = qubImage.matrix()
        xScale,yScale = matrix.m11(),matrix.m22()
        if xScale < 1.0 or yScale < 1.0 : color = qt.Qt.red
        else: color = qt.Qt.black

        if xScale > 1. :
            x,_ = matrix.invert()[0].map(x,y)
        if yScale > 1. :
            _,y = matrix.invert()[0].map(x,y)
 
        try:
            value = self.__data[y][x]
            if isinstance(value,int) :
                self.__valueLabel.setText("%s" % str(value))
            else:
                self.__valueLabel.setText("%.2f" % value)
        except IndexError,err:
            self.__valueLabel.setText("x")
        except TypeError,err:
            self.__valueLabel.setText("")
        self.__valueLabel.setPaletteForegroundColor(color)
####################################################################
##########                                                ##########
##########                  QubSubDataView                ##########
##########                                                ##########
####################################################################
class QubSubDataViewAction(QubToggleImageAction) :
    class _ToolButton(qt.QToolButton) :
        def __init__(self,parent = None,name = '',cnt = None) :
            qt.QToolButton.__init__(self,parent,name)
            self.__cnt = weakref.ref(cnt)
            self.setMouseTracking(True)
        def mouseMoveEvent(self,event) :
            qt.QToolButton.mouseMoveEvent(self,event)
            cnt = self.__cnt()
            if cnt:  cnt.setCoordOnWidget(event.x(),event.y())
        def enterEvent(self,event) :
            qt.QToolButton.enterEvent(self,event)
            cnt = self.__cnt()
            if cnt: cnt.showToolTip(True)
            
        def leaveEvent(self,event) :
            qt.QToolButton.leaveEvent(self,event)
            cnt = self.__cnt()
            if cnt: cnt.showToolTip(False)
 
    def __init__(self,name = 'point',autoConnect = True,**keys) :
        QubToggleImageAction.__init__(self,name=name,autoConnect=autoConnect,**keys)
        self.__data = None
        self.__colormap = None
        self.__dataCrop = None
        self.__xOn,self.__yOn = -1,-1
        self.__x,self.__y = -1,-1
        self.__stateFlag = False
        self.__idle = qt.QTimer()
        qt.QObject.connect(self.__idle,qt.SIGNAL('timeout()'),self.__refreshPixmap)
        
    def viewConnect(self,qubImage) :
        import sys
        QubToggleImageAction.viewConnect(self,qubImage)
        self.__drawingMgr,_ = QubAddDrawing(qubImage,QubPointDrawingMgr,QubCanvasHomotheticRectangle)
        self.__drawingMgr.setColor(qubImage.foregroundColor())
        self.__drawingMgr.setDrawingEvent(QubFollowMouseOnClick)
        self.__drawingMgr.setExclusive(False)
        self.__drawingMgr.setEndDrawCallBack(self.__refresh)
        self.__drawingMgr.setWidthNHeight(10,10)

    def setColor(self,color) :
        self.__drawingMgr.setColor(color)

    def setData(self,data) :
        self.__data = data

    def setColormapObject(self,colormap):
        self.__colormap = colormap

    def showToolTip(self,aShowFlag) :
        if aShowFlag and self.__stateFlag : self.__toolTip.show()
        else: self.__toolTip.hide()
        
    def setCoordOnWidget(self,x,y) :
        xShift = (self._widget.width() - 20) / 2
        yShift = (self._widget.height() - 20 ) / 2
        self.__xOn,self.__yOn = x - xShift,y - yShift
        if not self.__idle.isActive() :
            self.__idle.start(0)
        
    def addStatusWidget(self, parent):
        try:
            if self._widget is None:
                self._widget = QubSubDataViewAction._ToolButton(parent, "%s"%self._name,cnt=self)
                self._widget.setIconSet(qt.QIconSet(loadIcon("%s.png"%self._name)))
                self._widget.setAutoRaise(True)
                self._widget.setToggleButton(True)
                self.connect(self._widget, qt.SIGNAL("toggled(bool)"),
                             self.setState)
                scr = qt.QApplication.desktop().screenNumber(self._widget);
                self.__toolTip = qt.QLabel(qt.QApplication.desktop().screen(scr),"tooltips",
                                           qt.Qt.WStyle_StaysOnTop | qt.Qt.WStyle_Customize | qt.Qt.WStyle_NoBorder | qt.Qt.WStyle_Tool | qt.Qt.WX11BypassWM)
 
                self.__toolTip.setPaletteBackgroundColor(qt.Qt.white)
            return self._widget
        except:
            import traceback
            traceback.print_exc()
            
    def _setState(self,aFlag) :
        self.__stateFlag = aFlag
        if aFlag :
            self.__drawingMgr.startDrawing()
        else:
            self.__drawingMgr.hide()
            self.__drawingMgr.stopDrawing()
            self._widget.setIconSet(qt.QIconSet(loadIcon("%s.png"%self._name)))
            self.__x,self.__y = -1,-1
            self.__toolTip.hide()
            self.__toolTip.setText('')
            self.__toolTip.setFixedSize(0,0)
            
    def __refresh(self,drawingMgr) :
        self.__x,self.__y = drawingMgr.point()
        if not self.__idle.isActive() :
            self.__idle.start(0)
            
    def __refreshPixmap(self) :
        self.__idle.stop()
        if self.__data and self.__colormap and self.__x >= 0 and self.__y >= 0 :
            import spslut
            import Numeric
            ymin = self.__y - 4
            if ymin < 0 : ymin = 0
            ymax = ymin + 10
            line,cols = self.__data.shape
            if ymax > line: ymax = line

            xmin = self.__x - 4
            if xmin < 0 : xmin = 0
            xmax = xmin + 10
            if xmax > cols: xmax = cols
            
            FloatArrayType = Numeric.typecodes['Float']
            if FloatArrayType.find(self.__data.typecode()) > -1 :
                valueFormatString = '%s<td>%s%.2f%s</td>'
            else:
                valueFormatString = '%s<td>%s%d%s</td>'
            self.__dataCrop = Numeric.take(Numeric.take(self.__data,range(ymin,ymax)),range(xmin,xmax),axis=1)
            (image_str, size, minmax) = spslut.transform(self.__dataCrop ,
                                                         (1,0), 
                                                         (self.__colormap.lutType(), 1.0),
                                                         "BGRX", 
                                                         self.__colormap.colorMapType(),
                                                         1, 
                                                         (0,0))
            if not image_str: return
            image = qt.QImage(image_str,size[0],size[1],32,None,0,
                              qt.QImage.IgnoreEndian)
            self._widget.setPixmap(qt.QPixmap(image.scale(20,20)))
            tooltipstring = '<table><tr><th><b>rows/col</b></th>'
            xOn,yOn = self.__xOn / 2,self.__yOn / 2
            for cols in range(xmin,xmax) :
                tooltipstring = '%s<th><b>%d</b></th>' % (tooltipstring,cols)
            tooltipstring = '%s</tr>' % tooltipstring
            for y,(line,lineId) in enumerate(zip(self.__dataCrop,range(ymin,ymax))):
                tooltipstring = '%s<tr><td><b>%d</b></td>' % (tooltipstring,lineId)
                for x,column in enumerate(line):
                    size = len('%d' % column)
                    if x == xOn and y == yOn :
                        startColor,stopColor = '<font COLOR=red>','</font>'
                    else:
                        startColor,stopColor = '',''
                    tooltipstring = valueFormatString % (tooltipstring,startColor,column,stopColor)
                tooltipstring = '%s</tr>' % tooltipstring
            tooltipstring = '%s</table>' % tooltipstring
            self.__toolTip.setText(tooltipstring)
            tootipSize = self.__toolTip.sizeHint()
            point = self._widget.mapToGlobal(qt.QPoint(self._widget.width(),0))
            scr = qt.QApplication.desktop().screenNumber(self._widget);
            screen = qt.QApplication.desktop().screen(scr)
            if point.y() + tootipSize.height() > screen.height(): point.setY(screen.height() - tootipSize.height())
            if point.x() + tootipSize.width() > screen.width() : point.setX(point.x() - tootipSize.width() - self._widget.width())
            self.__toolTip.setFixedSize(tootipSize)
            self.__toolTip.move(point)
        
####################################################################
##########                                                ##########
##########                 QubInfoAction               ##########
##########                                                ##########
####################################################################
class QubInfoAction(QubImageAction) :
    def __init__(self,autoConnect=True,**keys) :
        QubImageAction.__init__(self,autoConnect=autoConnect,**keys)
        
    def addStatusWidget(self,parent) :
        if self._widget is None :
            self._widget = qt.QLabel(parent)
        return self._widget
    
    def viewConnect(self,qubImage) :
        self._qubImage = weakref.ref(qubImage)
        if qubImage is not None :
            self.connect(qubImage,qt.PYSIGNAL("ActionInfo"),
                         self.__displayTextInfo)

    def __displayTextInfo(self,text) :
        if self._widget is not None :
            try:
                self._widget.setText(text)
            except:
                import traceback
                traceback.print_exc()
                
####################################################################
##########                                                ##########
##########                 QubBeamAction                  ##########
##########                                                ##########
####################################################################
class QubBeamAction(QubToggleImageAction):
    def __init__(self,name="beam",**keys):
        QubToggleImageAction.__init__(self,name=name, **keys)

        self.__state = False
        self.__onMove = False
        self.__drawingMgr = None
        
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__drawingMgr = QubPointDrawingMgr(qubImage.canvas(),
                                                qubImage.matrix())
        beam = QubCanvasBeam(qubImage.canvas())
        self.__drawingMgr.addDrawingObject(beam)
        qubImage.addDrawingMgr(self.__drawingMgr)

        self.__drawingMgr.setColor(qubImage.foregroundColor())
        
        self.__drawingMgr.setEndDrawCallBack(self.sendBeamMove)

    def setColor(self, color):
        """   
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        """
        self.__drawingMgr.setColor(color)
      
    def _setState(self, aFlag):
        """
        Draw or Hide the 2 ellipse canvas items
        """
        self.__state = aFlag
        qubImage = self._qubImage and self._qubImage() or None
        if qubImage is None : return
        
        if self.__drawingMgr is not None:
            if self.__state:
                self.__drawingMgr.setColor(qubImage.foregroundColor())
                self.__drawingMgr.show()
                self.signalConnect(qubImage)
            else:
                self.signalDisconnect(qubImage)
                self.__drawingMgr.hide()

    def setBeamPosition(self, y, z):
        if y is None or z is None:
            y,z = 0,0

        self.__drawingMgr.setPoint(y, z)
        
    def sendBeamMove(self, drawingMgr):
        self.emit(qt.PYSIGNAL("BeamSelected"), drawingMgr.point())
        
#####################################################################
##########                  QubScaleAction                 ##########
#####################################################################

class QubScaleAction(QubToggleImageAction) :
    HORIZONTAL,VERTICAL,BOTH = (0x1,0x2,0x3)
    def __init__(self,name = 'scale',mode = 0x3,
                 authorized_values = [1,2,5,10,20,50,100,200,500],**keys) :
        QubToggleImageAction.__init__(self,name = name,**keys)
        self.__xPixelSize = 0
        self.__yPixelSize = 0
        self.__mode = mode
        self.__autorizeValues = authorized_values

        self.__scale = None
                
    def viewConnect(self, qubImage):
        QubToggleImageAction.viewConnect(self,qubImage)
        self.__scale = QubContainerDrawingMgr(qubImage.canvas(),qubImage.matrix())
        scaleObject = QubCanvasScale(qubImage.canvas())
        self.__scale.addDrawingObject(scaleObject)
        qubImage.addDrawingMgr(self.__scale)

        self.__scale.setXPixelSize(self.__xPixelSize)
        self.__scale.setYPixelSize(self.__yPixelSize)
        self.__scale.setMode(self.__mode)
        self.__scale.setAutorizedValues(self.__autorizeValues)

        
    def setXPixelSize(self,size) :
        try:
            self.__xPixelSize = abs(size)
        except:
            self.__xPixelSize = 0
        if self.__scale is not None :
            self.__scale.setXPixelSize(self.__xPixelSize)

    def xPixelSize(self) :
        return self.__xPixelSize
    
    def setYPixelSize(self,size) :
        try:
            self.__yPixelSize = abs(size)
        except:
            self.__yPixelSize = 0
        if self.__scale is not None :
            self.__scale.setYPixelSize(self.__yPixelSize)

    def yPixelSize(self) :
        return self.__yPixelSize
                    
    def addToolWidget(self,parent) :
        widget = QubToggleImageAction.addToolWidget(self,parent)
        self.__colorToolButton = QubColorToolButton()
        widget.setPopup(self.__colorToolButton.popupMenu)
        self.__colorToolButton.setPopup(None)
        widget.setPopupDelay(0)
        self.connect(self.__colorToolButton, qt.PYSIGNAL("colorSelected"),
                     self.__colorChanged)
        return widget

    def __colorChanged(self,color) :
        self.__scale.setColor(color)
        
    def _setState(self,aFlag) :
        if self.__scale is not None :
            if aFlag:
                # HAS TO BE REMOVE
                self.__scale.show()
            else:
                self.__scale.hide()
#####################################################################
##########                  QubRulerAction                 ##########
#####################################################################
from Qub.Objects.QubDrawingCanvasTools import QubCanvasRuler

class QubRulerAction(QubToggleImageAction) :
    HORIZONTAL,VERTICAL = range(2)
    def __init__(self,iconName='gears',**keys) :
        QubToggleImageAction.__init__(self,**keys)
        self.__iconName = iconName
        self.__ruler = []
        for i in range(2) :
            ruler = QubContainerDrawingMgr(None)
            rulerObject = QubCanvasRuler(None)
            ruler.addDrawingObject(rulerObject)

            if i :
                ruler.setPositionMode(QubCanvasRuler.VERTICAL)
            else:
                ruler.setPositionMode(QubCanvasRuler.HORIZONTAL)
            self.__ruler.append(ruler)
            
    def viewConnect(self,qubImage) :
        QubToggleImageAction.viewConnect(self,qubImage)
        for ruler in self.__ruler :
            ruler.setCanvas(qubImage.canvas())
            qubImage.addDrawingMgr(ruler)
            self.connect(qubImage,qt.PYSIGNAL("ForegroundColorChanged"),
                         ruler.setColor)
            
    ##@brief create widget for the view toolbar
    def addToolWidget(self, parent):
        if self._widget is None:
            self._widget = qt.QToolButton(parent,self._name)
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("%s.png" % self.__iconName)))
            self._widget.setToggleButton(True)
            self._widget.connect(self._widget, qt.SIGNAL("toggled(bool)"),
                                 self._setState)
            qt.QToolTip.add(self._widget, "%s"%self._name)

        return self._widget
    ##@brief set the cursor label
    #@param HorV can be :
    # - QubRulerAction.HORIZONTAL for horizontal ruler
    # - QubRulerAction.VERTICAL for vertical ruler
    #
    #@param motorId can be 0 or 1 because ruler can manage at most 2 cursors
    #@param textLabel the label of the cursor
    def setLabel(self,HorV,motorId,textLabel) :
        try:
            self.__ruler[HorV].setLabel(motorId,textLabel)
        except:
            import traceback
            traceback.print_exc()
    ##@brief set limit of ruler
    #for param: @see setLabel
    def setLimits(self,HorV,motorId,lowLimit,highLimit) :
        try:
            self.__ruler[HorV].setLimits(motorId,lowLimit,highLimit)
        except:
            import traceback
            traceback.print_exc()
    ##@brief set the cursor position
    #for param: @see setLabel
    def setCursorPosition(self,HorV,motorId,position) :
        try:
            self.__ruler[HorV].setCursorPosition(motorId,position)
        except:
            import traceback
            traceback.print_exc()
        
    def _setState(self,aFlag) :
        for ruler in self.__ruler:
            if aFlag: ruler.show()
            else: ruler.hide()

    def test(self) :
        self.__ruler[QubRulerAction.HORIZONTAL].setLabel(0,'samy')
        self.__ruler[QubRulerAction.HORIZONTAL].setLabel(1,'sampy')
        self.__ruler[QubRulerAction.VERTICAL].setLabel(0,'samz')
        self.__ruler[QubRulerAction.VERTICAL].setLabel(1,'sampz')

        
        self.__ruler[QubRulerAction.HORIZONTAL].setLimits(0,-10,1000)
        self.__ruler[QubRulerAction.HORIZONTAL].setLimits(1,-50,50)
        self.__ruler[QubRulerAction.VERTICAL].setLimits(0,0,3)
        self.__ruler[QubRulerAction.VERTICAL].setLimits(1,-3,10)

        self.__ruler[QubRulerAction.HORIZONTAL].setCursorPosition(0,5)
        self.__ruler[QubRulerAction.HORIZONTAL].setCursorPosition(1,43)
        self.__ruler[QubRulerAction.VERTICAL].setCursorPosition(0,2.1)
        self.__ruler[QubRulerAction.VERTICAL].setCursorPosition(1,-1.5)
        
####################################################################
##########                                                ##########
##########                QubOpenDialogAction             ##########
##########                                                ##########
####################################################################
class QubOpenDialogAction(QubAction):
    """
    This action will allow to open a dialog 
    """
    def __init__(self,label=None,iconName='fileopen',**keys):
        QubAction.__init__(self,**keys)

        self.__dialog = None
        self.__connectCBK = None
        if label : self._label = label
        else: self._label = self._name
        self.__iconName = iconName
        
    def addToolWidget(self, parent):
        """
        create save pushbutton in the toolbar of the view
        create the save dialog if not already done
        """
        
        """
        create widget for the view toolbar
        """   
        if self._widget is None:
            self._widget = qt.QToolButton(parent,self._name)
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("%s.png" % self.__iconName)))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                            self.__showSaveDialog)
            qt.QToolTip.add(self._widget,self._label)

        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        self._menu = menu
        iconSet = qt.QIconSet(loadIcon("%s.png" % self.__iconName))
        self._item = menu.insertItem(iconSet, qt.QString(self._label),
                                      self.__showSaveDialog)
        
    def setDialog(self,dialog) :
        """ Interface to manage the dialogue window.
        this interface must have the methode :
             -> show()
             -> raiseW()
        """
        self.__dialog = dialog
        
    def setConnectCallBack(self,cbk) :
        self.__connectCBK = createWeakrefMethod(cbk)
        
    def __showSaveDialog(self):
        if self.__dialog is not None :
            self.__dialog.show()
            self.__dialog.raiseW()

    def viewConnect(self,parent) :
        if self.__connectCBK is not None:
            try:
                self.__connectCBK(self,parent)
            except :
                import traceback
                traceback.print_exc()
            
            if hasattr(self.__dialog, "refresh"):
                self.__dialog.refresh()

####################################################################
##########                                                ##########
##########            QubBrightnessContrastAction         ##########
##########                                                ##########
####################################################################
class QubBrightnessContrastAction(QubAction):
    """
    This action will allow to open a dialog 
    """
    def __init__(self,label = None,iconName = 'bright-cont',**keys):
        from Qub.Widget.QubDialog import QubBrightnessContrastDialog
        QubAction.__init__(self,**keys)

        self.__dialog = QubBrightnessContrastDialog(None)
        if label : self._label = label
        else: self._label = self._name
        self.__iconName = iconName
        
    def addToolWidget(self, parent):
        """
        create save pushbutton in the toolbar of the view
        create the save dialog if not already done
        """
        
        """
        create widget for the view toolbar
        """   
        if self._widget is None:
            self._widget = qt.QToolButton(parent,self._name)
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("%s.png" % self.__iconName)))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                            self.__showDialog)
            qt.QToolTip.add(self._widget,self._label)

        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        self._menu = menu
        iconSet = qt.QIconSet(loadIcon("%s.png" % self.__iconName))
        self._item = menu.insertItem(iconSet, qt.QString(self._label),
                                      self.__showSaveDialog)
                
    def __showDialog(self):
        if self.__dialog is not None :
            self.__dialog.show()
            self.__dialog.raiseW()

    def setCamera(self, camera):
        self.__dialog.setCamera(camera)
                
################################################################################
####################    TEST -- QubViewActionTest -- TEST   ####################
################################################################################
class QubMain(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        self.colormapSps = [spslut.GREYSCALE, spslut.REVERSEGREY, spslut.TEMP,
                            spslut.RED, spslut.GREEN, spslut.BLUE, spslut.MANY]
        #pixmap = qt.QPixmap(file)
        self.readEdfFile(file)
        self.colormap = 0
        self.colorMin = self.dataMin
        self.colorMax = self.dataMax
        self.autoscale = 0
        
        actions = []
        
        # A1
        action = QubColormapAction(show=1, group="color")
        actions.append(action)
        
        action.setParam(self.colormap, self.colorMin, self.colorMax,
                        self.dataMin, self.dataMax, self.autoscale)
        self.connect(action, qt.PYSIGNAL("ColormapChanged"),
                        self.colormapChanged)
        
        action = QubForegroundColorAction(name="Foreground", group="color")
        actions.append(action)
        
        action = QubSeparatorAction(name="sep1", show=1, group="admin")
        actions.append(action)

        action = QubPrintPreviewAction(name="PP", show=1, group="admin")
        actions.append(action)
        
        actions.append(action)

        action = QubVLineSelection(show=1, group="selection")
        actions.append(action)

        action = QubLineSelection(show=1, group="selection")
        actions.append(action)

        action = QubRectangleSelection(show=1, group="selection")
        actions.append(action)

        action = QubPointSelection(show=1, group="selection")
        actions.append(action)

        action = QubCircleSelection(show=1, group="selection")
        actions.append(action)

        action = QubSeparatorAction(name="sep2", show=1, group="selection")
        actions.append(action)

        action = QubDiscSelection(show=1, group="selection")
        actions.append(action)

        # A3
        action1 = QubZoomAction(show=1, group="zoom")
        actions.append(action1)
        
        action = QubZoomListAction(show=1, group="zoom")
        actions.append(action)
        
        action1.setList(action)
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
    
        self.qubImage = QubImageView(container, "actions", None, actions)
        
        hlayout.addWidget(self.qubImage)
        self.updatePixmap()
    
        self.setCentralWidget(container)

    def colormapChanged(self, colormap, autoscale, colorMin, colorMax):
        self.colormap  = colormap
        self.autoscale = autoscale
        self.colorMin  = colorMin
        self.colorMax  = colorMax
        self.updatePixmap()
        
    def updatePixmap(self):
        (image_str, size, minmax) = spslut.transform(self.data ,
                                               (1,0), 
                                               (spslut.LINEAR, 3.0),
                                               "BGRX", 
                                               self.colormapSps[self.colormap],
                                               self.autoscale, 
                                               (self.colorMin, self.colorMax))
        image = qt.QImage(image_str, size[0], size[1], 32, None, 0,
                          qt.QImage.IgnoreEndian)
        pixmap = qt.QPixmap()
        pixmap.convertFromImage(image)         	      
        
        if self.qubImage is not None:
            self.qubImage.setPixmap(pixmap)       
        
    def readEdfFile(self, file):    
        edf = EdfFile.EdfFile(file)
        self.data = edf.GetData(0)
        self.dataMin = min(Numeric.ravel(self.data))
        self.dataMax = max(Numeric.ravel(self.data))

                       
##  MAIN   
if  __name__ == '__main__':
    from Qub.Widget.QubImageView import QubImageView
    import EdfFile
    import Numeric
    import spslut
    
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    if len(sys.argv) < 2:
        print "Usage to test : QubActionSet.py file.edf"
        sys.exit()

    window = QubMain(None, file = sys.argv[1])
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
