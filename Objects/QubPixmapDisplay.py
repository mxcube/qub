import qt
import qtcanvas
import sys
from Qub.Objects.QubImage2Pixmap import QubImage2PixmapPlug
from Qub.Objects.QubEventMgr import QubEventMgr

class QubPixmapDisplay(qtcanvas.QCanvasView,QubEventMgr):
    def __init__(self, parent=None, name=None):
        qtcanvas.QCanvasView.__init__(self, parent, name, 
                                      qt.Qt.WNoAutoErase|qt.Qt.WStaticContents) 
                                           
        QubEventMgr.__init__(self)
        self._setScrollView(self)
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
        self.__scrollMode = "Auto"
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

        self.connect(self,qt.SIGNAL('contentsMoving (int, int)'),self.__startIdle)

        self.__idle = qt.QTimer(self)
        self.connect(self.__idle,qt.SIGNAL('timeout()'),self.__emitViewPortUpdate)

        self.__foregroundColor = qtcanvas.QCanvasView.foregroundColor(self)
        
    ##################################################
    ## EVENTS    
    ##################################################          
    def contentsMouseMoveEvent(self, event):
        """
        Mouse has moved, tells the actions
        if right button is set, this move is for context menu only
        """
        if event.button() != qt.Qt.RightButton:
            self.emit(qt.PYSIGNAL("MouseMoved"), (event,))
            self.canvas().update()
            
        self._mouseMove(event)

    def contentsMousePressEvent(self, event):
        """
        Mouse has been pressed, tells the actions
        if right button is set, this press is for context menu only
        """
        if event.button() != qt.Qt.RightButton:   
            self.emit(qt.PYSIGNAL("MousePressed"), (event,))
            self.canvas().update()        

        self._mousePressed(event)
        
    def contentsMouseReleaseEvent(self, event):
        """
        Mouse has been pressed, tells the actions
        if right button is set, this press is for context menu only
        """
        if event.button() != qt.Qt.RightButton:   
            self.emit(qt.PYSIGNAL("MouseReleased"), (event,))
            self.canvas().update()
            
        self._mouseRelease(event)

    def contentsContextMenuEvent(self, event):
        """
        right mouse button has been hit. make the context menu appears
        """
        if self.__contextMenu is not None:
            if event.reason() == qt.QContextMenuEvent.Mouse:
                self.__contextMenu.exec_loop(qt.QCursor.pos())

    def keyPressEvent(self,keyevent) :
        self._keyPressed(keyevent)

    def keyReleaseEvent (self,keyevent) :
        self._keyReleased(keyevent)

    def enterEvent(self,event) :
        self.setFocus()
    def leaveEvent(self,event) :
        self._leaveEvent(event)
        
    def __startIdle(self,x = 0,y = 0) :
        if not self.__idle.isActive() :
            self.__idle.start(0)
            
    def __emitViewPortUpdate(self) :
        self.emit(qt.PYSIGNAL("ViewportUpdated"), ())
        self._update()
        self.__idle.stop()

    def _realEmitActionInfo(self,text) :
        self.emit(qt.PYSIGNAL("ActionInfo"),(text,))
        
    ##################################################
    ## PUBLIC METHOD    
    ##################################################
    def setPixmapPlug(self, plug):
        if self.__plug is not None :
            self.__plug.setEnd()
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
            return self.__plug.zoom()
        
        raise StandardError("QubPixmapDisplay object not plugged")
            
    def setZoom(self, zoomx, zoomy,keepROI = False):
        if self.__plug is None:
            raise StandardError("QubPixmapDisplay object not plugged")
        
        if self.__scrollMode in ["Auto", "AlwaysOff"]:
            self.__plug.zoom().setZoom(zoomx, zoomy,keepROI)
        
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
        (cvs_w, cvs_h) = (self.__cvs.width(), self.__cvs.height())
        (pix_w, pix_h) = (pixmap.width(), pixmap.height())
        zoomClass = self.__plug.zoom()
        if self.__scrollMode in ["Auto", "AlwaysOff"]:
            if (cvs_w, cvs_h) != (pix_w, pix_h):
                self.__cvs.resize(pix_w, pix_h)
                self.__startIdle()
            self.__cvs.setBackgroundPixmap(pixmap)
        else:
            zoom = zoomClass.zoom()
            (view_w, view_h) = (self.viewport().width(), self.viewport().height())
            if zoomClass.isRoiZoom() :
                offx,offy,width,height = zoomClass.roi()
                (im_w, im_h) = width,height
            else:
                (im_w, im_h) = (image.width(), image.height())
            (w, h) = (int(im_w * zoom[0]), int(im_h * zoom[1]))

            if(abs(w - view_w) <= 1 and abs(h - view_h) <= 1 and self.__scrollMode == "FillScreen" or
               self.__scrollMode == "Fit2Screen" and zoom[0] == zoom[1] and
               (abs(w - view_w) <= 1 and h <= view_h or w <= view_w and abs(h - view_h) <= 1)) :
                if (cvs_w, cvs_h) != (pix_w, pix_h):
                    self.__cvs.resize(pix_w, pix_h)
                    self.__startIdle()
                self.__cvs.setBackgroundPixmap(pixmap)
            else:
                zoom_w = float(view_w) / im_w
                zoom_h = float(view_h) / im_h
                if self.__scrollMode == "Fit2Screen":
                    zoom_val = min(zoom_w, zoom_h)
                    self.__plug.zoom().setZoom(zoom_val, zoom_val,zoomClass.isRoiZoom())
                else:
                    self.__plug.zoom().setZoom(zoom_w, zoom_h,zoomClass.isRoiZoom())
                self.__startIdle()

        zoomx,zoomy = zoomClass.zoom()
        lastoffx,lastoffy = self.__matrix.dx(),self.__matrix.dy()
        self.__matrix.setMatrix(zoomx, 0, 0, zoomy,0,0)
        if zoomClass.isRoiZoom() :
            offx,offy,width,height = zoomClass.roi()
            self.__matrix = self.__matrix.translate(-offx,-offy)
            lastoffx /= zoomx
            lastoffy /= zoomy
            if (offx,offy) != (-lastoffx,-lastoffy) :
                self.__startIdle()

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
            self.__scrollMode = mode
            
            if mode == "Auto":
                self.setHScrollBarMode(self.Auto)
                self.setVScrollBarMode(self.Auto)
                if self.__plug is not None :
                    self.__plug.zoom().setZoom(1, 1)
                
            elif mode == "AlwaysOff":
                self.setHScrollBarMode(self.AlwaysOff)
                self.setVScrollBarMode(self.AlwaysOff)
                if self.__plug is not None :
                    self.__plug.zoom().setZoom(1, 1)

            elif mode == "Fit2Screen" or mode == "FillScreen":
                self.setHScrollBarMode(self.AlwaysOff)
                self.setVScrollBarMode(self.AlwaysOff)
                if self.__plug is not None :
                    self.__plug.refresh()
    def matrix(self) :
        return self.__matrix
    def foregroundColor(self) :
        return self.__foregroundColor
    def setForegroundColor(self,color) :
        self.__foregroundColor = color
        self.emit(qt.PYSIGNAL("ForegroundColorChanged"), 
                  (self.__foregroundColor,))
