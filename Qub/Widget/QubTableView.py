import qt
import sys

from Qub.Widget.QubView import QubView
from Qub.Widget.QubTable import QubTable

################################################################################
####################               QubTableView             ####################
################################################################################
class QubTableView(QubView):
    """
    The QubTableView allows to display big set of data in a table like a
    spreadsheet.
    Only needed values are displayed.
    """
    def __init__(self, parent=None, name=None, row=1, col=1, data=None, actions=None,
                 flags=qt.Qt.WDestructiveClose):
        QubView.__init__(self, parent, name,flags)
        
        widget = QubTable(self, "QubTable", row, col, data)
        
        self.setView(widget)
        
        if actions is not None:
            self.addAction(actions)
                          
################################################################################
####################    TEST -- QubViewTableTest -- TEST   #####################
################################################################################

class QubMain(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        # a dummy action
        actions = []
        action = QubPrintPreviewAction(place="statusbar", show=1, group="marcel")
        actions.append(action)
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)

        a = Numeric.array(range(100000), 'f')
        datatab  = Numeric.resize(a, (1000,100))

        qubTableView = QubTableView(container,
                                    "QubTableView",
                                    1000, 100, datatab, actions)
   
        hlayout.addWidget(qubTableView)
    
        self.setCentralWidget(container)
               
##  MAIN   
if  __name__ == '__main__':
    from Qub.Print.QubPrintPreviewAction import QubPrintPreviewAction
    import Numeric
    
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubMain()

    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
