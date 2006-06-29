import qt
import sys

from Qub.Widget.QubView import QubView

from Qub.Widget.QubImage import QubImage


################################################################################
####################               QubImageView             ####################
################################################################################
class QubImageView(QubView):
    """
    The QubImageView allows to display QPixmap and put behavior
    (zoom,selection,print ....) on it using QubAction.
    It inherits QubView to get the window structure (toolbar/contextmenu,
    view, statusbar).
    It creates a instance of QubImage as QubView view.  
    """
    def __init__(self,
                parent=None, name=None, pixmap=None, actions=None,
                scrollMode=None, useThread=0, flags=qt.Qt.WDestructiveClose):
        QubView.__init__(self, parent, name, flags)
        
        widget = QubImage(self, name, pixmap, useThread)
        
        self.setView(widget)
        
        if actions is not None:
            self.addAction(actions)
            
    def setPixmap(self, pixmap):
        """
        Set the Qpixmap to be displayed and tells the QubImage widget to
        display it
        """
        view = self.view()
        if view is not None and pixmap:
            self.view().setPixmap(pixmap)
    
    def setScrollbarMode(self, mode):
        """
        Change the scroll bar policy of the view (QubImage)
        accepted values:
            "Auto":         Scrollbars are shown if needed
            "AlwaysOff" :   Scrollbars are never displayed
            "Fit2Screen" :  Displayed pixmap size follow CanvasView size 
                            keeping data pixmap ratio
            "FullScreen":   Displayed pixmap size is CanvasView size without 
                            keeping data pixmap ratio
        """
        view = self.view()
        if view is not None and \
            mode in ["Auto","AlwaysOff","Fit2Screen","FullScreen"]:
            view.setScrollbarMode(mode)
            
    def setThread(self, useThread):
        """
        Used by the view (QubImage) to determine if thread must be used or not
        to build the dislpayed bckPixmap
        Thread is used mainly if the pixmap is updated often (shared memory 
        or ccd device servers)
        """
        view = self.view()
        if view is not None:
            view.setThread(useThread)
            
    def closeWidget(self):
        print "CloseWidget ImageView"
        self.view().closeWidget()

                      
################################################################################
####################    TEST -- QubViewActionTest -- TEST   ####################
################################################################################
from Qub.Data.Plug.QubPlug import QubPlug
import Numeric

class QubShm2Pixmap(QubPlug) :
    def __init__(self,aQubImageView,timeout = 1000) :
        QubPlug.__init__(self,timeout)
        self.__imageView = aQubImageView
        
    def update(self,specversion,specshm,data) :
        (image_str,size,minmax) = spslut.transform(data,
                                                   (1,0), (spslut.LINEAR, 3.0),
                                                   "BGRX", spslut.GREYSCALE,1,(0,255))
        image = qt.QImage(image_str,size[0],size[1],32,None,0,
                          qt.QImage.IgnoreEndian)
        
        self.__imageView.setPixmap(qt.QPixmap(image))

class QubMain(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        pixmap = qt.QPixmap(file)
        
        actions = []
        action = QubRectangleSelection(place="toolbar", show=1, group="selection")
        actions.append(action)
        action = QubLineSelection(place="statusbar",show=1,group="selection")
        actions.append(action)
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
        
        self.qubImageView=QubImageView(container, "Test QubImageView",
                                       pixmap, actions)
                    
        hlayout.addWidget(self.qubImageView)
    
        self.setCentralWidget(container)
               
##  MAIN   
if  __name__ == '__main__':
    from QubActionSet import QubRectangleSelection,QubLineSelection
    from Qub.Widget.QubProfiler import QubProfiler
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    if len(sys.argv) < 2:
##        print "Give an image file name as argument"
##        sys.exit(1)
        import sps,spslut
        from Qub.Data.Source.QubSpecSource import getSpecVersions
        SpecVers = getSpecVersions()
        sebSpec = SpecVers.getObjects('seb')
        if(sebSpec) :
            imgArray = sebSpec.getObjects('image')
            if(imgArray) :
                window = qt.QMainWindow()
                layout = qt.QVBoxLayout(window)
                imgView = QubImageView(window,"Test")
                layout.addWidget(imgView)
                plug = QubShm2Pixmap(imgView)
                imgArray.plug(plug)
            else :
                print "Array not found"
        else :
            print "Spec version not found"
    else:
        window = QubMain(file = sys.argv[1])
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
