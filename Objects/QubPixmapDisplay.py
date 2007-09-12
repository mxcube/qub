import weakref
import qt
import qtcanvas
import sys
from Qub.Objects.QubImage2Pixmap import QubImage2PixmapPlug
from Qub.Objects.QubEventMgr import QubEventMgr
##@defgroup ImageDisplayTools Tools to display Pixmap
#
#this is simple tools that can be link with DataProvidingTools

##@brief This tool display a Pixmap
#
#Display a Pixmap on a QCanvas background pixmap
#@ingroup ImageDisplayTools
class QubPixmapDisplay(qtcanvas.QCanvasView,QubEventMgr):
    ##@param parent the parent widget
    #@param name widget name
    def __init__(self, parent=None, name=None):
        qtcanvas.QCanvasView.__init__(self, parent, name, 
                                      qt.Qt.WNoAutoErase|qt.Qt.WStaticContents) 
                                           
        QubEventMgr.__init__(self)
        self.setFocusPolicy(qt.QWidget.WheelFocus)
        self._setScrollView(self)
        self.__name = name
        self.__plug = None
              
        self.__contextMenu = None
                
        self.__matrix = qt.QWMatrix(1, 0, 0, 1, 0, 0)
        self.__matrix.setTransformationMode(qt.QWMatrix.Areas)
        
        """
        create canvas for canvas view. It will hold the backPixmap as 
        background pixmap.
        Its size will be the size of the bckPixmap
        """
        self.__cvs = qtcanvas.QCanvas(1, 1)
        self.setCanvas(self.__cvs)

        
        ##@brief By default set the scrollbar mode to automatic
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
        self.__lastImage = None
        
    ##@name Mouse Events
    #@{

    ##@brief Mouse has moved
    #
    #tells the actions
    #if right button is set, this move is for context menu only
    def contentsMouseMoveEvent(self, event):
        if event.button() != qt.Qt.RightButton:
            self.emit(qt.PYSIGNAL("MouseMoved"), (event,))
            self.canvas().update()
            
        self._mouseMove(event)
    ##@brief Mouse has been pressed
    #
    #tells the actions
    #if right button is set, this press is for context menu only
    def contentsMousePressEvent(self, event):
        if not self.hasFocus() :
            self.setFocus()
      
        if event.button() != qt.Qt.RightButton:   
            self.emit(qt.PYSIGNAL("MousePressed"), (event,))
            self.canvas().update()        

        self._mousePressed(event)
             
    ##@brief Mouse has been release
    #
    #tells the actions
    #if right button is set, this press is for context menu only
    def contentsMouseReleaseEvent(self, event):
        if event.button() != qt.Qt.RightButton:   
            self.emit(qt.PYSIGNAL("MouseReleased"), (event,))
            self.canvas().update()
            
        self._mouseRelease(event)
    ##@}
    #

    ##@brief right mouse button has been hit. make the context menu appears
    def contentsContextMenuEvent(self, event):
        if self.__contextMenu is not None:
            if event.reason() == qt.QContextMenuEvent.Mouse:
                self.__contextMenu.exec_loop(qt.QCursor.pos())

    ##@name Key Event
    #@{

    ##@brief key pressed, dispatch
    def keyPressEvent(self,keyevent) :
        self._keyPressed(keyevent)
    ##@brief key release, dispatch
    def keyReleaseEvent (self,keyevent) :
        self._keyReleased(keyevent)
    ##@}

    ##@name Enter and Leave Events
    #@{

    ##@brief manged enter event
    #
    #on enter, take the focus for wheel an key event
    ##@brief leave event dispatch
    def leaveEvent(self,event) :
        self._leaveEvent(event)
    def viewportResizeEvent(self,resize) :
        self.__startIdle()
    ##@}
    
    def __startIdle(self,x = 0,y = 0) :
        vp = self.viewport()
        if not self.__idle.isActive() :
            self.__idle.start(0)
            
    def __emitViewPortUpdate(self) :
        self.__idle.stop()
        vp = self.viewport()
        self.emit(qt.PYSIGNAL("ContentViewChanged"), (self.contentsX(),self.contentsY(),vp.width(),vp.height()))
        self._update()

    def _realEmitActionInfo(self,text) :
        self.emit(qt.PYSIGNAL("ActionInfo"),(text,))
        
    ##@brief link this object with the pixmap object provider
    #
    #For now the pixmap object provider could be:
    # - QubImage2Pixmap
    #
    #@param plug the mother class of this object is QubImage2PixmapPlug
    #@see Qub::Objects::QubImage2Pixmap::QubImage2Pixmap
    #@see Qub::Objects::QubImage2Pixmap::QubImage2PixmapPlug
    def setPixmapPlug(self, plug):
        if self.__plug is not None :
            plug = self.__plug()
            if plug:
                plug.setEnd()
        self.__plug = weakref.ref(plug)
           
    ##@brief set a context menu on the QubPixmapDisplay
    #
    #It'll be called on the right click
    #@param menu is a QPopupMenu
    def setContextMenu(self, menu):
        self.__contextMenu = menu 

    ##@brief get the current pixmap of this object
    #@return the current display pixmap
    #
    #This methode is called before printing
    def getPPP(self):
        if self.__lastImage is not None:
            return qt.QPixmap(self.__lastImage)
        else:
            return qt.QPixmap()
        
    ##@brief get the in used zoom class
    #@see Qub::Objects::QubImage2Pixmap::QubImage2PixmapPlug::Zoom
    def zoom(self):
        if self.__plug :
            plug = self.__plug()
            if plug:
                return plug.zoom()
        
        raise StandardError("QubPixmapDisplay object not plugged")
    ##@brief set the horizontal and vertical zoom
    #
    #@param zoomx the values of the horizontal zoom ie: zoomx == 1 == 100%
    #@param zoomy the values of the vertical zoom
    #@param keepROI if keepROI == False -> zoom on full image
    #               else the ROI is keept
    def setZoom(self, zoomx, zoomy,keepROI = False):
        try:
            if self.__plug :
                plug = self.__plug()
                if plug is None:
                    raise StandardError("QubPixmapDisplay object not plugged")

                if self.__scrollMode in ["Auto", "AlwaysOff"]:
                    plug.zoom().setZoom(zoomx, zoomy,keepROI)
        except:
            import traceback
            traceback.print_exc()
    ##@brief Change the visible part of the pixmap.
    #
    #@param center:
    # - if True: the (x,y) point of the pixmap is moved to the center of
    #   the visible part of the QubPixmapDisplay Widget
    # - if False: the (x,y) point of the pixmap is moved to the upper
    #   left corner of the visible part of the QubPixmapDisplay object
    def setImagePos(x=0, y=0, center=False):
        (px, py) = self.__matrix.map(x, y)
        
        if center:
            self.center(px, py)
        else:
            self.setContentsPos(px, py)
                        
    ##@brief set the the pixmap on the QubPixmapDisplay
    #
    #This is the only way to set a pixmap on QubPixmapDisplay
    #@warning this mathode should't be directly called, but via the plug
    #@see setPixmapPlug
    #@param pixmap the pixmap at the zoom asked
    #@param image the full size image
    def setPixmap(self, pixmap, image):
        self.__lastImage = image
        (cvs_w, cvs_h) = (self.__cvs.width(), self.__cvs.height())
        (pix_w, pix_h) = (pixmap.width(), pixmap.height())
        plug = self.__plug()
        if plug:
            zoomClass = plug.zoom()
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
                        plug.zoom().setZoom(zoom_val, zoom_val,zoomClass.isRoiZoom())
                    else:
                        plug.zoom().setZoom(zoom_w, zoom_h,zoomClass.isRoiZoom())
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

    ##@brief Change the scroll bar policy
    #@param mode accepted string values:
    # -# <b>"Auto"</b>: Scrollbars are shown if needed
    # -# <b>"AlwaysOff"</b>: Scrollbars are never displayed
    # -# <b>"Fit2Screen"</b>: Displayed pixmap size follow CanvasView size 
    #                       keeping data pixmap ratio
    # -# <b>"FillScreen"</b>: Displayed pixmap size is CanvasView size without 
    #                       keeping data pixmap ratio
    def setScrollbarMode(self, mode):
        if mode in ["Auto", "AlwaysOff", "Fit2Screen", "FillScreen"]:
            self.__scrollMode = mode
            if self.__plug :
                plug = self.__plug()
                if mode == "Auto":
                    self.setHScrollBarMode(self.Auto)
                    self.setVScrollBarMode(self.Auto)
                    if plug is not None :
                        plug.zoom().setZoom(1, 1)

                elif mode == "AlwaysOff":
                    self.setHScrollBarMode(self.AlwaysOff)
                    self.setVScrollBarMode(self.AlwaysOff)
                    if plug is not None :
                        plug.zoom().setZoom(1, 1)

                elif mode == "Fit2Screen" or mode == "FillScreen":
                    self.setHScrollBarMode(self.AlwaysOff)
                    self.setVScrollBarMode(self.AlwaysOff)
                    if plug is not None :
                        plug.refresh()
    ##@return scrollbarMode
    #
    def scrollbarMode(self) :
        return self.__scrollMode
    ##@brief get the transformation matrix
    #
    #the matrix include the image zoom and the translation
    def matrix(self) :
        return self.__matrix
    ##@brief get the default foreground color of the drawing vector
    def foregroundColor(self) :
        return self.__foregroundColor
    ##@brief change the default foreground color of the drawing vector 
    def setForegroundColor(self,color) :
        self.__foregroundColor = color
        self.emit(qt.PYSIGNAL("ForegroundColorChanged"), 
                  (self.__foregroundColor,))
##@brief this is the link plug for QubPixmapDisplay
#
#this the link of an object and QubPixmapDisplay
class QubPixmapZoomPlug(QubImage2PixmapPlug):
    def __init__(self, receiver) :
        QubImage2PixmapPlug.__init__(self)
        
        self._receiver = receiver
        receiver.setPixmapPlug(self)
        
    def setPixmap(self, pixmap, image) :
        self._receiver.setPixmap(pixmap, image)
        return False
            

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



if  __name__ == '__main__':
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubImageTest()
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
