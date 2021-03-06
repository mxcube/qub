import logging
import Qwt5 as qwt
import qt

from Qub.Widget.Graph.QubGraph import QubGraphView
from Qub.Widget.Graph.QubGraphCurveMarker import QubGraphCurvePointControl
from Qub.Widget.Graph.QubGraphCurveMarker import QubGraphCurvePointMarked
from Qub.Widget.Graph.QubGraphCurveMarker import QubGraphCurvePointFollowMarked

##@brief curve class
#
#With this object you can define a graphic curve to be drawn in Qub::Widget::QubGraph::QubGraph
#
#@ingroup GraphDisplay
#
class QubGraphCurve(qwt.QwtPlotCurve):
    Black = qt.Qt.black
    Red = qt.Qt.red
    Blue = qt.Qt.blue
    Green = qt.Qt.green

    NoSymbol = qwt.QwtSymbol.NoSymbol
    Diamond = qwt.QwtSymbol.Diamond
    Rect = qwt.QwtSymbol.Rect
    Triangle = qwt.QwtSymbol.Diamond
    Cross = qwt.QwtSymbol.Cross
    Hexagon = qwt.QwtSymbol.Hexagon

    NoCurve = qwt.QwtPlotCurve.NoCurve
    Lines = qwt.QwtPlotCurve.Lines
    Dots = qwt.QwtPlotCurve.Dots
    
    def __init__(self,title = '',**keys) :
        qwt.QwtPlotCurve.__init__(self,title)
        self.__controlPoint = {}
        self.__markedPoint = {}
        self.__markedFollow = None
        
        self._X = None
        self._Y = None
                    
    def setCurveStyle(self, symbol=NoSymbol, style=Lines, color=Black):
        brush = qt.QBrush(color)
        pen = qt.QPen(color)
        size = qt.QSize(5,5)
        sym = qwt.QwtSymbol(symbol, brush, pen, size)
        self.setSymbol(sym)
        self.setPen(pen)
        self.setStyle(style)
                
    ##@brief get or create a control point on that curves
    #
    #@param anId the point id of the curve
    #@return a Qub::Widget::Graph::QubGraphCurveMarker::QubGraphCurvePointControl
    #
    def getPointControl(self,anId) :
        x = self.x(anId)
        y = self.y(anId)
        curveControl = self.__controlPoint.get(anId,QubGraphCurvePointControl(self,anId))
        curveControl.setValue(x,y)
        if self.plot() :
            curveControl.attach(self.plot())
        return curveControl
    ##@brief get or create a marker
    #
    #@param anId the point id of the curve
    #@return a Qub::Widget::Graph::QubGraphCurveMarker::QubGraphCurvePointMarked
    #
    def getPointMarked(self,anId) :
        x = self.x(anId)
        y = self.y(anId)
        pointMarked = self.__markedPoint.get(anId,QubGraphCurvePointMarked(self,anId))
        pointMarked.setValue(x,y)
        if self.plot() :
            pointMarked.attach(self.plot())
        return pointMarked
    ##@brief get a follow curves cursor (you can only have one by curve)
    #
    #@return a Qub::Widget::Graph::QubGraphCurveMarker::QubGraphCurvePointFollowMarked
    def getCurvePointFollowMarked(self) :
        if self.__markedFollow :
            pointFollowMarked = self.__markedFollow
        else:
            pointFollowMarked = QubGraphCurvePointFollowMarked(self)
            if self.plot() :
                pointFollowMarked.attach(self.plot())
            self.__markedFollow = pointFollowMarked
        return pointFollowMarked
            
    ##@brief use to modify One value
    #
    #@param index the index in the data table
    #@param xData
    # - if yData is not None -> the y Axis value
    # - else the x Axis value
    #
    #@param yData the y Axis value
    def modifyValue(self,index,xData,yData = None) :
        if yData is None :
            yData = xData
            xData = index

        self._X[index] = xData
        self._Y[index] = yData
        self.setData(self._X,self._Y)

    ##@brief use to set data value
    #
    #@param xDatas
    # - if yDatas is None -> the y Axis values
    # - else the x Axis values
    #
    #@param yDatas the y Axis values
    def setData(self,xDatas,yDatas = None) :
        if yDatas is None:
            yDatas = xDatas
            xDatas = range(len(yDatas))
            
        qwt.QwtPlotCurve.setData(self,xDatas,yDatas)
        
        self._X = xDatas
        self._Y = yDatas
        for markedDict in [self.__controlPoint,self.__markedPoint] :
            for index,control in markedDict :
                try:
                    control.setValue(self._X[index],self._Y[index])
                except IndexError,err:
                    logging.getLogger().error('Marked point %d will be removed, %s' % (index,err))
                    markedDict.pop(index)
        if self.__markedFollow:
            self.__markedFollow.refresh()

    ##@brief attach a curve on a graph
    #
    def attach(self,graph) :
        if isinstance(graph,QubGraphView) :
            graph = graph.view()
        qwt.QwtPlotCurve.attach(self,graph)
        for markedDict in [self.__controlPoint,self.__markedPoint] :
            for index,control in markedDict:
                control.attach(graph)
        if self.__markedFollow :
            self.__markedFollow.attach(graph)
                
