import sys

import qt
import qtcanvas

__revision__="$Revision$"

# Gilles.Berruyer@esrf.fr
# Cyril.Guilloud@esrf.fr
# 2005

# BUGS

# TODO

##############################################################################
##############################################################################
#######################       QubWidgetSet      ##############################
##############################################################################
##############################################################################

ok_xpm = [
"16 16 6 1",
"  c black",
". c #008000",
"X c #00C000",
"o c green",
"O c #C0C0C0",
"+ c None",
"++++++++++++++++",
"++++++++++++++++",
"++++++++++++++++",
"++++++++++++++++",
"++++++++++++++++",
"+++++++++++oo+++",
"++++++++++oX.+++",
"++oo+++++oX. +++",
"++oXo+++oX. ++++",
"++oXXo+oX. +++++",
"++ .XXoX. ++++++",
"+++ .XX. +++++++",
"++++ .. ++++++++",
"+++++  +++++++++",
"++++++++++++++++",
"++++++++++++++++"]

cancel_xpm = [
"16 16 5 1",
"  c #800000",
". c #C00000",
"X c red",
"o c #C0C0C0",
"O c None",
"OOOOOOOOOOOOOOOO",
"OOOOOOOOOOOOOOOO",
"OOOOOOOOOOOXOOOO",
"OOOXXOOOOOX..OOO",
"OOX..XXOOX..  OO",
"OOO ...XX..  OOO",
"OOOOO ....  OOOO",
"OOOOOOX..X OOOOO",
"OOOOOX...X OOOOO",
"OOOOX.  ..XOOOOO",
"OOOOX. OO.. OOOO",
"OOOX. OOOO..OOOO",
"OOOX  OOOOO. OOO",
"OOOX OOOOOOO OOO",
"OOOO OOOOOOOOOOO",
"OOOOOOOOOOOOOOOO"]


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

