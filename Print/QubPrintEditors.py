import sys
import qt
from Qub.Widget.QubColorToolButton import QubColorToolButton

__revision__="$Revision$"

class QubTitleEditor(qt.QDialog):
    """
    This dialog window allow to define top and bottom texts (fonts and
    colors) to comment items put in a PrintPreviewCanvas
    """
    def __init__(self, topText = None, bottomText = None, \
                 parent = None, name = "TextEditor", modal = 1, fl = 0): 
        """
        Constructor method
        topText .. : text appearing in the top of the item (title ?)
        bottomText : text appearing in the bottom of the item (legend ?)
        parent ... : 
        name ..... : name of the dialog widget
        modal .... : is the dialog modal ?
        fl ....... : qt flag
        """
        qt.QDialog.__init__(self, parent, name, modal, fl)
        self.setCaption(name)

        # placing
        layout = qt.QVBoxLayout(self)
        gridg  = qt.QHGroupBox(self)
        
        gridw  = qt.QWidget(gridg)
        grid   = qt.QGridLayout(gridw, 2, 4)

        grid.setColStretch(1, 4)

        # Top Text
        topLabel     = qt.QLabel("Top Text", gridw)   # self. ?
        self.topText = qt.QLineEdit(gridw)
        
        if topText is not None:
            self.topText.setText(topText[0])
            self.topFont  = topText[1]
            self.topColor = topText[2]
        else:
            self.topFont  = self.topText.font()
            self.topColor = self.topText.paletteForegroundColor()

        topFontButton = qt.QPushButton("Font" , gridw)
        self.topColorButton = QubColorToolButton (gridw)
        self.topColorButton.setAutoRaise(False)
        self.topColorButton.setIconColor(self.topColor)
        
        self.connect(topFontButton , qt.SIGNAL("clicked()"), self.__topFont)
        self.connect(self.topColorButton, qt.PYSIGNAL("colorSelected"),
                     self.__setTopColor)
        
        grid.addWidget(topLabel, 0, 0)
        grid.addWidget(self.topText, 0, 1)
        grid.addWidget(topFontButton, 0, 2)
        grid.addWidget(self.topColorButton, 0, 3)
        

        # Bottom Text
        botLabel     = qt.QLabel("Bottom Text", gridw)
        self.botText = qt.QLineEdit(gridw)

        if bottomText is not None:
            self.botText.setText(bottomText[0])
            self.botFont  = bottomText[1]
            self.botColor = bottomText[2]
        else:
            self.botFont  = self.botText.font()
            self.botColor = self.botText.paletteForegroundColor()

        botFontButton = qt.QPushButton("Font", gridw)
        self.botColorButton = QubColorToolButton (gridw)
        self.botColorButton.setAutoRaise(False)
        self.botColorButton.setIconColor(self.botColor)
            
        self.connect(botFontButton,  qt.SIGNAL("clicked()"), self.__botFont)
        self.connect(self.botColorButton, qt.PYSIGNAL("colorSelected"),
                     self.__setBotColor)

        grid.addWidget(botLabel, 1, 0)
        grid.addWidget(self.botText, 1, 1)
        grid.addWidget(botFontButton, 1, 2)
        grid.addWidget(self.botColorButton, 1, 3)

        # dialog buttons
        butw = qt.QHButtonGroup(self)
        cancelBut = qt.QPushButton("Cancel", butw)
        okBut     = qt.QPushButton("OK", butw)
        okBut.setDefault(1)
        self.connect(cancelBut, qt.SIGNAL("clicked()"), self.reject)
        self.connect(okBut,     qt.SIGNAL("clicked()"), self.accept)

        layout.addWidget(gridg)
        layout.addWidget(butw)

    def __topFont(self):
        """
        set the Font of the top label
        """
        font = qt.QFontDialog.getFont(self.topFont)
        if font[1]:
            self.topFont = font[0]

    def __setTopColor(self):
        """
        set the Color of the top label
        """
        self.topColor = self.topColorButton.selectedColor

    def __setBotColor(self):
        """
        set the Color of the bottom label
        """
        self.botColor = self.botColorButton.selectedColor

    def __botFont(self):
        """
        set the Font of the bottom label
        """
        font = qt.QFontDialog.getFont(self.botFont)
        if font[1]:
            self.botFont = font[0]

    def getTopText(self):
        """
        return the text of the Top Label
        """
        text = str(self.topText.text())
        if len(text):
            return (text, self.topFont, self.topColor)
        else:    return (None, None, None)

    def getBottomText(self):
        """
        return the text of the bottom Label
        """
        text = str(self.botText.text())
        if len(text):
            return (text, self.botFont, self.botColor)
        else:    return (None, None, None)


      
################################################################################
####################    TEST -- QUbPrintEditors -- TEST   ######################
################################################################################
        
class QubMain(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)

        l1 = qt.QLabel (container)
        l2 = qt.QLabel (container)
        qub = QubTitleEditor(("titi", qt.QFont("Times"), qt.QColor("red")),
                             ("toto", qt.QFont("Times"), qt.QColor("blue")),
                             None)
                                       
        qub.show()
        hlayout.addWidget(l1)
        hlayout.addWidget(l2)
        self.setCentralWidget(container)

        self.show()
        
        qub.exec_loop()
        
        if qub.result() == qt.QDialog.Accepted:
            topText = qub.getTopText()
            l1.setText(topText[0] ) #, topText[1], topText[2])
            bottomText = qub.getBottomText()
            l2.setText(bottomText[0] ) #, bottomText[1], bottomText[2])
            self.update()

               
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

