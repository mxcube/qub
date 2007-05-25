import weakref
import qt
import Qwt5 as qwt

from Qub.Tools.QubWeakref import createWeakrefMethod

class _stat:
    def __init__(self,statMachine) :
        self._statMachine = statMachine
        statMachine.currentStat = self
    def event(self,event) :
        return []

##@brief a marker to control curve point
#
#If you set a callback, it'll be called each time the marker's value changed
#@see QubGraphCurvePointControl::setValueChangeCallback
class QubGraphCurvePointControl(qwt.QwtPlotMarker) :
    class _picker(qwt.QwtPicker) :
        class _statMachine(qwt.QwtPickerMachine) :
            class _outMarker(_stat) :
                def __init__(self,statMachine) :
                    _stat.__init__(self,statMachine)
                    self._statMachine.marker.highlight(False)
                    plot = self._statMachine.marker.plot()
                    if plot: plot.replot()
                    
                def __del__(self) :
                    self._statMachine.marker.highlight(True)
                    self._statMachine.marker.plot().replot()
                        
                def event(self,event) :
                    if isinstance(event,qt.QMouseEvent) :
                        marker = self._statMachine.marker
                        plot = marker.plot()
                        bRect = marker.boundingRect()
                        bRect = marker.transform(plot.canvasMap(marker.xAxis()),
                                                 plot.canvasMap(marker.yAxis()),
                                                 bRect)
                        x,y = bRect.x(),bRect.y()
                        if abs(x - event.x()) < 7 and abs(y - event.y()) < 7 :
                            QubGraphCurvePointControl._picker._statMachine._inMarker(self._statMachine)
                    return []

            class _inMarker(_stat) :
                def __init__(self,statMachine) :
                    _stat.__init__(self,statMachine)
                    
                def event(self,event) :
                    if(isinstance(event,qt.QMouseEvent)) :
                        marker = self._statMachine.marker
                        plot = marker.plot()
                        bRect = marker.boundingRect()
                        bRect = marker.transform(plot.canvasMap(marker.xAxis()),
                                                 plot.canvasMap(marker.yAxis()),
                                                 bRect)
                        x,y = bRect.x(),bRect.y()
                        if abs(x - event.x()) > 7 or abs(y - event.y()) > 7 :
                            QubGraphCurvePointControl._picker._statMachine._outMarker(self._statMachine)
                        elif(event.type() == qt.QEvent.MouseButtonPress and
                             event.button() == qt.QEvent.LeftButton) :
                            QubGraphCurvePointControl._picker._statMachine._moveMarker(self._statMachine)
                            return [self._statMachine.Begin]
                    return []
                
            class _moveMarker(_stat) :
                def __init__(self,statMachine) :
                    _stat.__init__(self,statMachine)

                def event(self,event) :
                    if(isinstance(event,qt.QMouseEvent)) :
                        if(event.type() == qt.QEvent.MouseButtonRelease and
                           event.button() == qt.QEvent.LeftButton) :
                            QubGraphCurvePointControl._picker._statMachine._inMarker(self._statMachine)
                            return [self._statMachine.End]
                        else:
                            return [self._statMachine.Move]
                    else:
                        return []

            def __init__(self,marker) :
                qwt.QwtPickerMachine.__init__(self)
                self.marker = marker
                QubGraphCurvePointControl._picker._statMachine._outMarker(self)
                
            def transition(self,eventPattern,event) :
                return self.currentStat.event(event)
            
        def __init__(self,marker,widget) :
            qwt.QwtPicker.__init__(self,widget)
            self.__stat = QubGraphCurvePointControl._picker._statMachine(marker)
            self.marker = marker

        def begin(self) :
            pass

        def end(self,aFlag = True) :
            return True

        def move(self,point) :
            plot = self.marker.plot()
            rect = self.marker.invTransform(plot.canvasMap(self.marker.xAxis()),
                                            plot.canvasMap(self.marker.yAxis()),
                                            qt.QRect(point.x(),point.y(),0,0))
            self.marker.setValue(rect.x(),rect.y())
            plot.replot()
            
        def stateMachine(self,flag) :
            return self.__stat
        
    def __init__(self,curve,anIndex) :
        qwt.QwtPlotMarker.__init__(self)

        self.__xMin = None
        self.__xMax = None
        self.__yMin = None
        self.__yMax = None
        self.__cbk = None
        
        self.__curve =  weakref.ref(curve)
        self.__index = anIndex
        self.__movableMarkerSymbol = qwt.QwtSymbol (qwt.QwtSymbol.Diamond,
                                                     qt.QBrush(qt.Qt.red),
                                                     qt.QPen(qt.Qt.blue),
                                                     qt.QSize(15, 15))
        self.__higlightedMarkerSymbol = qwt.QwtSymbol (qwt.QwtSymbol.Diamond,
                                                     qt.QBrush(qt.Qt.green),
                                                     qt.QPen(qt.Qt.green),
                                                     qt.QSize(15, 15))
        self.__moveCursor = qt.QCursor(qt.Qt.SizeAllCursor)
        
    def attach(self,plot) :
        qwt.QwtPlotMarker.attach(self,plot)
        if plot:
            self.__picker = QubGraphCurvePointControl._picker(self,plot.canvas())
            self.__picker.setSelectionFlags(0)
        else:
            self.__picker = None

    def highlight(self,aFlag) :
        self.setSymbol(aFlag and self.__higlightedMarkerSymbol or self.__movableMarkerSymbol)
        plot = self.plot()
        if plot :
            plot.canvas().setCursor(aFlag and self.__moveCursor or plot.defaultCursor())
            
    ##@brief set the callback for the value change
    #
    #the callback should have this signature <b>def callback_func(xValue,yValue)</b>
    def setValueChangeCallback(self,cbk) :
        self.__cbk = createWeakrefMethod(cbk)
        
    def setValue(self,x,y) :
        oldx,oldy = self.xValue(),self.yValue()
        x,y = self.__checkConstraints(x,y)
        if abs(oldx - x) > 1e-9 or abs(oldy - y) > 1e-9 :
            qwt.QwtPlotMarker.setValue(self,x,y)
            curve = self.__curve()
            if curve:
                curve.modifyValue(self.__index,x,y)
            if self.__cbk : self.__cbk(x,y)
            
    ##@brief set contraint limit
    #if one param is set to None -> no limit
    def setConstraints(self,xMin,xMax,yMin,yMax) :
        self.__xMin = xMin
        self.__xMax = xMax
        self.__yMin = yMin
        self.__yMax = yMax

        values = self.__checkConstraints()
        self.setValue(*values)
        
    def __checkConstraints(self,x = None,y = None) :
        if x is None :
            x = self.xValue()
        if y is None :
            y = self.yValue()
            
        yValue = self.yValue()
        if self.__xMax is not None and x > self.__xMax:
            x = self.__xMax
        elif self.__xMin is not None and x < self.__xMin:
            x = self.__xMin

        xValue = self.xValue()
        if self.__yMax is not None and y > self.__yMax:
            y = self.__yMax
        elif self.__yMin is not None and y < self.__yMin:
            y = self.__yMin

        return (x,y)

