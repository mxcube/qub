import os
import sys
import qt
##@defgroup howto Howto
#
##@defgroup howto_imageDisplay display an image
##@ingroup howto
#The simplest way to display a data image with Qub is to use Qub::Widget::QubDataDisplay.
#
#<b>Simple Example:</b>\n
#import qt\n
#from Qub.Widget.QubDataDisplay import QubDataDisplay\n
#app = qt.QApplication([])\n
# - SHM : display = QubDataDisplay(data='spec_version:array_name')
# - EdfFile: display = QubDataDisplay(data='full_path_to_edf_file')
#
#app.setMainWidget(display)\n
#display.show()\n
#app.exec_loop()
#

from Qub.Data.Source.QubADSC import QubADSC
from Qub.Data.Source.QubMarCCD import QubMarCCD

from Qub.Widget.QubDataDisplay import QubDataDisplay
##@brief this simple class display Mar or ADSC image
#
#@ingroup howto_imageDisplay
#to try it type -> python QubDataDisplayWithPlugIns [filelist]
class QubDataDisplayWithPlugIns(qt.QVBox) :
    ##@brief constructor
    #
    #In this init, we check if the file list passed to the class is valid
    #ie: If we can open the file and if we know the file format (Mar or ADSC)
    #then we display the first image
    def __init__(self) :
        qt.QVBox.__init__(self)
        self.anIndex = 0
        self.readableImageFileName = []
        self.pluginsList = [QubADSC(),QubMarCCD()]
        ##Qt init
        self.hbox = qt.QHBox(self)
        self.dataDisplay = QubDataDisplay(parent = self)

        self.pButton = qt.QPushButton(self.hbox)
        self.pButton.setText('previous')
        qt.QObject.connect(self.pButton,qt.SIGNAL("clicked()"),self._previousImage)

        self.nButton = qt.QPushButton(self.hbox)
        self.nButton.setText('next')
        qt.QObject.connect(self.nButton,qt.SIGNAL("clicked()"),self._nextImage)

        ## Test validity of file
        for filename in sys.argv[1:] :
            try:
                fd = file(filename)
                for plugin in self.pluginsList:
                    try:
                        reader = plugin.readHandler(fd)
                        self.readableImageFileName.append(filename)
                        break
                    except: pass                # Format not recognised
                fd.close()
            except :
                import traceback
                traceback.print_exc()

        self._nextOrPreviousImage(0)

    ##@brief go to next or previous image
    #@param inc
    # - if inc is 1 -> next image
    # - else if inc is -1 -> previous image
    #
    def _nextOrPreviousImage(self,inc) :
        self.anIndex += inc
        if self.anIndex >= len(self.readableImageFileName) : self.anIndex = 0
        elif self.anIndex < 0: self.anIndex = len(self.readableImageFileName) - 1
        fullPath = self.readableImageFileName[self.anIndex]
        fd = file(fullPath)
        for plugin in self.pluginsList:
            try:
                reader = plugin.readHandler(fd)
                data = reader.get(0)
                info = reader.info(0)
                self.dataDisplay.setData(data)
                self.dataDisplay.setInfo(info)
                self.setCaption(os.path.split(fullPath)[1])
            except: pass

    ##@brief display next Image
    #
    def _nextImage(self) :
        self._nextOrPreviousImage(1)

    ##@brief display previous Image
    def _previousImage(self) :
        self._nextOrPreviousImage(-1)

if __name__ == "__main__":
    app = qt.QApplication(sys.argv)
    display = QubDataDisplayWithPlugIns()
    app.setMainWidget(display)
    display.show()
    app.exec_loop()