class QubPixmapZoomPlug(QubImage2PixmapPlug):
    def __init__(self, receiver) :
        QubImage2PixmapPlug.__init__(self)
        
        self._receiver = receiver
        receiver.setPixmapPlug(self)
        
    def setPixmap(self, pixmap, image) :
        self._receiver.setPixmap(pixmap, image)
        return False
            
#########################################################################
###  CLASS TEST PART
#########################################################################
class QubImageTest(qt.QMainWindow):
    class _timer(qt.QTimer) :
        def __init__(self,pixmapMgr) :
            qt.QTimer.__init__(self)
            import os
            import os.path
            self.connect(self,qt.SIGNAL('timeout()'),self.__putImage)
            self.images = []
            imagenames = []
            for root,dirs,files in os.walk('/bliss/users/petitdem/TestGui/Image') :
                for file_name in files :
                  basename,ext = os.path.splitext(file_name)
                  if ext == '.jpeg' :
                      imagenames.append(file_name)
                break
            for name in sorted(imagenames) :
                self.images.append(qt.QImage(os.path.join(root,name)))
            self.__pixmapManager = pixmapMgr
            self.id = 0
            self.start(0)

        def __putImage(self) :
            self.__pixmapManager.putImage(self.images[self.id % len(self.images)])
            self.id += 1

    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        self.__scrollMode = ["Auto", "AlwaysOff", "Fit2Screen", "FillScreen"]
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
    
        self.__qubpixmapdisplay = QubPixmapDisplay(container, "QubImage")
        self.__qubpixmapdisplay.setScrollbarMode("Auto")
        hlayout.addWidget(self.__qubpixmapdisplay)
    
        vlayout = qt.QHBoxLayout(hlayout)
    
        self.scrollBarWidget = qt.QButtonGroup(len(self.__scrollMode), 
                                               qt.Qt.Vertical, container, 
                                               "Scrollbar mode")
        self.connect(self.scrollBarWidget, qt.SIGNAL("clicked(int)"),
                     self.setScrollbarMode)
        for name in self.__scrollMode:
            scrollbarModeWidget = qt.QRadioButton(name, self.scrollBarWidget)
        
        vlayout.addWidget(self.scrollBarWidget)
        
        self.setCentralWidget(container)

        from Qub.Objects.QubImage2Pixmap import QubImage2Pixmap
        self.__image2Pixmap = QubImage2Pixmap(True)
        plug = QubPixmapZoomPlug(self.__qubpixmapdisplay)
        self.__image2Pixmap.plug(plug)
        self.__timer = QubImageTest._timer(self.__image2Pixmap)

    def setScrollbarMode(self, item):
        self.__qubpixmapdisplay.setScrollbarMode(self.__scrollMode[item])            


##  MAIN   
if  __name__ == '__main__':
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubImageTest()
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