##@brief a simple marker on curve
#
class QubGraphCurvePointMarked(qwt.QwtPlotMarker) :
    def __init__(self,curve,anIndex) :
        qwt.QwtPlotMarker.__init__(self)

        self.__curve = weakref.ref(curve)
        self.__index = anIndex

        self.__symbol = qwt.QwtSymbol (qwt.QwtSymbol.Diamond,
                                       qt.QBrush(qt.Qt.black),
                                       qt.QPen(qt.Qt.black),
                                       qt.QSize(7,7))
        self.setSymbol(self.__symbol)

    def setValue(self,x,y) :
        qwt.QwtPlotMarker.setValue(self,x,y)
        curve = self.__curve()
        if curve:
            curve.modifyValue(self.__index,x,y)
        

##@brief a simple object to set a follow marker curve
#
#
class QubGraphCurvePointFollowMarked(qwt.QwtPlotMarker) :
    def __init__(self,curve) :
        qwt.QwtPlotMarker.__init__(self)
        self.__pointIndex = -1
        self.__curve = curve and weakref.ref(curve) or None
        self.__symbol = qwt.QwtSymbol (qwt.QwtSymbol.Diamond,
                                       qt.QBrush(qt.Qt.red),
                                       qt.QPen(qt.Qt.black),
                                       qt.QSize(7,7))
        self.setSymbol(self.__symbol)
        # TEXT MARKER
        self.__textMarker = qwt.QwtPlotMarker()
        self.__textLabelCBK = None

    ##@brief set the text label callback
    #
    #the callback methode should have this signature <b>def callback_textlabel_callback(x,y)<b>
    #and return a simple text string or rich text
    def setTextLabelCallback(self,cbk) :
        self.__textLabelCBK = createWeakrefMethod(cbk)
        
    def attach(self,plot) :
        qwt.QwtPlotMarker.attach(self,plot)
        self.__textMarker.attach(plot)
        if plot:
            self.__picker = qwt.QwtPicker(plot.canvas())
            self.__picker.setSelectionFlags(qwt.QwtPicker.PointSelection | qwt.QwtPicker.DragSelection)
            qt.QObject.connect(self.__picker,qt.SIGNAL('moved(const QPoint&)'),self.__moved)
            qt.QObject.connect(self.__picker,qt.SIGNAL('appended(const QPoint &)'),self.__moved)
        else:
            self.__picker = None

    def refresh(self) :
        curve = self.__curve and self.__curve() or None
        if curve and self.__pointIndex > -1 and self.__pointIndex < curve.dataSize() :
            self.setValue(curve.x(self.__pointIndex),curve.y(self.__pointIndex))
            if self.__textLabelCBK:
                textLabel = self.__textLabelCBK(curve.x(self.__pointIndex),curve.y(self.__pointIndex))
            else:
                textLabel = '<b><font COLOR=red>(%d,%d)</font></b>' % (curve.x(self.__pointIndex),curve.y(self.__pointIndex))
            self.__textMarker.setLabel(qwt.QwtText(textLabel))

    def setVisible(self,aFlag) :
        qwt.QwtPlotMarker.setVisible(self,aFlag)
        self.__textMarker.setVisible(aFlag)
            
    def __moved(self,point) :
        curve = self.__curve and self.__curve() or None
        if curve and self.isVisible() :
            self.__pointIndex,distance = curve.closestPoint(point)
            self.setValue(curve.x(self.__pointIndex),curve.y(self.__pointIndex))
            plot = self.plot()
            rect = self.invTransform(plot.canvasMap(self.xAxis()),
                                     plot.canvasMap(self.yAxis()),
                                     qt.QRect(point.x(),point.y(),0,0))
            self.__textMarker.setValue(rect.x(),rect.y())

            if self.__textLabelCBK:
                textLabel = self.__textLabelCBK(curve.x(self.__pointIndex),curve.y(self.__pointIndex))
            else:
                textLabel = '<b><font COLOR=red>(%d,%d)</font></b>' % (curve.x(self.__pointIndex),curve.y(self.__pointIndex))
            self.__textMarker.setLabel(qwt.QwtText(textLabel))

            if point.x() > plot.canvas().width() / 2:
                self.__textMarker.setLabelAlignment(qt.Qt.AlignLeft)
            else:
                self.__textMarker.setLabelAlignment(qt.Qt.AlignRight)
            self.plot().replot()
            
    def copy(self) :
        graphCurvePointFollowMarked = QubGraphCurvePointFollowMarked(self.__curve())
        textMarker = graphCurvePointFollowMarked._QubGraphCurvePointFollowMarked__textMarker
        textMarker.setLabel(self.__textMarker.label())
        textMarker.setValue(self.__textMarker.value())
        textMarker.setLabelAlignment(self.__textMarker.labelAlignment())
        graphCurvePointFollowMarked.setValue(self.value())
        return graphCurvePointFollowMarked
