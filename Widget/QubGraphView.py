import qt
import sys

from Qub.Widget.QubView import QubView
from Qub.Widget.QubGraph import QubGraph

################################################################################
####################               QubGraphView             ####################
################################################################################
class QubGraphView(QubView):
    """
    The QubGraphView allows to display Graph and put behavior (zoom,
    selection, print ....) on it using QubAction.
    It inherits QubView to get the window structure (toolbar/contextmenu,
    view, statusbar).
    It creates an instance of QubGraph as QubView view.
    """
    def __init__(self, parent=None, name=None, actions=None,
                 flags=qt.Qt.WDestructiveClose):
        QubView.__init__(self, parent, name,flags)
        
        widget = QubGraph(self, "QubGraph")
        
        self.setView(widget)
        
        if actions is not None:
            self.addAction(actions)
    
    def setCurve(self, name, x, y):
        view = self.view()
        if view is not None:
            self.view().setCurve(name, x, y)
                
    def setMarkedCurve(self, name, x, y):
        view = self.view()
        if view is not None:
            self.view().setMarkedCurve(name, x, y)
            
                      
################################################################################
####################    TEST -- QubViewGraphTest -- TEST   #####################
################################################################################


class QubMain(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        #      pixmap = qt.QPixmap(file)
        
        actions = []
        action = QubPrintPreviewAction(place="statusbar", show=1, group="marcel")
        actions.append(action)
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
        
        self.qubGraphView = QubGraphView(container, "Test QubgraphView", actions)
                    
        hlayout.addWidget(self.qubGraphView)
    
        self.setCentralWidget(container)
               
##  MAIN   
if  __name__ == '__main__':
    from Qub.Print.QubPrintPreviewAction import QubPrintPreviewAction

    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubMain()
    window.qubGraphView.setMarkedCurve( "ConstrainedCurve", [0,2,8,10], [0,0,4,4] )

    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
