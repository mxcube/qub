##@defgroup howto_graph display a graph
#@ingroup howto
#To display a graph with qub, you should use the container QubGraph (Qub.Widget.Graph.QubGraph.QubGraph)
#and add some curves to the graph by using QubGraphCurve (Qub.Widget.Graph.QubGraphCurve.QubGraphCurve).
#All of those object are inherited from <A href="http://qwt.sourceforge.net/index.html">qwt</A>\n
#<b>Simple Example:</b>
#Let's say that you want to draw a sin(x)/x in red and a sin(x) in green. On the first curve sin(x)/x you want to add a followed curve point and a marker on the top of it. On the second curve sin(x) you whant to control each point around y == 0\n
# - Qt Init\n
#import qt\n
#import numpy\n
#\n
#from Qub.Widget.Graph.QubGraph import QubGraph\n
#from Qub.Widget.Graph.QubGraphCurve import QubGraphCurve\n
#\n
#app = qt.QApplication([])\n
#graph = QubGraph()\n
# - class to define a text format for the follow curve point\n
#class _myFormat:\n
#&nbsp;&nbsp;&nbsp;&nbsp;def&nbsp;CBK(self,x,y) :\n
#&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return '%d,%.2f' % ((x * 180) / numpy.pi,y)\n
# - init the data curve x and y\n
#xData = numpy.arange(-4 * numpy.pi,4 * numpy.pi,numpy.pi/16)\n
#yData_sinx_x = numpy.sin(xData) / xData\n
#\n
#yData_sinx = numpy.sin(xData)\n
#\n
# - First curve sin(x)/x\n
#sinx_xCurve = QubGraphCurve(title='sin(x)/x')\n
#sinx_xCurve.attach(graph)\n
#sinx_xCurve.setPen(qt.QPen(qt.Qt.red))\n
#sinx_xCurve.setData(xData,yData_sinx_x)\n
#\n
# -# add a curve follow marked\n
#sinx_xFollowMarked = sinx_xCurve.getCurvePointFollowMarked()\n
#format = _myFormat()\n
#sinx_xFollowMarked.setTextLabelCallback(format.CBK)\n
#\n
# -# add a  marked point on the middle of the curve\n
#markedPoint = sinx_xCurve.getPointMarked(len(xData) / 2)
# - Second curve sin(x)\n
#sinxCurve = QubGraphCurve(title='sin(x)')\n
#sinxCurve.attach(graph)\n
#sinxCurve.setPen(qt.QPen(qt.Qt.green))\n
#sinxCurve.setData(xData,yData_sinx)\n
# -# add a controled marked point on all y == 0\n
#controledPoints = []\n
#for i,y in enumerate(yData_sinx) :\n
#&nbsp;&nbsp;&nbsp;&nbsp;if 0. < y < 1e-3:\n
#&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;controledPoints.append(sinxCurve.getPointControl(i))\n
#
# - Qt Loop\n
#graph.replot()\n
#graph.show()\n
#app.setMainWidget(graph)\n
#\n
#app.exec_loop()\n


class _myFormat:
    def CBK(self,x,y) :
        return '%d,%.2f' % ((x * 180) / numpy.pi,y)

import qt
import numpy

from Qub.Widget.Graph.QubGraph import QubGraph
from Qub.Widget.Graph.QubGraphCurve import QubGraphCurve

app = qt.QApplication([])
graph = QubGraph()

xData = numpy.arange(-4 * numpy.pi,4 * numpy.pi,numpy.pi/16)
yData_sinx_x = numpy.sin(xData) / xData

yData_sinx = numpy.sin(xData)

#First curve sin(x)/x
sinx_xCurve = QubGraphCurve(title='sin(x)/x')
sinx_xCurve.attach(graph)
sinx_xCurve.setPen(qt.QPen(qt.Qt.red))
sinx_xCurve.setData(xData,yData_sinx_x)

#add a curve follow marked
sinx_xFollowMarked = sinx_xCurve.getCurvePointFollowMarked()
format = _myFormat()
sinx_xFollowMarked.setTextLabelCallback(format.CBK)

#add a  marked point on the middle of the curve
markedPoint = sinx_xCurve.getPointMarked(len(xData) / 2)

#Second curve sin(x)
sinxCurve = QubGraphCurve(title='sin(x)')
sinxCurve.attach(graph)
sinxCurve.setPen(qt.QPen(qt.Qt.green))
sinxCurve.setData(xData,yData_sinx)


#add a controled marked point on all y == 0
controledPoints = []
for i,y in enumerate(yData_sinx) :
    if 0. < y < 1e-3:
        controledPoints.append(sinxCurve.getPointControl(i))
    
graph.replot()
graph.show()
app.setMainWidget(graph)

app.exec_loop()
