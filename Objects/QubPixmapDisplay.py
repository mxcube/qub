import qt
import qtcanvas
import sys

class QubPixmapDisplay(qtcanvas.QCanvasView):
    def __init__(self, parent=None, name=None):
        qtcanvas.QCanvasView.__init__(self, parent, name, 
                                      qt.Qt.WNoAutoErase|qt.Qt.WStaticContents ) 
                                           
        """
        parent widget
        """
        self.__parent = parent
        self.__name = name
        
        """
        plug
        """
        self.__plug = None
              
        """
        context menu QPopupMenu object
        """
        self.__contextMenu = None
                
        """
        pixmap which is displayed = data pixmap * transformation matrix
        """
        self.bckPixmap = None
        self.__matrix = qt.QWMatrix(1, 0, 0, 1, 0, 0)
        self.__matrix.setTransformationMode(qt.QWMatrix.Areas)
        
        """
        create canvas for canvas view. It will hold the backPixmap as 
        background pixmap.
        Its size will be the size of the bckPixmap
        """
        self.__cvs = qtcanvas.QCanvas(1, 1)
        self.setCanvas(self.__cvs)

        """
        By default set the scrollbar mode to automatic
        """
        self.__scrollbarMode = "Auto"
        self.setHScrollBarMode(self.Auto)
        self.setVScrollBarMode(self.Auto)
        
        """
        Set default behavior of the viewport:
            color outside the canvas = grey
            report all mouse movement
        """
        self.viewport().setPaletteBackgroundColor(qt.QColor(qt.Qt.gray))
        self.viewport().setMouseTracking(True)

        self.setSizePolicy(qt.QSizePolicy.Ignored,
                           qt.QSizePolicy.Ignored)
     
    ##################################################
    ## EVENTS    
    ##################################################          
    def contentsContextMenuEvent(self, event):
        """
        right mouse button has been hit. make the context menu appears
        """
        if self.__contextMenu is not None:
            if event.reason() == qt.QContextMenuEvent.Mouse:
                self.__contextMenu.exec_loop(qt.QCursor.pos())
        
    ##################################################
    ## PUBLIC METHOD    
    ##################################################
    def setPixmapPlug(self, plug):
        self.__plug = plug
           
    def setContextMenu(self, menu):
        """
        set the QPopupMenu to be used as context menu
        """
        self.__contextMenu = menu 

    def getPPP(self):
        """
        return the pixmap to print
        """
        return self.__cvs.backgroundPixmap()

    def zoom(self):
        """
        return current x and y zoom values
        """
        if self.__plug is not None:
            return(self.__plug.getZoom())
        
        raise StandardError("QubPixmapDisplay object not plugged")
            
    def setZoom(self, zoomx, zoomy):
        if self.__plug is None:
            raise StandardError("QubPixmapDisplay object not plugged")
        
        if self.__scrollMode in ["Auto", "AlwaysOff"]:
            self.__matrix.setMatrix(zoomx, 0, 0, zoomy, 0, 0)
            self.__plug.zoom().setZoom(zoomx, zoomy)
        
    def setImagePos(x=0, y=0, center=False):
        """
        Change the visible part of the pixmap.
        "center"=True: the (x,y) point of the pixmap is moved to the center of
        the visible part of the QubImage Widget
        "center"=False: the (x,y) point of the pixmap is moved to the upper
        left corner of the visible part of th QubImage object
        """            
        (px, py) = self.__matrix.map(x, y)
        
        if center:
            self.center(px, py)
        else:
            self.setContentsPos(px, py)
                        
    def setPixmap(self, pixmap, image):
        (cvs_w, cvs_h) = (self.__cvs.width(), self.cvs.height())
        if self.__scrollMode in ["Auto", "AlwaysOff"]:
            (pix_w, pix_h) = (pixmap.width(), pixmap.height())
            if (cvs_w, cvs_h) != (pix_w, pix_h):
                self.__cvs.resize(pix_w, pix_h)
            self.__cvs.setBackgroundPixmap(pixmap)
        else:
            zoom = self.__plug.zoom().getZoom()
            (im_w, im_h) = (image.width(), image.height())
            (w, h) = (int(im_w * zoom[0]), int(im_h * zoom[1]))
            if (w, h) == (cvs_w, cvs_h):
                self.__cvs.setBackgroundPixmap(pixmap)
            else:
                zoom_w = float(cvs_w) / im_w
                zoom_h = float(cvs_h) / im_h
                if self.__scrollMode == "Fit2Screen":
                    zoom_val = min(zoom_w, zoom_h)
                    self.__plug.zoom().setZoom(zoom_val, zoom_val)
                else:
                    self.__plug.zoom().setZoom(zoom_w, zoom_h)                    
            
    def setScrollbarMode(self, mode):
        """
        Change the scroll bar policy
        accepted values:
            "Auto":         Scrollbars are shown if needed
            "AlwaysOff" :   Scrollbars are never displayed
            "Fit2Screen" :  Displayed pixmap size follow CanvasView size 
                            keeping data pixmap ratio
            "FillScreen":   Displayed pixmap size is CanvasView size without 
                            keeping data pixmap ratio
        """
        if mode in ["Auto", "AlwaysOff", "Fit2Screen", "FillScreen"]:
            self.__scrollbarMode = mode
            
            if mode == "Auto":
                self.setHScrollBarMode(self.Auto)
                self.setVScrollBarMode(self.Auto)
                self.__plug.zoom().setZoom(1, 1)
                
            if mode == "AlwaysOff":
                self.setHScrollBarMode(self.AlwaysOff)
                self.setVScrollBarMode(self.AlwaysOff)
                self.__plug.zoom().setZoom(1, 1)

            if mode == "Fit2Screen" or mode == "FillScreen":
                self.setHScrollBarMode(self.AlwaysOff)
                self.setVScrollBarMode(self.AlwaysOff)
                self.__plug.refresh()
                

#########################################################################
###  CLASS TEST PART
#########################################################################
class QubImageTest(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        self.__scrollbarMode = ["Auto", "AlwaysOff", "Fit2Screen", "FillScreen"]
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
    
        self.qubImage = QubImage(container, "QubImage", 
                                 qt.QPixmap(file), 0)
        self.qubImage.setScrollbarMode("Auto")
        hlayout.addWidget(self.qubImage)
    
        vlayout = qt.QHBoxLayout(hlayout)
    
        self.scrollBarWidget = qt.QButtonGroup(len(self.__scrollbarMode), 
                                               qt.Qt.Vertical, container, 
                                               "Scrollbar mode")
        self.connect(self.scrollBarWidget, qt.SIGNAL("clicked(int)"),
                     self.setScrollbarMode)
        for name in self.__scrollbarMode:
            scrollbarModeWidget = qt.QRadioButton(name, self.scrollBarWidget)
        
        vlayout.addWidget(self.scrollBarWidget)
        
        self.useThreadWidget = qt.QPushButton("Use Thread", container)
        self.useThreadWidget.setToggleButton(True)
        self.connect(self.useThreadWidget, qt.SIGNAL("toggled(bool)"),
                     self.qubImage.setThread)

        vlayout.addWidget(self.useThreadWidget)

        self.setCentralWidget(container)

    def setScrollbarMode(self, item):
        self.qubImage.setScrollbarMode(self.__scrollbarMode[item])            


##  MAIN   
if  __name__ == '__main__':
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubImageTest(file=sys.argv[1])
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
