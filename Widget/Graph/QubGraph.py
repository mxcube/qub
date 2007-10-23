import qt
import Qwt5 as qwt

from Qub.Widget.QubView import QubView

from Qub.Widget.Graph.QubGraphCurveMarker import QubGraphCurvePointFollowMarked

from Qub.Widget.QubMdi import QubMdiCheckIfParentIsMdi

##@defgroup GraphDisplay Tools to display curves histogram...
#

##@ingroup GraphDisplay
#
##@brief simple graph widget
#
#This class is herited from qwt.QwtPlot
class QubGraph(qwt.QwtPlot) :
    def __init__(self,parent=None,name='') :
        qwt.QwtPlot.__init__(self,qwt.QwtText(name),parent)
        canvas = self.canvas()
        canvas.setMouseTracking(True)
        canvas.setPaletteBackgroundColor(qt.Qt.white)
        self.__grid = qwt.QwtPlotGrid()
        self.__grid.setMajPen(qt.QPen(qt.Qt.black,1,qt.Qt.DotLine))
        self.__grid.attach(self)
        self.__defaultCursor = qt.QCursor(self.canvas().cursor())
    ##@brief set the absciss label
    #
    def setXLabel(self,label) :
        self.setAxisTitle(self.xBottom,label)
    ##@brief set the ordonnes label
    #
    def setYLabel(self,label) :
        self.setAxisTitle(self.yLeft,label)

    ##@brief get the default cursor
    #
    #internal function
    def defaultCursor(self) :
        return self.__defaultCursor

    ##@brief get a graph copy with all the curves and marker
    #
    #Use for example by the print function
    #
    def getGraph(self) :
        graph = qwt.QwtPlot()
        graph.setPaletteBackgroundColor(qt.QColor(self.canvasBackground()))
        graph.setTitle(qwt.QwtText(self.title()))
               
        for axis in [graph.yLeft,graph.yRight,graph.xBottom,graph.xTop] :
            graph.setAxisTitle(axis,qwt.QwtText(self.axisTitle(axis)))
            graph.enableAxis(axis,self.axisEnabled(axis))
            if isinstance(self.axisScaleEngine(axis),qwt.QwtLog10ScaleEngine) :
                graph.setAxisScaleEngine(axis,qwt.QwtLog10ScaleEngine())
            scaleDiv = self.axisScaleDiv(axis)
            graph.setAxisScale(axis,scaleDiv.lBound(),scaleDiv.hBound())

        for item in self.itemList() :
            if isinstance(item,qwt.QwtPlotCurve) :
                newItem = qwt.QwtPlotCurve()
                newItem.setData(item.data().copy())
                newItem.setStyle(item.style())
                newItem.setPen(qt.QPen(item.pen()))
            elif isinstance(item,QubGraphCurvePointFollowMarked) and item.isVisible():
                newItem = item.copy()
            elif isinstance(item,qwt.QwtPlotGrid) :
                newItem = qwt.QwtPlotGrid()
                newItem.setMajPen(qt.QPen(item.majPen()))
            else: continue
            newItem.attach(graph)
        graph.replot()
        return graph

##@brief same as QubGraph but herited from QubView so ,
#you can add some action
#
class QubGraphView(QubView) :
    def __init__(self, parent = None, name = "",actions=[]):
        QubView.__init__(self,parent,name,flags=0)
        self.setView(QubGraph(parent=self,name=name))
        if actions : self.addAction(actions)

    def __nonzero__(self) :
        return True

    def __getattr__(self,attr) :
        if not attr.startswith('__') :
            try:
                return getattr(self.view(),attr)
            except AttributeError,err:
                raise AttributeError,'QubGraphView instance has not attribute %s' % attr
        else:
            raise AttributeError,'QubGraphView instance has not attribute %s' % attr

    def show(self):
        shownFlag = self.isShown()
        QubView.show(self)
        _,mainWidget = QubMdiCheckIfParentIsMdi(self)
        if mainWidget or self.parent() is None:
            sizeHint = self.sizeHint()
            width,height = sizeHint.width(),sizeHint.height()
            self.setMinimumSize(sizeHint)
            if not shownFlag :
                self.resize(max(width,height * 16 / 9),height)
