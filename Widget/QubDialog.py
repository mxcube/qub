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
from Qub.Widget.QubWidgetSet import QubSlider
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


####################################################################
##########                                                ##########
##########        QubBrightnessContrastDialog             ##########
##########                                                ##########
####################################################################        
class QubBrightnessContrastDialog(qt.QDialog):
    def __init__(self, parent):
        qt.QDialog.__init__(self, parent)
        
        """
        variables
        """
        self.__camera = None
        
        self.__contrast = 0
        self.__contrastMin = 0
        self.__contrastMax = 200
        
        self.__brightness = 0
        self.__brightnessMin = 0
        self.__brightnessMax = 255
        
        """
        widget
        """        
        vlayout = qt.QVBoxLayout(self)
        vlayout.setMargin(10)
        
        """
        contrast updater
        """
        self.contrastLabel = qt.QLabel("Contrast:", self)
        vlayout.addWidget(self.contrastLabel)
       
        self.contrastSlider = QubSlider(self.__contrastMin,
                                        self.__contrastMax,
                                        10, self.__contrast,
                                        qt.Qt.Horizontal,self)
        self.connect(self.contrastSlider, qt.PYSIGNAL("sliderChanged"),
                     self.setContrast)
        vlayout.addWidget(self.contrastSlider)
        
        vlayout.addSpacing(10)
                 
        """
        brightness updater
        """
        self.brightLabel = qt.QLabel("Brightness:", self)
        vlayout.addWidget(self.brightLabel)
        
        self.brightnessSlider = QubSlider(self.__brightnessMin,
                                           self.__brightnessMax, 
                                           10, self.__brightness,
                                           qt.Qt.Horizontal, self)
        self.connect(self.brightnessSlider, qt.PYSIGNAL("sliderChanged"),
                     self.setBrightness)
        vlayout.addWidget(self.brightnessSlider)

    def setContrastLimits(self, contrastMin, contrastMax):
        self.__contrastMin = contrastMin
        self.__contrastMax = contrastMax
        
        self.setContrast(self.__contrast)
        self.contrastChanged(self.__contrast)
        
    def setContrast(self, contrast):
        self.__contrast = contrast
        if contrast < self.__contrastMin:
            self.__contrast = self.__contrastMin
        if contrast > self.__contrastMax:
            self.__contrast = self.__contrastMax
            
        if self.__camera is not None:
            self.__camera.setContrast(self.__contrast)
                    
    def contrastChanged(self, contrast):
        self.__contrast = contrast
        if contrast < self.__contrastMin:
            self.__contrast = self.__contrastMin
        if contrast > self.__contrastMax:
            self.__contrast = self.__contrastMax

        self.contrastSlider.setValue(self.__contrast)

    def setBrightnessLimits(self, brightnessMin, brightnessMax):
        self.__brightnessMin = brightnessMin
        self.__brightnessMax = brightnessMax
        
        self.setBrightness(self.__brightness)
        self.BrightnessChanged(self.__brightness)

    def setBrightness(self, brightness):
        self.__brightness = brightness
        if brightness < self.__brightnessMin:
            self.__brightness = self.__brightnessMin
        if brightness > self.__brightnessMax:
            self.__brightness = self.__brightnessMax
            
        if self.__camera is not None:
            self.__camera.setBrightness(self.__brightness)
        
    def brightnessChanged(self, brightness):
        self.__brightness = brightness
        if brightness < self.__brightnessMin:
            self.__brightness = self.__brightnessMin
        if brightness > self.__brightnessMax:
            self.__brightness = self.__brightnessMax
            
        self.brightnessSlider.setValue(self.__brightness)
            
    def setCamera(self, camera):
        self.__camera = camera
        
        if self.__camera is not None:
            self.contrastChanged(self.__camera.getContrast())
            self.brightnessChanged(self.__camera.getBrightness())
    
    def show(self):
        if self.__camera is not None:
            self.contrastChanged(self.__camera.getContrast())
            self.brightnessChanged(self.__camera.getBrightness())
        
        qt.QDialog.show(self)
        
