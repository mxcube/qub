#!/usr/bin/env python

import qt

import copy   # ???
import Numeric
import qwt

class QubGraphError(Exception):
    """
    This class privide an exception error object for QG
    """
    def __init__(self, message):
        self.message= message
        
    def __str__(self):
        return "QubGraphError: %s"%self.message

class MarkedCurve:
    """
    This class define an object used to manage a curve defined by control
    points.
    The control points can be moved by the mouse and the curve follows the
    points.
    """
    def __init__(self, graph, name, data1, data2, diams):
        """
        """
        self.name  = name
        self.data1 = data1
        self.data2 = data2
        self.diams = diams
        self.graph = graph
        self.constraints = None
        
    def getData(self):
        """
        """
        return (self.name, self.data1, self.data2, self.diams)

    def reDraw(self):
        """
        redisplay the curve
        """
        self.graph.setCurve(self.name, self.data1, self.data2)

    def defConstraints(self, constraints):
        """
        Define constrsaints applyable to a control point in order to avoid
        some movements.
        constraints is a list of 4-uples constraints
        [(xmin, xmax, ymin, ymax),(....),]
        """
        self.constraints = constraints

    def movePoint(self, diam, x, y):
        """
        move a control point
        """
        a = self.diams.index(diam)
        if self.constraints != None:
            (xmin, xmax, ymin, ymax) = self.constraints[a]
            #print "contraintes :" , xmin, xmax, ymin, ymax
            if (x < xmin):
                x = xmin
            if (x > xmax):
                x = xmax
            if (y < ymin):
                y = ymin
            if (y > ymax):
                y = ymax
                
        self.data1[a] = x
        self.data2[a] = y

        return (diam, x, y)

    def deplace(self, point, x, y):
        """
        move the view (a marker) of a control point
        """
        diam = self.diams[point]
        self.movePoint(diam,x,y)
        self.graph._movedDiam = (diam, x, y)
        self.graph.setMarkerPos(diam, x, y)
        self.reDraw()
        

