import qt

paintbrush_xpm = [
"17 19 8 1",
"   c None",
"n  c #000000",
"c  c #444444",
"m  c #AAAAAA",
"*  c #DDDDDD",
"d  c #949494",
"e  c #706c6c",
"j  c #000000",
"           ndecn ",
"          ndeecn ",
"         ndeecn  ",
"         ndeecn  ",
"        ndeecn   ",
"        ndeecn   ",
"       ndeecn    ",
"       ndeecn    ",
"       nnnnn     ",
"      n*mmn      ",
"     n**mcn      ",
"     n*mmcn      ",
"    n*mmcn       ",
"    nmccn        ",
"   nccnn         ",
"  nnnn           ",
"                 ",
" jjjjjjjjjjjjjj  ",
" jjjjjjjjjjjjjj  "]


################################################################################
##################           QubColorToolButton                   ##############
################################################################################
class QubColorToolButton(qt.QToolButton):
    """
    The QubColorToolButton provides a pushButton usable as a color selector. Its
    icon represents a paint tool with a color sample dynamicly updated according
    to the selected color.
    """
    def __init__(self, parent=None, name="CTB"):
        """
        """
        qt.QToolButton.__init__(self, parent, name)

        self.setAutoRaise(True)
        
        self.simpleColor = [qt.Qt.black,
                            qt.Qt.white,
                            qt.Qt.red,
                            qt.Qt.green,
                            qt.Qt.blue,
                            qt.Qt.yellow]
        
        self.selectedColor = qt.QColor(qt.Qt.black)
        
        self.setIconColor(self.selectedColor)
        
        self.popupMenu = qt.QPopupMenu(self)

        self.setPopup(self.popupMenu)
        self.setPopupDelay(0)
        
        colorBar = qt.QHButtonGroup(self.popupMenu)
        colorBar.setFlat(True)
        colorBar.setInsideMargin(5)
        colorButton = []
        
        for color in self.simpleColor:
            w = qt.QPushButton(colorBar)
            w.setPaletteBackgroundColor(color)
            w.setFixedSize(15, 15)
            colorBar.insert(w)
            colorButton.append(w)
        
        self.connect(colorBar, qt.SIGNAL("clicked(int )"),
                     self.selectSimpleColor)
                    
        otherBar = qt.QHButtonGroup(self.popupMenu)
        otherBar.setFlat(True)
        otherBar.setInsideMargin(5)
        moreButton = qt.QToolButton(otherBar)
        moreButton.setTextLabel("More color ...")
        moreButton.setUsesTextLabel(True)
        moreButton.setAutoRaise(True)
        self.connect(moreButton, qt.SIGNAL("clicked()"), self.selectColor)
                        
        self.popupMenu.insertItem(colorBar)
        self.popupMenu.insertItem(otherBar)
        
    def selectSimpleColor(self, ind):
        """
        
        """
        self.selectedColor = qt.QColor(self.simpleColor[ind])
        self.setIconColor(self.selectedColor)
        self.emit(qt.PYSIGNAL("colorSelected"), (self.selectedColor,))
        self.popupMenu.hide()
        
    def selectColor(self):
        """
        
        """
        color = qt.QColorDialog.getColor(self.selectedColor, self)
        
        if color is not None:
            self.selectedColor = color
            self.setIconColor(self.selectedColor)
            self.emit(qt.PYSIGNAL("colorSelected"), (self.selectedColor,))      
        
        self.popupMenu.hide()
    
    def setIconColor(self, color):
        """
        internal method to change the color of the icon
        """
        r = color.red()
        g = color.green()
        b = color.blue()
        paintbrush_xpm[8] = "j  c #%02x%02x%02x"%(r, g, b)
        self.setPixmap(qt.QPixmap(paintbrush_xpm))
          
class ColorToolMenu(qt.QPopupMenu):
    """
    """
    def __init__(self, parent=None, name=None):
        """
        """
        qt.QPopupMenu.__init__(self, parent, name)
        
        self.simpleColor = [qt.Qt.black,
                            qt.Qt.white,
                            qt.Qt.red,
                            qt.Qt.green,
                            qt.Qt.blue,
                            qt.Qt.yellow]
        self.simpleName = ["black", "white", "red", "green", "blue", "yellow"]
        self.selectedColor = qt.QColor(qt.Qt.black)
        
        self.setIconColor(self.selectedColor)

        self.itemId = {}
        for i  in range(len(self.simpleColor)):
            itemId = self.insertItem(qt.QString(self.simpleName[i]))
            self.itemId[itemId] = self.simpleColor[i]
        
        self.connect(self, qt.SIGNAL("activated(int )"), self.selectSimpleColor)
                    
        self.insertItem(qt.QString("More color ..."), self.selectColor)
        
    def selectSimpleColor(self, item):
        """
        """
        if self.itemId.has_key(item):
            self.selectedColor = qt.QColor(self.itemId[item])
            self.setIconColor(self.selectedColor)
            self.emit(qt.PYSIGNAL("colorSelected"), (self.selectedColor,))
            self.hide()
        
    def selectColor(self):
        """
        """
        color = qt.QColorDialog.getColor(self.selectedColor, self)
        
        if color is not None:
            self.selectedColor = color
            self.setIconColor(self.selectedColor)
            self.emit(qt.PYSIGNAL("colorSelected"), (self.selectedColor,))      
        
        self.hide()
    
    def setIconColor(self, color):
        """
        """
        r = color.red()
        g = color.green()
        b = color.blue()
        paintbrush_xpm[8] = "j  c #%02x%02x%02x"%(r, g, b)
        self.iconSet = qt.QIconSet(qt.QPixmap(paintbrush_xpm))
      

 
################################################################################
###################    TEST -- QubColorToolButton -- TEST   ####################
################################################################################
import sys

class QubMain(qt.QMainWindow):
    """
    Test class
    """
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
        
        self.qubColorToolButton = QubColorToolButton (self )
                    
        hlayout.addWidget(self.qubColorToolButton)
    
        self.setCentralWidget(container)
        
##  MAIN   
if  __name__ == '__main__':
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubMain()
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
