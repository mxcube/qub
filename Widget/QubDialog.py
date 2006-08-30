###############################################################################
###############################################################################
####################                                       ####################
####################         Miscallenous Dialog           ####################
####################                                       ####################
###############################################################################
###############################################################################
import qt
import os.path
from Qub.Objects.QubPixmapDisplay import QubPixmapDisplay
from Qub.Objects.QubPixmapDisplay import QubPixmapZoomPlug
from Qub.Icons.QubIcons import loadIcon

####################################################################
##########                                                ##########
##########               QubSaveImageDialog               ##########
##########                                                ##########
####################################################################
class QubSaveImageDialog(qt.QDialog):
    class _Image2Pixmap(QubPixmapZoomPlug) :
        def __init__(self,receiver,buttonFile) :
            QubPixmapZoomPlug.__init__(self,receiver)
            self.__inPollFlag = False
            self.__lastImage = None
            self.__buttonFile = buttonFile
            
        def setPixmap(self,pixmap,image) :
            self.__inPollFlag = False
            QubPixmapZoomPlug.setPixmap(self,pixmap,image)
            if not self.__buttonFile.isEnabled() :
                self.__buttonFile.setEnabled(True)
            self.__lastImage = image
            return True # One Shot 

        def refresh(self) :
            if self._mgr is not None and not self.__inPollFlag :
                self.__inPollFlag = True
                self._mgr.plug(self)
                self._mgr.refresh()

        def setInPoll(self) :
            self.__inPollFlag = True
            
        def getImage(self) :
            return self.__lastImage
    """
    Dialog to take a snapshot of the falcon via device server
    and to save it in different format
    "parent" is supposed to be the brick itself in order to acces its
    "pixmap" attribute
    """
    def __init__(self,parent = None,name = '') :
        qt.QDialog.__init__(self, parent, name)
        
        self.resize(350, 350)
        
        self.__parent = parent

        vlayout = qt.QVBoxLayout(self)
        vlayout.setMargin(10)
        
        self.__ImView = QubPixmapDisplay(self)
        self.__ImView.setScrollbarMode("Fit2Screen")

        vlayout.addWidget(self.__ImView)
       
        iconSet = qt.QIconSet(loadIcon("fileopen.png"))
        self.__buttonFile = qt.QPushButton(iconSet, "", self)
        self.__buttonFile.setEnabled(False)
        self.connect(self.__buttonFile, qt.SIGNAL("clicked()"), 
                        self.openFile)
        self.__imagePlug = QubSaveImageDialog._Image2Pixmap(self.__ImView,self.__buttonFile)
                        
        iconSet = qt.QIconSet(loadIcon("snapshot.png"))
        self.__snapButton = qt.QPushButton(iconSet, "", self)
        self.connect(self.__snapButton, qt.SIGNAL("clicked()"),self.__imagePlug.refresh)
           
        hlayout = qt.QHBoxLayout(vlayout)
        hlayout.addWidget(self.__snapButton)
        hlayout.addSpacing(10)
        hlayout.addWidget(self.__buttonFile)

    def openFile(self):
        filename = qt.QFileDialog.getSaveFileName( ".", "*;;*.png;;*.jpg", self, "selectFile",
                                                    "Choose a filename to save under")
        

        if filename :
            (radix, ext) = os.path.splitext(str(filename))

            image = self.__imagePlug.getImage()

            if ext.lower() == ".png" :
                image.save(filename, "PNG")
            elif ext.lower() == ".jpeg" or ext.lower() ==".jpg" :
                image.save(filename, "JPEG")
            else :
                dialog = qt.QErrorMessage(self.__parent)
                dialog.message('File format not managed')
                dialog.exec_loop()
            
    def setImage2Pixmap(self,image2pixmap) :
        self.__imagePlug.setInPoll()
        image2pixmap.plug(self.__imagePlug)

    def refresh(self) :
        self.__imagePlug.refresh()