class QubGraph(qwt.QwtPlot):
    """
    QubGraph provide a canvas to draw 2d curves.
    Curves are defined by points.
    It is possible to use QubMarkedCurves (i.e. curves with control points)
    """
    MouseActions  = [None, "zoom",  "xzoom"]
    CursorMarkers = [None, "cross", "vline", "hline"]

    modeList = [None, "selectdiamond", "movediamond", "diamond",
                "zoom", "zooming"]

    def __init__(self, parent = None, name = "QubGraph", actions = None):
        """
        """
        qwt.QwtPlot.__init__(self, parent, name)
        
        self.parent  = parent
        self.actions = actions
        self.contextMenu = None
        self.actionColor = qt.QColor(qt.Qt.red)
        
        self.curveKeys  = {}
        self.activeName = None
        self.legendMenu = None
        
        self.isZooming = 0
        self.zoomStart = None
        self.zoomEnd   = None
        self.zoomState = None
        self.zoomStack = []
        
        self.zoomMarker    = None
        self.zoomMarkerKey = None
        
        self.cursorType    = None
        self.cursorVMarker = None
        self.cursorHMarker = None
        
        self.setDefaults()

        # allow to receive mouse move events even if no button pressed...
        self.canvas().setMouseTracking(1)

        # mouse signals
        self.connect(self, qt.SIGNAL("plotMouseMoved(const QMouseEvent&)"),
                     self._onMouseMoved)
        self.connect(self, qt.SIGNAL('plotMousePressed(const QMouseEvent&)'),
                     self._onMousePressed)
        self.connect(self, qt.SIGNAL('plotMouseReleased(const QMouseEvent&)'),
                     self._onMouseReleased)
        self.connect(self, qt.SIGNAL("legendClicked(long)"),
                     self._onLegend)

        # default mode
        # self.setMode("zoom")
        self.setMode("selectdiamond")
        
        # diamonds init
        self._selectedDiamond = None

        # list of (id marker , curve name) 2-uples
        self.diamondList = []
        
        self.markedCurves = {}
        

    def setModeCursor(self):
        """
        Set the cursor depending on the mode
        available cursors:
        
        Qt.ArrowCursor     Qt.UpArrowCursor      Qt.CrossCursor
        Qt.WaitCursor      Qt.SizeHorCursor      Qt.WhatsThisCursor
        Qt.SizeVerCursor   Qt.BusyCursor         Qt.SizeBDiagCursor
        Qt.SizeFDiagCursor Qt.SizeAllCursor      Qt.SplitVCursor
        Qt.SplitHCursor    Qt.PointingHandCursor Qt.ForbiddenCursor
        Qt.IbeamCursor

        """
        if self.mode == "selectdiamond":
            self.canvas().setCursor(qt.QCursor(qt.QCursor.CrossCursor))

        if self.mode == "movediamond":
            if qt.qVersion() < '3.0.0':
                self.canvas().setCursor(qt.QCursor(qt.QCursor.SizeHorCursor))
            else:
                self.canvas().setCursor(qt.QCursor(qt.QCursor.SizeAllCursor))
        
        if self.mode == "diamond":
            self.canvas().setCursor(qt.QCursor(qt.QCursor.UpArrowCursor))
        
        if self.mode == "zooming":
            self.canvas().setCursor(qt.QCursor(qt.QPixmap(
                "../Icons/IconsLibrary/zoomrect.png")))
        
        if self.mode == "zoom":
            self.canvas().setCursor(qt.QCursor(qt.QPixmap(
                "../Icons/IconsLibrary/zoomrect.png")))
        

    def setMode(self, mode):
        """
        define the working mode : selectdiamond, movediamond, diamond, zoom
        """
        if mode in self.modeList:
            self.mode = mode
            self.setModeCursor()

            if self.mode == "zoom" or  self.mode == "zooming" :
                self.enableOutline(1)
            else:
                self.enableOutline(0)
                        
        else:
            print "error invalid mode in setMode"
        


    def setContextMenu(self, menu):
        """
        """
        self.contextMenu = menu 

    def contentsContextMenuEvent(self, event):
        """
        """
        if self.contextMenu is not None:
            if event.reason() == qt.QContextMenuEvent.Mouse:
                self.contextMenu.exec_loop(qt.QCursor.pos())

    # fonction a remonter dans MdiQubGraph ?
    def getPreviewPixmap(self):
        """
        """
        return qt.QPixmap(qt.QPixmap.grabWidget(self))


    def setDefaults(self):
        """
        """
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        
        self.setCanvasBackground(qt.Qt.white)
        
        self.setTitle(" ")
        self.setXLabel("X axis")
        self.setYLabel("Y axis")
        
        self.enableXBottomAxis(1)
        self.enableXTopAxis(0)
        self.enableYLeftAxis(1)
        self.enableYRightAxis(0)
        
        self.setAxisAutoScale(qwt.QwtPlot.xBottom)
        self.setAxisAutoScale(qwt.QwtPlot.yLeft)
        
        self.setLegendFrameStyle(qt.QFrame.Box)
        self.setLegendPos(qwt.Qwt.Bottom)
        
        self.useLegend(1)
        self.useLegendMenu(1)
        
        self.activePen= qt.QPen(qt.Qt.red, 2, qt.Qt.SolidLine)
        self.actionPen= qt.QPen(qt.Qt.black, 2, qt.Qt.DotLine)
        
        self.setMouseAction("xzoom")
        #        self.setCursorMarker("vline", 1)
        
    # 
    # AXIS
    #
    def setXLabel(self, label):
        """
        """
        self.setAxisTitle(qwt.QwtPlot.xBottom, label)
        
    def getXLabel(self):
        """
        """
        return str(self.axisTitle(qwt.QwtPlot.xBottom))

    def setYLabel(self, label):
        """
        """
        self.setAxisTitle(qwt.QwtPlot.yLeft, label)
        
    def getYLabel(self):
        """
        """
        return str(self.axisTitle(qwt.QwtPlot.yLeft))

    def getTitle(self):
        """
        """
        return str(self.title())

    def mapToY1(self, name):
        """
        """
        key = self.curveKeys[name]
        self.setCurveYAxis(key, qwt.QwtPlot.yLeft)
        self.__checkYAxis()
        self.replot()

    def mapToY2(self, name):
        """
        """
        key = self.curveKeys[name]
        if not self.axisEnabled(qwt.QwtPlot.yRight):
            self.enableAxis(qwt.QwtPlot.yRight, 1)

        self.setCurveYAxis(key, qwt.QwtPlot.yRight)
        self.__checkYAxis()
        self.resetZoom()

    def __checkYAxis(self):
        """
        """
        keys = self.curveKeys.values()
        right = 0
        left = 0
        for key in self.curveKeys.values():
            if self.curveYAxis(key) == qwt.QwtPlot.yRight:
                right += 1
            else:
                left += 1

        if not left:
            for key in keys:
                self.setCurveYAxis(key, qwt.QwtPlot.yLeft)
                self.enableAxis(qwt.QwtPlot.yRight, 0)
        else:
            if not right:
                self.enableAxis(qwt.QwtPlot.yRight, 0)

    #
    # LEGEND
    #
    def useLegend(self, yesno):
        """
        """
        self.setAutoLegend(yesno)
        self.enableLegend(yesno)

    def __setLegendBold(self, name, yesno):
        """
        <LEGEND> Set legend font to bold or not
        """
        key= self.curveKeys[name]
        if self.legendEnabled(key):
            item= self.legend().findItem(key)
            font= item.font()
            font.setBold(yesno)
            item.setFont(font)

    def useLegendMenu(self, yesno):
        """
        """
        if yesno:
            self.__useLegendMenu= 1
            if self.legendMenu is None:
                self.__createLegendMenu()
            else:
                pass
        else:
            self.__useLegendMenu= 0

    def __createLegendMenu(self):
        self.legendMenu= qt.QPopupMenu()
        self.legendMenuItems= {}
        self.legendMenuItems["active"]= self.legendMenu.insertItem(
            qt.QString("Set Active"),
            self.__legendSetActive
            )
        self.legendMenu.insertSeparator()
        self.legendMenuItems["mapy1"]= self.legendMenu.insertItem(
            qt.QString("Map to y1") ,self.__legendMapToY1
            )
        self.legendMenuItems["mapy2"]= self.legendMenu.insertItem(
            qt.QString("Map to y2") ,self.__legendMapToY2
            )
        self.legendMenu.insertSeparator()
        self.legendMenuItems["remove"]= self.legendMenu.insertItem(
            qt.QString("Remove"), self.__legendRemove
            )
        
    def __checkLegendMenu(self, name):
        self.legendMenu.setItemEnabled(
            self.legendMenuItems["active"], not (name==self.activeName))
        yaxis = self.curveYAxis(self.curveKeys[name])
        self.legendMenu.setItemEnabled( \
            self.legendMenuItems["mapy1"], \
            yaxis==qwt.QwtPlot.yRight and len(self.curveKeys.keys())>1)
        self.legendMenu.setItemEnabled(
            self.legendMenuItems["mapy2"],
            yaxis==qwt.QwtPlot.yLeft)

    
    def eventFilter(self, object, event):
        """
        <LEGEND> Look for mouse event on legend item to display legend menu
        """
        if self.__useLegendMenu and \
               event.type() == qt.QEvent.MouseButtonRelease and \
               event.button() == qt.Qt.RightButton:
                   self.__legendName = str(object.text())
                   self.__checkLegendMenu(self.__legendName)
                   self.legendMenu.exec_loop(self.cursor().pos())
                   return 1
        return 0

    def __legendAddCurve(self, key):
        """
        <LEGEND> To be called on curve creation to catch
        mouse event for legend menu
        """
        if self.legendEnabled(key):
            item = self.legend().findItem(key)
            item.setFocusPolicy(qt.QWidget.ClickFocus)
            if self.__useLegendMenu:
                item.installEventFilter(self)

    def __legendSetActive(self):
        """
        <LEGEND>  menu callback
        """
        self.setActiveCurve(self.__legendName)

    def __legendMapToY1(self):
        """
        <LEGEND> menu callback
        """
        self.mapToY1(self.__legendName)

    def __legendMapToY2(self):
        """
        <LEGEND> menu callback
        """
        self.mapToY2(self.__legendName)

    def __legendRemove(self):
        """
        <LEGEND> menu callback
        """
        self.delCurve(self.__legendName)

    #
    # CURVE
    #
    def setCurve(self, name, data1, data2=None):
        """
        name = name of the curve also used in the legend
        data1 = x data if data2 is set, y data otherwise
        data2 = y data
        """
        if not self.curveKeys.has_key(name):
            curve = QubGraphCurve(self, name)
            self.curveKeys[name] = self.insertCurve(curve)
        else:
            curve = self.curve(self.curveKeys[name])
            
        if data2 is None:
            y = Numeric.array(data1)
            x = Numeric.arange(len(y)).astype(Numeric.Float)
        else:
            x = Numeric.array(data1)
            y = Numeric.array(data2)

        curve.setData(x, y)
        self.__legendAddCurve(self.curveKeys[name])
        self.setActiveCurve(name)

    def setMarkedCurve(self, name, data1, data2=None):
        """
        """
        diamTab = []
        
        if len(data1) > 100:
            print "warning it may be big..."
        
        if data2 is None:
            y = data1
            x = Numeric.arange(len(y)).astype(Numeric.Float)
        else:
            x = data1
            y = data2

        for i in range(len(x)):
            diam = self._drawDiamond(name, x[i], y[i])
            diamTab.append(diam)

        self.markedCurves[name] = MarkedCurve(self, name, x, y, diamTab) 

        self.markedCurves[name].reDraw()
        
    def delCurve(self, name):
        """
        """
        if self.curveKeys.has_key(name):

            if name == self.activeName:
                self.activeName= None

            self.removeCurve(self.curveKeys[name])
            del self.curveKeys[name]
            self.__checkYAxis()
            self.setActiveCurve(self.activeName)

    def setActiveCurve(self, name=None):
        """
        """
        if name is None:
            if len(self.curveKeys.keys()):
                name= self.curveKeys.keys()[0]

        if self.curveKeys.has_key(name):
            if self.activeName is not None:
                key= self.curveKeys[self.activeName]
                pen= self.curve(key).getSavePen()
                self.setCurvePen(key, pen)
                self.__setLegendBold(self.activeName, 0)
                
            key= self.curveKeys[name]
            curve= self.curve(key)
            curve.savePen()
            self.setCurvePen(key, self.activePen)
            self.__setLegendBold(name, 1)
            self.activeName= name
            self.replot()
            self.emit(qt.PYSIGNAL("QubGraphActive"), (self.activeName,))


    #
    # Diamonds
    #
    def _drawDiamond(self, curveName=None, x=0, y=0):
        """ add a diamond marker
        """
        self.marker = self.insertMarker()
        self.diamondList.append((self.marker, curveName))
        # print "self.marker, x, y", self.marker, x, y
        self.setMarkerPos(self.marker, x, y)
        self.setMarkerLinePen(self.marker, qt.QPen(qt.Qt.green, 2,
                                                   qt.Qt.DashDotLine))
        self.setMarkerSymbol(self.marker,
                             qwt.QwtSymbol (qwt.QwtSymbol.Diamond,
                                            qt.QBrush(qt.Qt.blue),
                                            qt.QPen(qt.Qt.red),
                                            qt.QSize(15, 15)))
        self.replot()
        
        return self.marker

    def _delDiamond(self, markerRef):
        """
        Delete the marker with ref markerRef
        """
        pass

    def _moveDiamond(self, diam, x, y):
        """
        move the marker diam to position (x, y)
        Update the related curve
        """
        # update the data of the marked curve...
        for (diamond, curve) in self.diamondList:
            if diamond == diam:
                (diam, x, y) = self.markedCurves[curve].movePoint(diam, x, y)
                self.markedCurves[curve].reDraw()
                self._movedDiam = (diam, x, y)
        # move the marker 
        self.setMarkerPos(diam, x, y)

    def _highlightDiamondOn(self, marker):
        """
        highlight a marker in green
        """
        self.setMarkerSymbol( marker,
                              qwt.QwtSymbol (qwt.QwtSymbol.Diamond,
                                         qt.QBrush(qt.Qt.green),
                                         qt.QPen(qt.Qt.green),
                                         qt.QSize(15,15))
                              )
        self.replot()

    def _highlightDiamondOff(self, marker):
        """
        redraw a marker back in red/blue
        """
        self.setMarkerSymbol( marker,
                              qwt.QwtSymbol (qwt.QwtSymbol.Diamond,
                                         qt.QBrush(qt.Qt.blue),
                                         qt.QPen(qt.Qt.red),
                                         qt.QSize(15,15))
                              )
        self.replot()

    #
    # MOUSE CALLBACKS
    #

    # mouse MOVE
    def _onMouseMoved(self, event):
        """
        """
        xpixel = event.pos().x()
        ypixel = event.pos().y()

        xdata = self.invTransform(qwt.QwtPlot.xBottom, xpixel)
        ydata = self.invTransform(qwt.QwtPlot.yLeft, ypixel)

        replot = 0
        
        if self.mode == "selectdiamond":
            pass

        if self.mode == "movediamond":
            self._moveDiamond(self._selectedDiamond, xdata, ydata)
            self.emit(qt.PYSIGNAL("PointMoved"), self._movedDiam)
            replot = 1
            
        if self.__updateCursorMarker(xdata, ydata):
            replot = 1

        if self.isZooming and self.zoomMarker is not None:
            self.__updateZoomMarker(xdata, ydata)
            replot = 1
                
        if self.mode == "zooming":
            pass
            
        # replot if needed
        if replot:
            self.replot()
            
        pos = {"data": (xdata, ydata), "pixel": (xpixel, ypixel)}
        self.emit(qt.PYSIGNAL("QubGraphPosition"), (pos,))

    # mouse PRESSED
    def _onMousePressed(self, event):
        """
        """
        if event.button() == qt.Qt.LeftButton:
            self._onMouseLeftPressed(event)
        elif event.button() == qt.Qt.RightButton:
            self._onMouseRightPressed(event)
        elif event.button() == qt.Qt.MidButton:
            self._onMouseMidPressed(event)
        
    def _onMouseLeftPressed(self, event):
        """
        """

        x = self.invTransform(qwt.QwtPlot.xBottom, event.x())
        y = self.invTransform(qwt.QwtPlot.yLeft, event.y())

        # print "mouseLeftPressed:", event.x(), event.y(),
        #         "data:", x, y, "mode:", self.mode

        if self.mode == "diamond":
            self._drawDiamond(None, x, y)

        if self.mode == "movediamond" or self.mode == "zooming":
            print " y a comme une erreur...  mode=", self.mode

        if self.mode == "selectdiamond":
            (cmarker, distance) = self.closestMarker(event.x(), event.y())
            if distance < 8:
                self.setMode("movediamond")
                self._selectedDiamond = cmarker
                self._highlightDiamondOn(self._selectedDiamond)
                
        if self.mode == "zoom":
            self._zoomPointOne = (x,y)
            self.setMode ("zooming")
            
        if self.mode == "selection":
            pass
    
    def _onMouseRightPressed(self, event):
        """
        """
        self.zoomBack()
        
    def _onMouseMidPressed(self, event):
        """
        """
        self.nextMode()

    def nextMode(self):
        """
        """
        print " old mode = " , self.mode
        oldmode = self.mode
        if oldmode == "zoom":
            self.setMode("selectdiamond")
        elif oldmode == "selectdiamond":
            self.setMode("zoom")
            
        print " new mode = " , self.mode

        
    # mouse RELEASED
    def _onMouseReleased(self, event):
        """
        """
        if event.button() == qt.Qt.LeftButton:
            self._onMouseLeftReleased(event)
        elif event.button() == qt.Qt.RightButton:
            self._onMouseRightReleased(event)

    def _onMouseLeftReleased(self, event):
        """
        """
        if self.mode == "movediamond":
            self.setMode ("selectdiamond")
            self._highlightDiamondOff(self._selectedDiamond)
            self._movingDiamond = None
            self.emit(qt.PYSIGNAL("PointReleased"), self._movedDiam)

        if self.mode == "zooming":
            (xmin, ymin) = self._zoomPointOne
            xmax = self.invTransform(qwt.QwtPlot.xBottom, event.x())
            ymax = self.invTransform(qwt.QwtPlot.yLeft, event.y())
            self.setZoom(xmin, xmax, ymin, ymax)
            self.setMode("zoom")

    def _onMouseRightReleased(self, event):
        """
        """
        pass

    #
    # legend ?
    #
    def _onLegend(self, item):
        """
        """
        curve = self.curve(item)
        name  = str(curve.title())
        self.setActiveCurve(name)

    #
    # ZOOM
    #

    # ??? unused ?
    def __startZoom(self, x, y):
        """
        """
        self.isZooming= 1
        xpos = self.invTransform(qwt.QwtPlot.xBottom, x)
        ypos = self.invTransform(qwt.QwtPlot.yLeft, y)

        if self.axisEnabled(qwt.QwtPlot.yRight):
            y2pos = self.invTransform(qwt.QwtPlot.yRight, y)
        else:
            y2pos = 0

        self.zoomStart = (xpos, ypos, y2pos)

        marker = self.zoomMarkerClass(self)
        self.zoomMarker = self.insertMarker(marker)

    # ??? unused ?
    def __stopZoom(self, x, y):
        """
        """
        self.isZooming = 0
        xpos = self.invTransform(qwt.QwtPlot.xBottom, x)
        ypos = self.invTransform(qwt.QwtPlot.yLeft, y)
        if self.axisEnabled(qwt.QwtPlot.yRight):
            y2pos = self.invTransform(qwt.QwtPlot.yRight, y)
        else:
            y2pos = 0
        self.zoomEnd = (xpos, ypos, y2pos)

        self.removeMarker(self.zoomMarker)
        self.zoomMarker = None

    def __updateZoomMarker(self, x, y):
        """
        """
        self.setMarkerPos(self.zoomMarker, x, y)

    def getZoom(self):
        """
        """
        if self.axisAutoScale(qwt.QwtPlot.xBottom):
            xmin= None
            xmax= None
        else:
            xmin= self.axisScale(qwt.QwtPlot.xBottom).lBound()
            xmax= self.axisScale(qwt.QwtPlot.xBottom).hBound()

        if self.axisAutoScale(qwt.QwtPlot.yLeft):
            ymin= None
            ymax= None
        else:
            ymin= self.axisScale(qwt.QwtPlot.yLeft).lBound()
            ymax= self.axisScale(qwt.QwtPlot.yLeft).hBound()

        if self.axisEnabled(qwt.QwtPlot.yRight):
            if self.axisAutoScale(qwt.QwtPlot.yRight):
                y2min= None
                y2max= None
            else:
                y2min= self.axisScale(qwt.QwtPlot.yRight).lBound()
                y2max= self.axisScale(qwt.QwtPlot.yRight).hBound()
        else:
            y2min= 0
            y2max= 0

        return (xmin, xmax, ymin, ymax, y2min, y2max)

    def setZoom(self, xmin, xmax, ymin, ymax, y2min=0, y2max=0):
        """
        """
        self.zoomStack.append(self.getZoom())
        self.__setZoom(xmin, xmax, ymin, ymax, y2min, y2max)

    def __setZoom(self, xmin, xmax, ymin, ymax, y2min=0, y2max=0):
        if xmin is None or xmax is None:
            self.setAxisAutoScale(qwt.QwtPlot.xBottom)
        else:
            self.setAxisScale(qwt.QwtPlot.xBottom, xmin, xmax)

        if ymin is None or ymax is None:
            self.setAxisAutoScale(qwt.QwtPlot.yLeft)
        else:
            self.setAxisScale(qwt.QwtPlot.yLeft, ymin, ymax)

        if self.axisEnabled(qwt.QwtPlot.yRight):
            if y2min is None or y2max is None:
                self.setAxisAutoScale(qwt.QwtPlot.yRight)
            else:
                self.setAxisScale(qwt.QwtPlot.yRight, y2min, y2max)
                
        self.replot()

    def setXZoom(self, xmin, xmax):
        """
        """
        self.setZoom(xmin, xmax, None, None)

    def setYZoom(self, ymin, ymax):
        """
        """
        self.setZoom(None, None, ymin, ymax)

    def zoomBack(self):
        """
        """
        if len(self.zoomStack)>1:
            zoom= self.zoomStack[-1]
            self.__setZoom(zoom[0], zoom[1], zoom[2], zoom[3], zoom[4], zoom[5])
            self.zoomStack.remove(zoom)
        else:
            self.resetZoom()

    def resetZoom(self):
        """
        """
        self.setAxisAutoScale(qwt.QwtPlot.xBottom)
        self.setAxisAutoScale(qwt.QwtPlot.yLeft)
        if self.axisEnabled(qwt.QwtPlot.yRight):
            self.setAxisAutoScale(qwt.QwtPlot.yRight)

        self.zoomStack= []
        self.replot()

    #
    # MOUSE ACTION
    #
    def setMouseAction(self, action):
        """
        """
        if action in self.MouseActions:
            self.mouseAction = self.MouseActions.index(action)
            self.isZooming = 0
            
            if self.mouseAction == 1:
                self.zoomMarkerClass = QubGraphRectMarker
            elif self.mouseAction == 2:
                self.zoomMarkerClass = QubGraphXRectMarker

    #
    # GRIDLINES
    #
    def setGridLines(self, xgrid, ygrid=None):
        """
        """
        if ygrid is None:
            ygrid = xgrid

        self.enableGridX(xgrid)
        self.enableGridY(ygrid)

    def getGridLines(self):
        """
        """
        return (self.gridXEnabled(), self.gridYEnabled())
    

    #
    # GRAPHIC CURSOR
    #
    def setCursorMarker(self, type = None, text = 0):
        """
        """
        if type not in self.CursorMarkers:
            raise QubGraphError("Invalid Cursor type <%s>"%type)

        self.cursorType = type
        self.cursorText = text

        if self.cursorVMarker is not None:
            self.removeMarker(self.cursorVMarker)

        if self.cursorHMarker is not None:
            self.removeMarker(self.cursorHMarker)

        if self.cursorType == "cross" or self.cursorType == "vline":
            self.cursorVMarker= self.insertLineMarker("", qwt.QwtPlot.xBottom)

        if self.cursorType == "cross" or self.cursorType == "hline":
            self.cursorHMarker= self.insertLineMarker("", qwt.QwtPlot.yLeft)

        self.replot()

    def __updateCursorMarker(self, xdata, ydata):
        """
        """

        if self.cursorType is None:
            return 0

        replot = 0
    
        if self.cursorVMarker is not None:
            self.setMarkerXPos(self.cursorVMarker, xdata)
            if self.cursorText:
                self.setMarkerLabelText(self.cursorVMarker, "%g"%xdata )
            replot = 1
                
        if self.cursorHMarker is not None:
            self.setMarkerYPos(self.cursorHMarker, ydata)
            if self.cursorText:
                self.setMarkerLabelText(self.cursorHMarker, "%g"%ydata )
            replot = 1
                
        return replot

