import sys

import qt

__revision__="$Revision$"

# Cyril.Guilloud@esrf.fr
# december 2005

# BUGS

# TODO


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

class QubCheckedText(qt.QWidget):
    """
    QubCheckedText is a controled line edit widget. When the text is
    changed, background color change and a validation action is
    needed. Is ok is clicked the velue is updated. if cancel is
    clicked, the value remain unchanged.
    """
    
    def __init__(self, parent=None, name=None, contents=None, text=None,
                 smallFlag=False ):

        qt.QWidget.__init__(self, parent, name)

        self._refValue = contents
        self.defaultColor = qt.QColor("white")
        self.alteredColor = qt.QColor("red")
        self._small = smallFlag

        hlayout = qt.QHBoxLayout(self, 0, 0 , "lay")

        self.label = qt.QLabel(text, self, "label1")
        
        okButton = qt.QToolButton(self, "ok button")
        okButton.setPixmap(qt.QPixmap(ok_xpm))
        okButton.setAutoRaise(True)
        
        cancelButton = qt.QToolButton(self, "cancel button")
        cancelButton.setPixmap(qt.QPixmap(cancel_xpm))
        cancelButton.setAutoRaise(True)
        
        self.lineEdit = qt.QLineEdit(self)
        self.lineEdit.setText(self._refValue)
        
        hlayout.addWidget (self.label) 
        hlayout.addWidget (self.lineEdit)

        # use this if not widget is not in a layout
        self.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.Fixed,
                                          qt.QSizePolicy.Fixed))

        if self._small:
            vvlayout = qt.QVBoxLayout(hlayout)
            t = self.lineEdit.size().height()/ 2

            vvlayout.setResizeMode(qt.QLayout.Minimum)
            hlayout.setResizeMode(qt.QLayout.Minimum)

            okButton.setFixedSize(t,t)
            print "t=", t
            cancelButton.setFixedSize(t,t)
            vvlayout.addWidget (okButton)
            vvlayout.addWidget (cancelButton)
        else:
            hlayout.addWidget (okButton)
            hlayout.addWidget (cancelButton)
            
        # we bind signals
        qt.QObject.connect(okButton, qt.SIGNAL("clicked()"),
                           self._onOkClicked)
        
        qt.QObject.connect(cancelButton, qt.SIGNAL("clicked()"),
                           self._onCancelClicked)
        
        qt.QObject.connect(self.lineEdit,
                           qt.SIGNAL("textChanged(const QString &)"),
                           self._onTextChanged)

    def _onTextChanged(self, newText):
        print "on a change' la value", newText
        self.lineEdit.setPaletteBackgroundColor(self.alteredColor)
        
    def _onOkClicked(self):
        print "on a clicke sur ok"
        self._refValue = self.lineEdit.text()
        self.lineEdit.setPaletteBackgroundColor(self.defaultColor)
        self.emit ( qt.PYSIGNAL("textChanged(qt.QString &)"),
                    (qt.QString(self._refValue),)
                  )
        
    def _onCancelClicked(self):
        print "on a clicke' sur cancel"
        self.lineEdit.setText(self._refValue)
        self.lineEdit.setPaletteBackgroundColor(self.defaultColor)
       
    def value(self):
        """
        return the value of the lineEdit
        """
        return self._refValue

    def sizeHint(self):
        return qt.QSize(800,30)
    
#########################################################################
###  QUBWIDGETSET TEST 
#########################################################################

class QubWidgetTest(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        container = qt.QWidget(self)
        
        vlayout = qt.QVBoxLayout(container)

        self.refText = qt.QLineEdit(container, "qleref")
        self.refText.setReadOnly(True)
        
        tstQCT = QubCheckedText(container, "test QCT",
                                "init String", "ma val:", True)

        self.refText.setText(tstQCT.value())
        
        vlayout.addWidget(self.refText)
        vlayout.addWidget(tstQCT)

        self.setCentralWidget(container)

        qt.QObject.connect(tstQCT, qt.PYSIGNAL("textChanged(qt.QString &)"),
                           self.chRV)

    def chRV(self, val):
        self.refText.setText(val)

        
if __name__=="__main__":
    app = qt.QApplication(sys.argv)
    
    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                       app, qt.SLOT("quit()"))

    window = QubWidgetTest()
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()



