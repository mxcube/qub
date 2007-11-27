import os.path
import qt
if __name__ == "__main__" :
    a = qt.QApplication([])

from Qub.Objects.QubPixmapDisplayView import QubPixmapDisplayView
from Qub.Objects.QubPixmapDisplay import QubPixmapZoomPlug
from Qub.Objects.QubImage2Pixmap import QubImage2Pixmap

from Qub.Widget.QubActionSet import QubZoomListAction
from Qub.Widget.QubActionSet import QubZoomAction
from Qub.Widget.QubActionSet import QubPrintPreviewAction

from Qub.Print.QubPrintPreview import getPrintPreviewDialog

class QubImageDisplay(qt.QWidget) :
    def __init__(self,parent = None,imagePath = None,name='',**keys) :
        qt.QWidget.__init__(self,parent,name,qt.Qt.WDestructiveClose)
        layout = qt.QHBoxLayout(self)
        self.__mainView = QubPixmapDisplayView(parent=self)
        self.__mainView.setScrollbarMode('Auto')
        layout.addWidget(self.__mainView)

        self.__mainPlug = QubPixmapZoomPlug(self.__mainView)
        self.__image2Pixmap = QubImage2Pixmap()
        self.__image2Pixmap.plug(self.__mainPlug)
        self.putImagePath(imagePath)

        actions = []
        
                      ####### ZOOM LIST #######
        zoomActionList = QubZoomListAction(place = "toolbar",
                                           initZoom = 1,zoomValList = [0.25,0.5,0.75,1,1.5,2],
                                           show = 1,group = "image")
        actions.append(zoomActionList)
                     ####### ZOOM Action #######
        zoomFitOrFill = QubZoomAction(place = "toolbar",group = "image")
        actions.append(zoomFitOrFill)
                   ####### LINK ZOOM ACTION #######
        zoomFitOrFill.setList(zoomActionList)
        zoomActionList.setActionZoomMode(zoomFitOrFill)

                     ####### PRINT ACTION #######
        printAction = QubPrintPreviewAction(name="print",group="admin")
        printAction.previewConnect(getPrintPreviewDialog())
        actions.append(printAction)

        self.__mainView.addAction(actions)

    def putImagePath(self,imagePath) :
        if imagePath:
            image = qt.QImage(imagePath)
            if image.width() and image.height():
                self.__image2Pixmap.putImage(image,image)
                self.setCaption('File : %s' % os.path.split(imagePath)[1])
            else:
                raise StandardError("Can't open image %s" % imagePath)


if __name__ == "__main__" :
    import qt
    import sys
    if len(sys.argv) < 2:
        print sys.argv,"<filepath>"
        sys.exit(0)

    w = QubImageDisplay(imagePath=sys.argv[1])
    w.show()
    a.setMainWidget(w)
    a.exec_loop()