class QubGraphRectMarker(qwt.QwtPlotMarker):
    """
    """
    def __init__(self, plot):
        """
        """
        qwt.QwtPlotMarker.__init__(self, plot)
        self.x0= None
        self.x1= None
        self.y0= None
        self.y1= None

    def draw(self, painter, x, y, rect):
        """
        """
        if self.x0 is None:
            self.x0= x

        self.y0= y
        self.x1= x
        self.y1= y
        painter.drawRect(self.x0, self.y0, self.x1-self.x0, self.y1-self.y0)

class QubGraphXRectMarker(qwt.QwtPlotMarker):
    """
    """
    def __init__(self, plot):
        qwt.QwtPlotMarker.__init__(self, plot)
        self.x0= None
        self.x1= None

    def draw(self, painter, x, y, rect):
        if self.x0 is None:
            self.x0= x

        self.x1= x
        painter.drawRect(self.x0, rect.top(), self.x1-self.x0, rect.height())

class QubGraphCurve(qwt.QwtPlotCurve):
    """
    """
    def __init__(self, parent, name):
        qwt.QwtPlotCurve.__init__(self, parent, name)
        self.save= None

    def savePen(self):
        self.save= qt.QPen(self.pen())

    def getSavePen(self):
        return self.save

def test():
    import sys

    app = qt.QApplication(sys.argv)
    app.connect(app, qt.SIGNAL("lastWindowClosed()"), app.quit)
    wid = QubGraph()
    
