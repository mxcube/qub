# test ;llid210 2eme

import sys

import qt
import qttable 

__revision__="$Revision$"

# BUGS
# - cells display..


# TODO
# - disable selection/move/resize

class QubTable(qttable.QTable):
    def __init__(self,  parent=None, name=None, row=1, col=1, data=None, flags=None):

        qttable.QTable.__init__(self, row, col, parent, name)
        
        self.parent = parent
        
        self.col = col
        self.row = row
        self.contextMenu = None
        self.data = data

        self.txtColor  = qt.QColor("black")
        self.cellBrush = qt.QBrush(qt.QColor("green"), qt.Qt.Dense4Pattern)

        self.verouille(True)
        
    def setContextMenu(self, menu):
        self.contextMenu = menu 

    def paintCell(self, painter, row, col, cr, selected):
        rect = qt.QRect(0,0, cr.width(), cr.height())
        painter.fillRect(rect, self.cellBrush)
        painter.setPen(self.txtColor)
        painter.drawText( 0,0, cr.width(), cr.height(),
                          qt.Qt.AlignCenter, str( round(self.data[row][col], 2) )  )

    def verouille(self, bool):
        if bool:
            self.setReadOnly(True)
            self.setColumnMovingEnabled ( False )

            for c in range (self.col):
                self.setColumnStretchable ( c, False )
                self.setSelectionMode(qttable.QTable.NoSelection)
                
            for r in range (self.row):
                self.setRowStretchable ( r, False )
        else:
            self.setReadOnly(False)
            self.setColumnMovingEnabled ( True )

    def contentsContextMenuEvent(self, event):
        if self.contextMenu is not None:
            if event.reason() == qt.QContextMenuEvent.Mouse:
                self.contextMenu.exec_loop(qt.QCursor.pos())

    def getPPP(self):
        return qt.QPixmap(qt.QPixmap.grabWidget(self))
    
#########################################################################
###  QUBTABLE TEST 
#########################################################################

class QubTableTest(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        self.__scrollbarMode = ["Auto", "AlwaysOff", "Fit2Screen", "FullScreen"]
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)

        a = Numeric.array(range(100000), 'f')
        datatab  = Numeric.resize(a, (1000,100))
    
        myTable = QubTable(container, "Table_Test", 1000, 100, datatab)
        hlayout.addWidget(myTable)
        self.setCentralWidget(container)


        
if __name__=="__main__":
    import Numeric
    app = qt.QApplication(sys.argv)
    
    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                       app, qt.SLOT("quit()"))

    window = QubTableTest()
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
