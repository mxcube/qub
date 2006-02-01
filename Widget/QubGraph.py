#!/usr/bin/env python

import qt

import qwt
import Numeric
import operator
import math
import time
import sys

from Qub.Widget.QubCursors import zoom_xpm, hselection_xpm, smove_point_xpm

# TODO
# - enableOutline() is deprecated ...
#
# - possibility to move a line (ie: 2 egdes and a vertex)
# - (en/dis)able zoom / move
# - objectify some things
# - optimisations
# - keys actions (move markers ?)

# BUGS:
# - zoomback to previous zoom ok but pb with autoscale...
# - do not highlight unmovable points
# - Hselection is removed when zoom (bug or featuer ?)
# - diamond marker with vline merker in Hselection
# - zoom out when hselection vline marker is present

# FIXED :
# + outline for the zoom but...
# + highlight points on "onMouseOver"
# + do not highlight (onMousePress/Move) non movable points 
# + reduce point do not porevent from highlight... and unhighlight is bogus
# + change cursor to 4-arrows on "over Movable Point"

#############################################################################
##########                        QubGraph                         ##########
############################################################################# 
class QubGraph(qwt.QwtPlot):
    """
    QubGraph provides a 2d graph representation and related facilities:
     - legends
     - zoom
     - axis and scales
     - ROI selection (horizontal selection)
    It allows to display curves defined by arrays of points
    It is possible to use marked curves (ie Curves defined by control points)
    """
    
    MouseActions  = [None, "zoom", "hselection", "movepoint"]
    CursorMarkers = [None, "cross", "vline", "hline"]

    modeList = [None, "selectdiamond", "movediamond", "diamond",
                "zoom", "zooming"]
   
    def __init__(self, parent = None, name = "QubGraph"):
        """
        Constructor
        """
        qwt.QwtPlot.__init__(self, parent, name)

        ## parameters management:
        self.parent      = parent
        self.contextMenu = None

        self.can = self.canvas()
        self.oldOverMarker = None

        ## dict of {curveName ; curveKey}
        self.curveKeys = {}
        ## list of defined curves
        self.curveList = []
        
        ## mode authorisations
        self.hselectionAllowed = True
        self.zoomAllowed       = True
        self.movePointAllowed  = True
        self.moveNoneAllowed   = True

        ## inits
        self.legendMenu = None

        #? self.actionColor = qt.QColor(qt.Qt.red)

        # name of the active curve
        self.activeName = None
        
        ## state init
        self.state = None
        self._isZooming     = False
        self._isHselecting  = False
        self._isPointMoving = False

        ## Cursors
        self.cursorType    = None
        self.cursorVMarker = None
        self.cursorHMarker = None
        #define some cursors
        self.initCursors()
        
        ## Define a painter for drawing selections
        self.p = qt.QPainter(self.can)

        ## zoom
        self.zoomStart = None
        self.zoomEnd   = None
        self.zoomState = None
        self.zoomStack = []

        # ???
        self.zoomMarker    = None
        self.zoomMarkerKey = None

        
        ## hselection
        self._hsel = None
        self.p.setBrush(qt.QBrush(qt.Qt.red, qt.Qt.Dense7Pattern))
        self.p.setPen(qt.QPen(qt.Qt.black, 1, qt.Qt.DashLine))

        ## movepoint
        # distance of action
        self.markerDist  = 7
        # cursor to move points
        self._movingMarker = None
        self._movingCurve  = None
        self._movingPoint  = None

        # set defaults parameters of the QWT graph
        self.setDefaults()

        # allow to receive mouse move events even if no button pressed
        self.canvas().setMouseTracking(1)

        ## signals
        self.connect(self, qt.SIGNAL("plotMouseMoved(const QMouseEvent&)"),
                     self._onMouseMoved)
        self.connect(self, qt.SIGNAL("plotMousePressed(const QMouseEvent&)"),
                     self._onMousePressed)
        self.connect(self, qt.SIGNAL("plotMouseReleased(const QMouseEvent&)"),
                     self._onMouseReleased)
        self.connect(self, qt.SIGNAL("legendClicked(long)"),
                     self._onLegendClicked)

    def paintEvent(self, e):
        """
        redefinition of qt paintEvent to redraw selection 
        """
        qwt.QwtPlot.paintEvent(self, e)
        if self._hsel != None:
            print "--self._hsel != None"
            self._hsel.updateSelection(self)
            if qt.QApplication.eventLoop().hasPendingEvents():
                qt.QApplication.eventLoop().processEvents(
                       qt.QEventLoop.AllEvents, 1)
            self._hsel.draw()
 
    # Authorisations
    def setMarkerMoveAllowed(self, val):
        """
        allow or not to move the markers
        """
        self.markerMoveAllowed = val

    def setZoomAllowed(self, val):
        """
        allow or not to zoom
        """
        self.zoomAllowed = val

    def setHselectionAllowed(self, val):
        """
        allow or not to select a portion of the graph
        """
        self.hselectionAllowed = val

    def setModeCursor(self):
        """
        set the cursor depending on the mode
        """
        if self.mode == "zoom":
            self.can.setCursor(self.zoomCursor)

        if self.mode == "hselection":
            self.can.setCursor(self.hselectionCursor)

        if self.mode == "movepoint":
            self.can.setCursor(self.noneCursor)
            # self.can.setCursor(qt.QCursor(qt.Qt.SizeAllCursor))

        if self.mode == None:
            self.can.setCursor(self.noneCursor)

    def initCursors(self):
        """
        define some mouse cursor
        
          default qt cursors:
        qt.Qt.ArrowCursor     qt.Qt.UpArrowCursor      qt.Qt.CrossCursor
        qt.Qt.WaitCursor      qt.Qt.SizeHorCursor      qt.Qt.WhatsThisCursor
        qt.Qt.SizeVerCursor   qt.Qt.BusyCursor         qt.Qt.SizeBDiagCursor
        qt.Qt.SizeFDiagCursor qt.Qt.SizeAllCursor      qt.Qt.SplitVCursor
        qt.Qt.SplitHCursor    qt.Qt.PointingHandCursor qt.Qt.ForbiddenCursor
        qt.Qt.IbeamCursor
        
          QubGraph cursor(s) :
        self.zoomCursor
        self.hselectionCursor
        self.movePointCursor
        slef.noneCursor (default cursor) == qt.Qt.ArrowCursor
        """

        self.noneCursor       = qt.QCursor(qt.Qt.ArrowCursor)
        self.zoomCursor       = qt.QCursor(qt.QPixmap(zoom_xpm ), 5, 4)
        self.hselectionCursor = qt.QCursor(qt.QPixmap(hselection_xpm), 5, 4)
        self.movePointCursor  = qt.QCursor(qt.QPixmap(smove_point_xpm ), 11, 11)

    def setMode(self, mode):
        """
        define the mode of action : None; zoom; hselection; movepoint
        """
        if mode in self.MouseActions:
            self.mode = mode
            self.setModeCursor()
            
            if self.mode == None:
                self.enableOutline(0)
                self.setCursorMarker(None)
                
            if self.mode == "zoom":
                self.enableOutline(1)
                self.setCursorMarker(None)
                
            if self.mode == "hselection":
                self.setCursorMarker("vline")
                self.enableOutline(0)
                
            if self.mode == "movepoint":
                self.setCursorMarker(None)
                self.enableOutline(0)
                
        else:
            print "error invalid mode in setMode"

  
    def setContextMenu(self, menu):
        """
        define a context menu
        """
        self.contextMenu = menu 

    def contentsContextMenuEvent(self, event):
        """
        """
        if self.contextMenu is not None:
            if event.reason() == qt.QContextMenuEvent.Mouse:
                self.contextMenu.exec_loop(qt.QCursor.pos())

    def setDefaults(self):
        """
        -
        -
        - define some graphic symbols for markers
        """
        self.plotLayout().setMargin(0)
        self.plotLayout().setCanvasMargin(0)
        
        self.setCanvasBackground(qt.Qt.white)
        
        self.setTitle(" ")
        #self.setXLabel("X axis")
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
        
        self.setMouseAction("movepoint")
        # self.setCursorMarker("vline", 1)

        # default mode
        self.setMode("movepoint")

        # markers
        self.markerBigSize    = b = 15
        self.markerLittleSize = l = 7
        
        self.markerSymbolUnmovable  = qwt.QwtSymbol (qwt.QwtSymbol.Diamond,
                                                     qt.QBrush(qt.Qt.black),
                                                     qt.QPen(qt.Qt.black),
                                                     qt.QSize(l, l ))
        
        self.markerSymbolMovable    = qwt.QwtSymbol (qwt.QwtSymbol.Diamond,
                                                     qt.QBrush(qt.Qt.red),
                                                     qt.QPen(qt.Qt.blue),
                                                     qt.QSize(b, b))
        
        self.markerSymbolHiglighted = qwt.QwtSymbol (qwt.QwtSymbol.Diamond,
                                                     qt.QBrush(qt.Qt.green),
                                                     qt.QPen(qt.Qt.green),
                                                     qt.QSize(b, b))


    # 
    # AXIS
    #
    def setXLabel(self, label):
        """
        set the abscissas axis label
        """
        self.setAxisTitle(qwt.QwtPlot.xBottom, label)
        
    def getXLabel(self):
        """
        return the abscissas axis label
        """
        return str(self.axisTitle(qwt.QwtPlot.xBottom))

    def setYLabel(self, label):
        """
        set the ordinates axis label
        """
        self.setAxisTitle(qwt.QwtPlot.yLeft, label)
        
    def getYLabel(self):
        """
        return the ordinates axis label
        """
        return str(self.axisTitle(qwt.QwtPlot.yLeft))

    def getTitle(self):
        """
        """
        return str(self.title())

    #
    # reference axis of curves
    #
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
        keys  = self.curveKeys.values()
        right = 0
        left  = 0
        for key in self.curveKeys.values():
            if self.curveYAxis(key) == qwt.QwtPlot.yRight:
                right += 1
            else:
                left  += 1

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
        key = self.curveKeys[name]
        if self.legendEnabled(key):
            item = self.legend().findItem(key)
            font = item.font()
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
        """
        """
        self.legendMenu = qt.QPopupMenu()
        self.legendMenuItems = {}
        self.legendMenuItems["active"] = self.legendMenu.insertItem(
            qt.QString("Set Active"),
            self.__legendSetActive
            )
        self.legendMenu.insertSeparator()
        self.legendMenuItems["mapy1"] = self.legendMenu.insertItem(
            qt.QString("Map to y1") ,self.__legendMapToY1
            )
        self.legendMenuItems["mapy2"] = self.legendMenu.insertItem(
            qt.QString("Map to y2") ,self.__legendMapToY2
            )
        self.legendMenu.insertSeparator()
        self.legendMenuItems["remove"] = self.legendMenu.insertItem(
            qt.QString("Remove"), self.__legendRemove
            )
        
    def __checkLegendMenu(self, name):
        """
        """
        self.legendMenu.setItemEnabled(
            self.legendMenuItems["active"], not (name==self.activeName))
        yaxis = self.curveYAxis(self.curveKeys[name])
        self.legendMenu.setItemEnabled(      \
            self.legendMenuItems["mapy1"],   \
            yaxis == qwt.QwtPlot.yRight and len(self.curveKeys.keys()) > 1)
        self.legendMenu.setItemEnabled(
            self.legendMenuItems["mapy2"],
            yaxis == qwt.QwtPlot.yLeft)

    
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
        mouse events for legend menu
        """
        if self.legendEnabled(key):
            item = self.legend().findItem(key)
            item.setFocusPolicy(qt.QWidget.ClickFocus)
            if self.__useLegendMenu:
                item.installEventFilter(self)

    def __legendSetActive(self):
        """
        <LEGEND> menu callback
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
    # CURVES ##############################################################
    #
    def setCurve(self, curve):
        """
        Add a QubGraphCurve to the graph. 
        """
        # if a curve with the same name still exists
        if self.curveKeys.has_key(curve.name()):
            # get the key of the curve named curve.name()
            curveKey = self.curve(self.curveKeys[curve.name()])
        else:
            curveKey = self.curveKeys[curve.name()] = self.insertCurve(curve)

        self.curveList.append(curve)
        
        curve.setData(curve.X(), curve.Y())
        self.__legendAddCurve(self.curveKeys.has_key(curve.name()))
        self.setActiveCurve(self.curveKeys.has_key(curve.name()))
        
        # draw points with markers (controlled or marked)
        if curve.hasMarkedPoint():
            for i in xrange(len(curve.X())) :
                if curve.isMarked[i] :
                    symbol = self.markerSymbolUnmovable

                    if curve.isControlled[i]:
                        symbol = self.markerSymbolMovable
                        
                    curve.markerIdx[i] = self._drawPointMarker( curve.X()[i],
                                                                curve.Y()[i],
                                                                symbol)
        else:
            pass
        
    def addCurve(self, name, V1, V2=None):
        """
        Create a curve named "name" and defined by the vectors V1 and V2.
        V1 as Xs V2 as Ys. if V2 is None, V1 as Ys and naturals numer as Xs.
        """
        curve = QubGraphCurve(self, name, V1, V2)
        self.setCurve(curve)
        
    def delCurve(self, name):
        """
        destroy a curve and remove it from the graph.
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
                key = self.curveKeys[self.activeName]
                pen = self.curve(key).getSavedPen()
                self.setCurvePen(key, pen)
                self.__setLegendBold(self.activeName, 0)
                
            key = self.curveKeys[name]
            curve = self.curve(key)
            curve.savePen()
            self.setCurvePen(key, self.activePen)
            self.__setLegendBold(name, 1)
            self.activeName= name
            self.replot()
            self.emit(qt.PYSIGNAL("GraphActive"), (self.activeName,))


    def deplace(self, curve, point, x, y):
        """
        Function to call to move a point of the curve given the curveName,
        the point number and the new position.
        """

        if curve.isMovable[point]:
            # move the point (if possible) and get corrected coords
            (nx, ny) = curve._changePointCoords(point, x, y)
            
            # update the curve
            curve._update()
            
            # move the marker
            marker = curve.markerIdx[point]
            self.setMarkerPos(marker, nx, ny)
            return (nx, ny)
        else:
            print "error point unmovable"

    #
    # PointMarkers ########################################################
    #
    def _drawPointMarker( self, x, y, symbol  ):
        """
        create and place a marker to represent a point
        """
        marker = self.insertMarker()
        
        self.setMarkerPos(marker, x, y)
        
        # self.setMarkerLinePen(marker, qt.QPen(qt.Qt.green, 2,
        #  qt.Qt.DashDotLine)) ???
        
        self.setMarkerSymbol(marker, symbol)
        
        return marker
    
    
    def _delPointMarker(self, markerRef):
        """
        remove the marker markerRef from the graph and in the good curve.
        """
        pass

    def _selectPoint(self, marker):
        """
        given a marker number, this function returns the corresponding curve
        and point as a 2-uple (c, p).
        """
        
        found = False
        for curve in self.curveList:
            # point = curve.markerIdx.index(marker)
            point = Numeric.nonzero(curve.markerIdx == marker )[-1]
            
            if point != None:
                if found:
                    print " on l'a trouve' 2 fois, c louche"
                else:
                    found = True
                    # print "selected  point", point, "of curve", curve.name()
                    return (curve, point)
                

    def _movePointMarker(self, marker, x, y):
        """
        This internal function is called by QubGraph when the mouse move a
        point. A signal is emited to informe oustide of the movement.
        """

        # move the point
        (nx, ny) = self.deplace(self._movingCurve, self._movingPoint, x,y)

        # notifies the change to the outer world
        self.emit(qt.PYSIGNAL("PointMoved"),  (self._movingCurve.name(),
                                               self._movingPoint, nx, ny)
                  )

    def _highlightPointMarker(self, marker, onoff):
        """
        highlight on or off a point marker (in green)
        othserwise in red
        """
        if onoff:
            self.setMarkerSymbol( marker, self.markerSymbolHiglighted )
            self.can.setCursor(self.movePointCursor)
        else:
            self.setMarkerSymbol( marker, self.markerSymbolMovable )
            self.can.setCursor(self.noneCursor)

        self.replot()

    def _reducePointMarker(self, marker):
        """
        Reshape a point marker to a little black diam.
        """
        self.setMarkerSymbol( marker, self.markerSymbolUnmovable)
        self.replot()


    def _updateCoord(self, xdata, ydata, xpixel, ypixel):
        """
        update the coordinates displayed somewhere if needed
        """
        pass

    #
    # MOUSE CALLBACKS
    #

    # mouse PRESSED
    def _onMousePressed(self, event):
        """
        call the good function depending on the button pressed:
        mid, right or left.
        """
        if event.button() == qt.Qt.LeftButton:
            self._onMouseLeftPressed(event)
        elif event.button() == qt.Qt.RightButton:
            self._onMouseRightPressed(event)
        elif event.button() == qt.Qt.MidButton:
            self._onMouseMidPressed(event)
        else:
            print "oh oh big error _onMousePressed"

        
    def _onMouseLeftPressed(self, event):
        """
        Actions to do when the left/first button of the mouse is pressed.
        Actions depend on the current mode.
        - find a point to move
          update : - self._movingMarker
                   - self._movingCurve
                   - self._movingPoint
        - begining to define a zoom
        - begining to define a Hselection
        """
        
        xpixel = event.x()
        ypixel = event.y()
        xdata  = self.invTransform(qwt.QwtPlot.xBottom, xpixel)
        ydata  = self.invTransform(qwt.QwtPlot.yLeft,   ypixel)
        
        if self.mode == "movepoint":
            if self.curveList:
                (cmarker, distance) = self.closestMarker(xpixel, ypixel)
                (ccurve, cpoint)    = self._selectPoint(cmarker)
            
                if distance < 7 and ccurve.isControlled[cpoint]:
                    self._isPointMoving = True
                    self._movingCurve   = ccurve
                    self._movingPoint   = cpoint
                    self._movingMarker  = cmarker
                
        if self.mode == "zoom":
            if self._hsel != None:
                self._hsel = None
            self._zoomPointOne = (xdata, ydata)
            self._isZooming = True
            
        if self.mode == "hselection":
            h = self.can.frameRect().height()
            self._hsel = Hselection(self.p)
            self._hsel.beginSelection(xdata, xpixel, h)
            # self._isHselecting  = True
            
        if self.mode == None:
            pass

    def _onMouseRightPressed(self, event):
        """
        """
        self.zoomBack()
        
    def _onMouseMidPressed(self, event):
        """
        """
        pass
    
    # mouse MOVE
    def _onMouseMoved(self, event):
        """
        """
        # print "-- _onMouseMoved"
        # get coords
        xpixel = event.pos().x()
        ypixel = event.pos().y()
        xdata  = self.invTransform(qwt.QwtPlot.xBottom, xpixel)
        ydata  = self.invTransform(qwt.QwtPlot.yLeft,   ypixel)

        replot = 0
        redraw_selection = False

        self._updateCoord(xdata, ydata, xpixel, ypixel)

            
        # if distance < self.markerDist:

        if self.mode == "movepoint":
            if self.curveList:
                # get current marker / point / curve and distance to this marker
                (cmarker, distance) = self.closestMarker(xpixel, ypixel)
                (ccurve, cpoint)    = self._selectPoint(cmarker)
            
                if distance < 7:
                    if ccurve.isControlled[cpoint] and not self._isPointMoving:
                        self._highlightPointMarker (cmarker, True)
                        self.oldOverMarker = cmarker
                else:
                    if (self.oldOverMarker != None) and not self._isPointMoving:
                        self._highlightPointMarker (self.oldOverMarker, False)
                        self.oldOverMarker = None

        if self._isZooming:
            pass

        if self._isPointMoving:
            self._movePointMarker(self._movingMarker, xdata, ydata)
            replot = 1

        if self._hsel != None:
            redraw_selection = True
            if self._hsel.isSelecting:
                replot = 1
                self._hsel.updateXpos( xdata, xpixel)
        else:
            redraw_selection = False
            
        # move the enhanced cursors
        if self.__updateCursorMarker(xdata, ydata, xpixel, ypixel):
            replot = 1
            
        if replot:
            self.replot()

        if redraw_selection:
            pass
            self._hsel.draw()
        
        # send the mouse position if needed by someone outside the widget
        pos = {"data": (xdata, ydata), "pixel": (xpixel, ypixel)}
        self.emit(qt.PYSIGNAL("GraphPosition"), (pos,))

        
    # mouse RELEASED
    def _onMouseReleased(self, event):
        """
        Function called when a mouse button is released.
        Call the good function depending on the button.
        """
        if   event.button() == qt.Qt.LeftButton:
            self._onMouseLeftReleased(event)
        elif event.button() == qt.Qt.RightButton:
            self._onMouseRightReleased(event)
        elif event.button() == qt.Qt.MidButton:
            self._onMouseMidReleased(event)

    def _onMouseMidReleased(self, event):
        """
        Actions to do when the middle button is released
        """
        pass
    
    def _onMouseLeftReleased(self, event):
        """
        Actions to do when the left button is released:
        - 
        - 
        - 
        """
        # get coords
        xpixel = event.pos().x()
        ypixel = event.pos().y()
        xdata = self.invTransform(qwt.QwtPlot.xBottom, xpixel)
        ydata = self.invTransform(qwt.QwtPlot.yLeft, ypixel)

        if self.mode == "movepoint":
            if self._isPointMoving:
                #self._highlightPointMarker(self._movingMarker, False)
                self._isPointMoving = False

                # add curvename to the signal ?
                self.emit(qt.PYSIGNAL("PointReleased"),
                          (self._movingCurve.name(), self._movingPoint ,
                           xdata, ydata))

                self._movingCurve  = None
                self._movingPoint  = None
                self._movingMarker = None

        if self.mode == "zoom":
            (xmin, ymin) = self._zoomPointOne
            xmax = self.invTransform(qwt.QwtPlot.xBottom, event.x())
            ymax = self.invTransform(qwt.QwtPlot.yLeft,   event.y())
            self.setZoom(xmin, xmax, ymin, ymax)
            self.setMode("zoom")

        if self.mode == "hselection":
            if self._hsel.isSelecting:
                self._hsel.endSelection(xdata, xpixel)
            else:
                print "big pb with hselll"

    def _onMouseRightReleased(self, event):
        """
        """
        pass

    #
    # legend ?
    #
    def _onLegendClicked(self, item):
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
        self._isZooming = 1
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
        self._isZooming = 0
        xpos = self.invTransform(qwt.QwtPlot.xBottom, x)
        ypos = self.invTransform(qwt.QwtPlot.yLeft, y)
        if self.axisEnabled(qwt.QwtPlot.yRight):
            y2pos = self.invTransform(qwt.QwtPlot.yRight, y)
        else:
            y2pos = 0
        self.zoomEnd = (xpos, ypos, y2pos)

        self.removeMarker(self.zoomMarker)
        self.zoomMarker = None

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
                y2min = None
                y2max = None
            else:
                y2min = self.axisScale(qwt.QwtPlot.yRight).lBound()
                y2max = self.axisScale(qwt.QwtPlot.yRight).hBound()
        else:
            y2min = 0
            y2max = 0

        return (xmin, xmax, ymin, ymax, y2min, y2max)

    def setZoom(self, xmin, xmax, ymin, ymax, y2min=0, y2max=0):
        """
        """
        self.zoomStack.append(self.getZoom())
        self.__setZoom(xmin, xmax, ymin, ymax, y2min, y2max)

    def __setZoom(self, xmin, xmax, ymin, ymax, y2min=0, y2max=0):
        """
        """
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
            self._isZooming = 0
            
            if self.mouseAction == 1:
                self.zoomMarkerClass = GraphRectMarker
            elif self.mouseAction == 2:
                self.zoomMarkerClass = GraphXRectMarker

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

    # update the cursors
    # separer les lines et le label ?
    def __updateCursorMarker(self, xdata, ydata, xpixel, ypixel):
        """
        """
   
        if self.cursorType is None:
            return 0

        replot = False
    
        if self.cursorVMarker is not None:
            self.setMarkerXPos(self.cursorVMarker, xdata)
            if self.cursorText:
                self.setMarkerLabelText(self.cursorVMarker, "%g"%xdata )
            replot = True
                
        if self.cursorHMarker is not None:
            self.setMarkerYPos(self.cursorHMarker, ydata)
            if self.cursorText:
                self.setMarkerLabelText(self.cursorHMarker, "%g"%ydata )
            replot = True

                
        return replot

class GraphRectMarker(qwt.QwtPlotMarker):
    """
    """
    def __init__(self, plot):
        """
        """
        qwt.QwtPlotMarker.__init__(self, plot)
        self.x0 = None
        self.x1 = None
        self.y0 = None
        self.y1 = None

    def draw(self, painter, x, y, rect):
        """
        """
        if self.x0 is None:
            self.x0 = x

        self.y0 = y
        self.x1 = x
        self.y1 = y
        painter.drawRect(self.x0, self.y0, self.x1 - self.x0, self.y1 - self.y0)

class GraphXRectMarker(qwt.QwtPlotMarker):
    """
    """
    def __init__(self, plot):
        """
        """
        qwt.QwtPlotMarker.__init__(self, plot)
        self.x0 = None
        self.x1 = None

    def draw(self, painter, x, y, rect):
        """
        """
        if self.x0 is None:
            self.x0 = x

        self.x1 = x
        painter.drawRect(self.x0, rect.top(), self.x1-self.x0, rect.height())

class Hselection:
    """
    """
    topOffset = 2
    bottomOffset = 2 * topOffset

    def __init__(self, painter):
        """
        """

        self.painter = painter

        self.oldXdata  = 0
        self.oldXpixel = 0
        self.xdata     = 0
        self.xpixel    = 0
        
        self.hpixel = 0
        self.isSelecting = False

    def beginSelection(self, xd, xp, h):
        """
        """
        self.oldXdata  = xd
        self.oldXpixel = xp
        self.isSelecting = True
        self.hpixel = h
        
    def endSelection(self, xd, xp):
        """
        """
        self.xpixel = xp
        self.xdata = xd
        self.isSelecting = False

    def updateXpos(self,  xd, xp):
        """
        """
        self.xpixel = xp
        self.xdata  = xd

    def updateSelection(self, plot):
        """
        """
        self.oldXpixel = plot.transform(qwt.QwtPlot.xBottom, self.oldXdata)
        self.xpixel = plot.transform(qwt.QwtPlot.xBottom, self.xdata)
        self.hpixel = plot.can.frameRect().height()
        
    def draw(self):
        """
        """
        self.painter.drawRect( self.oldXpixel,
                               self.topOffset,
                               self.xpixel - self.oldXpixel + 1,
                               self.hpixel - self.bottomOffset )
    
class QubGraphError(Exception):
    """
    """
    def __init__(self, message):
        """
        """
        self.message = message
        
    def __str__(self):
        """
        """
        return "QubGraphError: %s"%self.message




class QubGraphCurve(qwt.QwtPlotCurve):
    # check to not override usefull function ???
    """
    This class implemant a curve class to use within the QubGraph.
    A curve is identified by his name (curveName) and defined by a set of
    points given by their coordinates (xset, yset).
    It is possible to define control points for some points of the curve. The
    controls points can be moved to change the shape of the curve. Controls
    points can be moved by the mouse.
    Movements of control points can be reduce to x and/or y ranges.

    The properties of a point are:
    - Marked     : the point is represented by a marker
    - Movable    : the point can be moved (from the outside of this class)
    - Controlled : the point is mouse movable
    - Constraint : the point cannot move everywhere
    """
    def __init__(self, graph, curveName, xset, yset = None):
        """
        Constructor of the curve:
        - define the array used to manage a curve ( coordinates, constraints
          and flags)
        - define the symbols usables for the markers

        Parameters:
        - name  = curveName to identify the curve and used in the legend label
        - xset = x data if yset is set, y data otherwise
        - yset = y data (or None)
        - grpah = graph containing the curve
        
        If yset is None, xset is considered as being Y values and then
        X = range[1.. len(xset)].

        """

        qwt.QwtPlotCurve.__init__(self, graph, curveName)

        self._name = curveName


        # fill the data arrays
        if yset is None:
            self._Y = xset
            self._X = Numeric.arange(len(self._X), typecode = 'f')
        else:
            self._X = xset
            self._Y = yset

        # ???
        self.savedPen = None 

        if graph != None:
            self.graph = graph
            #self.graph.__legendAddCurve(self.graph.curveKeys[self._name])
            self.graph.setActiveCurve(self._name)
            
        self.constraintXmin = Numeric.arrayrange(len(self._X), typecode = 'f')
        self.constraintXmax = Numeric.arrayrange(len(self._X), typecode = 'f')
        self.constraintYmin = Numeric.arrayrange(len(self._X), typecode = 'f')
        self.constraintYmax = Numeric.arrayrange(len(self._X), typecode = 'f')

        # properties of a point :
        
        # isMovable contains True if this point can be moved (from outside too).
        self.isMovable = Numeric.arrayrange(len(self._X), typecode = 'b')
        
        # isControlled contains True if this point can be moved by the mouse.
        self.isControlled = Numeric.arrayrange(len(self._X), typecode = 'b')

        # isConstraint contains True if this point cannot move everywhere.
        self.isConstraint = Numeric.arrayrange(len(self._X), typecode = 'b')

        # isMarked contains True if this point is represented by a marker.
        self.isMarked = Numeric.arrayrange(len(self._X), typecode = 'b')
        # markerIdx[i] is the index of the marker used to represent the point
        # i of this curve
        self.markerIdx = Numeric.arrayrange(len(self._X), typecode = 'i')
        
        self.isConstraint[:] = False
        self.isControlled[:] = False
        self.isMarked[:]     = False
        self.isMovable[:]    = True
        
    def name(self):
        """
        return the name of the curve
        """
        return self._name

    def setName(self, name):
        """
        set the name of the curve
        """
        self._name = name
        
    def X(self):
        """
        return the X-points array of the curve
        """
        return self._X

    def Y(self):
        """
        return teh Y-points array of the curve
        """
        return self._Y

    def hasControlledPoints(self):
        """
        return True if this curve has one or more controlled points otherwise
        return False.
        """
        if reduce(operator.add, self.isControlled, 0):
            return True
        else:
            return False

    def hasMarkedPoint(self):
        """
        return True if this curve has one or more controlled points otherwise
        return False.
        """
        if reduce(operator.add, self.isMarked, 0):
            return True
        else:
            return False

    # def hasMovablePoint(self):
    # def hasConstraintPoint(self):
        
    
    def savePen(self):
        """
        """
        self.savedPen = qt.QPen(self.pen())

    def getSavedPen(self):
        """
        """
        return self.savedPen

    def defConstraints(self, i, xmin, xmax, ymin, ymax):
        """
        defines the constraints of point i of the curve.
        x (resp. y) can be moved only in range [xmin, xmax] (resp.
        [ymin, ymax])
        """
        if xmin > xmax or ymin > ymax:
            print "error on constraints for point", i, ":",
            "  xmin:", xmin,
            "  xmax:", xmax,
            "  ymin:", ymin,
            "  ymax:", ymax
            # except
        else:
            self.constraintXmin[i] = xmin
            self.constraintXmax[i] = xmax
            self.constraintYmin[i] = ymin
            self.constraintYmax[i] = ymax
            self.isConstraint[i] = True
            self.isControlled[i] = True
            
        # if the point do not respect the constraints, move it.
        self._changePointCoords(i, self._X[i], self._Y[i])

        # update the curve
        #self._update()

    # set properties:
    ##################################
    def setPointControlled(self, i):
        """
        controled => marked
        """
        self.isControlled[i] = True
        self.isMarked[i] = True

    def setPointMarked(self, i):
        """
        """
        self.isMarked[i] = True

    def setPointMovable(self, i):
        """
        """
        self.isMovable[i] = True

    def setPointConstraint(self, i):
        """
        """
        self.isConstraint[i] = True

    #
    def setPointUnControlled(self, i):
        """        
        """
        self.isControlled[i] = False
    
    def setPointUnMarked(self, i):
        """
        not marked => not controlled
        """
        self.isMarked[i] = False
        self.isControlled[i] = False

    def setPointUnMovable(self, i):
        """
        """
        self.isMovable[i] = False

    def setPointUnConstraint(self, i):
        """
        """
        self.isConstraint[i] = False
    ##################################
        
    def _update(self):
        """
        Update the curve in the QWT canvas by redrawing the curve with curent
        coordinates.
        """
        self.setData(self._X, self._Y)
        
        
    def _changePointCoords(self, i, x, y):
        """
        Changes the coordinates of point i of this curve to position (x, y).
        The new position must respect the point constraints, otherwise the
        point is moved to the limits.
        The function return the new position (x, y) eventually corrected in
        order to respect the limits.
        """

        # correct the coords if point is constrained
        if self.isConstraint[i]:
            xmin = self.constraintXmin[i]
            xmax = self.constraintXmax[i]
            ymin = self.constraintYmin[i]
            ymax = self.constraintYmax[i]

            if (x < xmin):
                x = xmin
            if (x > xmax):
                x = xmax
            if (y < ymin):
                y = ymin
            if (y > ymax):
                y = ymax

        # assign coords to point i of the curve
        self.X()[i] = x
        self.Y()[i] = y
        
        # return the new coords
        return (x, y)

    def movePoint(self, i, x, y):
        """
        Changes the coordinates of point i of this curve to position (x, y).
        The new position must respect the point constraints, otherwise the
        point is moved to the limits.
        The function return the new position (x, y) eventually corrected in
        order to respect the limits.
        """
        (x,y) = self._changePointCoords(i, x, y)
        return (x, y)
    
    def fixPoint(self, point):
        """
        Set a point to be uncontrolled by the mouse and marked by a little
        black marker.
        """
        self.setPointUnControlled(point)
        self.graph._reducePointMarker(self.markerIdx[point])


##########################################################################
        
class QubGraphTest(qt.QWidget):
    def __init__(self, parent=None, name="QubGraphTestWindow"):

        qt.QWidget.__init__(self, parent, name)
        
        vlay = qt.QVBoxLayout (self, 2 ,3 , "Main V Layout")
        
        self.qubGW = QubGraph(self)
        
        # define control bar
        bbar = qt.QWidget(self)
        blay = qt.QHBoxLayout(bbar, 2 ,3 , "button bar layout")
        
        vlay.addWidget(self.qubGW)
        vlay.addWidget(bbar)
        
        # define control buttons
        quitButton = qt.QPushButton( "Quit", bbar)
        
        zoomButton = qt.QPushButton( "zoom",  bbar)
        zoomButton.setPixmap(qt.QPixmap(zoom_xpm))
        
        hselButton = qt.QPushButton( "Hsel", bbar )
        hselButton.setPixmap(qt.QPixmap(hselection_xpm))
        
        moveButton = qt.QPushButton( "move", bbar )
        moveButton.setPixmap(qt.QPixmap(smove_point_xpm))
        
        noneButton = qt.QPushButton( "none", bbar )
        
        blay.addWidget (zoomButton)
        blay.addWidget (hselButton)
        blay.addWidget (moveButton)
        blay.addWidget (noneButton)
        blay.addStretch()
        blay.addWidget (quitButton)
        
        self.connect(zoomButton, qt.SIGNAL("clicked()"),
                     self.setModeZoom)
        
        self.connect(hselButton, qt.SIGNAL("clicked()"),
                     self.setModeHsel)

        self.connect(moveButton, qt.SIGNAL("clicked()"),
                     self.setModeMove)

        self.connect(noneButton, qt.SIGNAL("clicked()"),
                     self.setModeNone)

        self.connect(quitButton, qt.SIGNAL("clicked()"),
                     self, qt.SLOT("close()"))
        
        #
        # plot some sample curves
        #

        # plot a simple curve (without control points)
        x = Numeric.arrayrange(0.0, 10.0, 0.5)
        y = Numeric.sin( x + ( 1 / 10.0 ) * 3.14 ) + 1

        #mySampleCurve = QubGraphCurve(self.qubGW, "matrace", x, y)

        mySampleCurve2 = QubGraphCurve(self.qubGW, "matrace2",
                                  [1,2,3,4,10], [0,0,4,4,2])

        
        # sample of marked curve
        #    a = array([0.0, 1.0, 2.0, 4.0, 8.0, 10.0 ])
        #    self.qubGW.setMarkedCurve( "mysampleTrace", a )

        # set the labels
        self.qubGW.setXLabel("XBabel")
        self.qubGW.setYLabel("YBabel")

        #                           point xmin xmax ymin ymax
        mySampleCurve2.defConstraints( 1,    2,   8,   0,   0)
        mySampleCurve2.defConstraints( 2,    2,   8,   4,   4)
        mySampleCurve2.setPointControlled(1)
        mySampleCurve2.setPointControlled(2)

        mySampleCurve2.movePoint(0,  0, 0)
        mySampleCurve2.movePoint(3, 10, 4)
        mySampleCurve2.setPointMarked(0)
        mySampleCurve2.setPointMarked(3)
        
        #self.qubGW.setCurve(mySampleCurve)

        self.qubGW.setCurve(mySampleCurve2)

        # define the view
        self.qubGW.setZoom(-0.5, 10.5, -0.5, 4.5)
        self.qubGW.show()
        
        # move point 2 of curve "ConstrainedCurve" to position (5, 4) 
        # self.qubGW.deplace("ConstrainedCurve", 2, 6.0, 4.0)

    def setModeZoom(self):
        self.qubGW.setMode("zoom")

    def setModeHsel(self):
        self.qubGW.setMode("hselection")

    def setModeMove(self):
        self.qubGW.setMode("movepoint")

    def setModeNone(self):
        self.qubGW.setMode(None)

if __name__=="__main__":
    app = qt.QApplication(sys.argv)
    
    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                       app, qt.SLOT("quit()"))

    window = QubGraphTest()
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