###############################################################################
##################           QubColorToolButton                   #############
###############################################################################
# berruyer@esrf.fr
class QubColorToolButton(qt.QToolButton):
    """
    The QubColorToolButton provides a pushButton usable as a color selector.
    Its icon represents a paint tool with a color sample dynamicly updated
    according to the selected color.
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
    
    def setColor(self, color):
        try:
            self.setIconColor(color)
        except:
            self.setIconColor(self.selectedColor)
        else:
            self.selectedColor = color
            
    def setIconColor(self, color):
        """
        internal method to change the color of the icon
        """
        r = color.red()
        g = color.green()
        b = color.blue()
        paintbrush_xpm[8] = "j  c #%02x%02x%02x"%(r, g, b)
        self.setPixmap(qt.QPixmap(paintbrush_xpm))
          
class QubColorToolMenu(qt.QPopupMenu):
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
    
    def setColor(self, color):
        try:
            self.setIconColor(color)
        except:
            self.setIconColor(self.selectedColor)
        else:
            self.selectedColor = color
    
    def setIconColor(self, color):
        """
        """
        r = color.red()
        g = color.green()
        b = color.blue()
        paintbrush_xpm[8] = "j  c #%02x%02x%02x"%(r, g, b)
        self.iconSet = qt.QIconSet(qt.QPixmap(paintbrush_xpm))
      

################################################################################
####################                                          ##################
####################           QubCheckedText                 ##################
####################                                          ##################
################################################################################
class QubSlider(qt.QSlider):
    """
    add "sliderChanged" signal to the QSlider widet.
    send like the "valueChanged" callback but not during the drag
    of the slider cursor
    """
    def __init__(self, *args):
        qt.QSlider.__init__(self, *args)
        
        self.__sliderState = "Released"

        self.connect(self, qt.SIGNAL("sliderPressed()"), self.__sliderPressed)
        self.connect(self, qt.SIGNAL("valueChanged(int)"), self.__valueChanged)
        self.connect(self, qt.SIGNAL("sliderReleased()"), self.__sliderReleased)
        
    def __sliderPressed(self):
        self.__sliderState = "Pressed"
    
    def __valueChanged(self, val):
        if self.__sliderState != "Pressed":
            self.emit(qt.PYSIGNAL("sliderChanged"), (val,))
            
    def __sliderReleased(self):
        self.__sliderState = "Released"
        val = self.value()
        self.emit(qt.PYSIGNAL("sliderChanged"), (val,))

################################################################################
####################           QubCheckedText                 ##################
################################################################################
# guilloud@esrf.fr
class QubCheckedText(qt.QWidget):
    """
    QubCheckedText is a controled line edit widget. When the text is
    changed, background color change and a validation action is
    needed. Is ok is clicked the value is updated and a signal emited. if
    cancel is clicked, the value remain unchanged.
            ________________________ ___    
    Label: |                        |V|X|
           |________________________|_|_|

    - "textChanged(const QString &)" Signal is emited when the value of the
    QubCheckedText lineEdit value change (ie on ok click).
    """
    
    def __init__(self, parent=None, name=None, editText=None, labelText=None,
                 smallFlag=False ):

        qt.QWidget.__init__(self, parent, name)

        self._refValue = editText
        self.defaultColor = qt.QColor("white")
        self.alteredColor = qt.QColor(204,102,102) # sort of salmon color
        self._small = smallFlag

        hlayout = qt.QHBoxLayout(self, 0, 0 , "QCTlayout")

        self.label = qt.QLabel(labelText, self, "QCTlabel")
        
        # Ok button (with a green mark)
        okButton = qt.QToolButton(self, "ok button")
        okButton.setPixmap(qt.QPixmap(ok_xpm))
        okButton.setAutoRaise(True)

        # Cancel button (with a red cross)
        cancelButton = qt.QToolButton(self, "cancel button")
        cancelButton.setPixmap(qt.QPixmap(cancel_xpm))
        cancelButton.setAutoRaise(True)

        # controlled lineEdit
        self.lineEdit = qt.QLineEdit(self)
        self.lineEdit.setText(self._refValue)
        
        hlayout.addWidget (self.label) 
        hlayout.addWidget (self.lineEdit)

        self.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Fixed,
                                          qt.QSizePolicy.Fixed))

        # position of buttons (side by side or up and down)
        if self._small:
            vvlayout = qt.QVBoxLayout(hlayout)
            t = self.lineEdit.size().height()/ 2

            vvlayout.setResizeMode(qt.QLayout.Minimum)
            hlayout.setResizeMode(qt.QLayout.Minimum)

            okButton.setFixedSize(t,t)
            cancelButton.setFixedSize(t,t)

            vvlayout.addWidget (okButton)
            vvlayout.addWidget (cancelButton)
        else:
            hlayout.addWidget (okButton)
            hlayout.addWidget (cancelButton)
            
        # binding signals
        qt.QObject.connect(okButton, qt.SIGNAL("clicked()"),
                           self._onOkClicked)
        
        qt.QObject.connect(cancelButton, qt.SIGNAL("clicked()"),
                           self._onCancelClicked)
        
        qt.QObject.connect(self.lineEdit,
                           qt.SIGNAL("textChanged(const QString &)"),
                           self._onTextChanged)

    def _onTextChanged(self, newText):
        self.lineEdit.setPaletteBackgroundColor(self.alteredColor)
        
    def _onOkClicked(self):
        self._refValue = self.lineEdit.text()
        self.lineEdit.setPaletteBackgroundColor(self.defaultColor)
        self.emit ( qt.PYSIGNAL("textChanged(const QString &)"),
                    (qt.QString(self._refValue),)
                  )
        
    def _onCancelClicked(self):
        self.lineEdit.setText(self._refValue)
        self.lineEdit.setPaletteBackgroundColor(self.defaultColor)
       
    def value(self):
        """
        return the value of the lineEdit
        """
        return self._refValue

    def sizeHint(self):
        """
        Return prefered size.
        """
        return qt.QSize(800,30)

    def setLabelText(self, text):
        self.label.setText(text)
        

 
   
###############################################################################
###  QUBWIDGETSET TEST 
###############################################################################

class QubWidgetTest(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        container = qt.QWidget(self)
        
        vlayout = qt.QVBoxLayout(container)

        ## test for QubCheckedText ############################################
        self.refText = qt.QLineEdit(container, "qleref")
        self.refText.setReadOnly(True)
        
        tstQCT = QubCheckedText(container, "test QCT",
                                "init String", "ma val:", True)

        self.refText.setText(tstQCT.value())
        
        vlayout.addWidget(self.refText)
        vlayout.addWidget(tstQCT)

        ## test for QubColorToolButton ########################################
        self.qubColorToolButton = QubColorToolButton (container)
        self.qubColorToolButton.setFixedSize(40,30)
        vlayout.addWidget(self.qubColorToolButton)


        self.setCentralWidget(container)
        
        qt.QObject.connect(tstQCT, qt.PYSIGNAL("textChanged(const QString &)"),
                           self.chRV)

        qt.QObject.connect(self.qubColorToolButton,
                           qt.PYSIGNAL("colorSelected"),
                           self.chColor)



    def chRV(self, val):
        self.refText.setText(val)

    def chColor(self, color):
        self.refText.setPaletteBackgroundColor(color)
        
if __name__=="__main__":
    app = qt.QApplication(sys.argv)
    
    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                       app, qt.SLOT("quit()"))

    window = QubWidgetTest()
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()