##     for i in range(2):
##         x = arrayrange(0.0, 10.0, 0.1)
##         y = sin(x+(i/10.0) * 3.14) * (i+1)
##         z = cos(x+(i/10.0) * 3.14) * (i+1)
    
##         wid.setCurve("sin%d"%i, x, y)
##         wid.setCurve("cos%d"%i, x, z)

    # sample of curve 
    # wid.setCurve("matrace", [ 0,1,2,3,4,5,6,7,8,9] ,
    #              [ 0,1,4,9,10,8,7,5,2,5])

    # sample of marked curve
    #    a = array([0.0, 1.0, 2.0, 4.0, 8.0, 10.0 ])
    #    wid.setMarkedCurve( "mysampleTrace", a )
    
    # sample of constrained marked curve
    wid.setMarkedCurve( "ConstrainedCurve", [0,2,8,10], [0,0,4,4] )

    wid.markedCurves["ConstrainedCurve"].defConstraints(
        [(0,0,0,0),(2,8,0,0),(2,8,4,4),(10,10,4,4)] )

    # move point 2 to position 5,5
    wid.markedCurves["ConstrainedCurve"].deplace( 2, 5, 4)

    # do you want a legend for your curve ?
    wid.useLegend(False)

    # define the view
    wid.setZoom(-0.5, 10.5, -0.5, 4.5)

    wid.show()

    app.setMainWidget(wid)
    app.exec_loop()


if __name__=="__main__":
    test()
