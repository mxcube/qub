import qt
import qtcanvas
import time
import sys

from Qub.Widget.QubThreadUpdater import QubPixmap2Canvas

__revision__="$Revision$"
class QubImage(qtcanvas.QCanvasView):
    """
    This class inherits QCanvasView and optimize in time the display of a
    QPixmap and the drawings (QCanvasItem) which can be drawn on it.
    
    To display the QPixmap sets by the user (dataPixmap), QubPixmapView create
    a Transformation matrix to build another pixmap (bckPixmap) according to 
    the zoom factor.
    The bckPixmap is then set as background pixmap of a canvas which has the
    size of the bckPixmap.
    Building the bckPixmap may take some time, especially if the zoom factor is
    important. In order to guarantee the fluidity of the application, thread 
    can be used setting correctly the useThread attribute.
    
    In order to interact on the display outside the QubPixmapView, it generates
    signals on its main events (Mouse, context, resize ...).
    QubAction object will connect to these signals to make drawing or perform 
    action son the  display.
    
    Therefore, this object principaly performs display tasks. QubAction will
    provide functionality on it.
    """
         
    def __init__(self, parent=None, name=None, pixmap=None, useThread=0):
        """
        Constructor of the class.
        Create a QCanvasView with parent and name defined by "parent" and 
        "name" parameters.
        If "pixmap" is a valid pixmap it will display it using thread or not
        depending on the "useThread" parameter.
        Generates PYSIGNAL 
        """        
        qtcanvas.QCanvasView.__init__(self, parent, name, 
                                      qt.Qt.WNoAutoErase|qt.Qt.WStaticContents ) 
                                      
        self.time = -1  
     
        """
        parent widget
        """
        self.__parent = parent
        
        """
        initialization of thread to build bckPixmap id needed
        """
        self.__bckSize = (-1, -1)
        self.__oldDataPixmap = None
        self.__pixmapUpdater = None
        if useThread:
            self.__useThread = 0
        else:
            self.__useThread = 1
        self.setThread(useThread)
        
        """
        context menu QPopupMenu object
        """
        self.__contextMenu = None
        
        """
        default color used to draw on top of the pixmap
        """
        self.__foregroundColor = qt.QColor(qt.Qt.black)
        
        """
        pixmap which is displayed = data pixmap * transformation matrix
        """
        self.bckPixmap = None
        self.__zoomx = 1
        self.__zoomy = 1
        self.matrix = qt.QWMatrix(self.__zoomx, 0, 0, self.__zoomy, 0, 0)
        self.matrix.setTransformationMode(qt.QWMatrix.Areas)
        
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
        """
        the QubImage is ready to display, tells actions for connexion
        """
        self.emit(qt.PYSIGNAL("ViewConnect"), (self,))
        
        """
        display the pixmap if any
        """    
        self.setPixmap(pixmap)
 
    ##################################################
    ## PRIVATE METHODS   
    ##################################################    
    def __emitUpdate(self):
        """
        this signal is emitted when the bckPixmap change.
        The reasons can be new dataPixmap to display or bckPixmap size 
        changes following the zoom factor.
        It tells the actions for redrawing.
        """
        self.emit(qt.PYSIGNAL("ViewportUpdated"), ())
        self.canvas().update()

    def __updatePixmap(self):
        """
        this method will construct the bckPixmap.
        it is called if useThread is set to NO
        """
        update = 0   
        if self.dataPixmap is not None:
            neww = self.matrix.m11() * self.dataPixmap.width()
            newh = self.matrix.m22() * self.dataPixmap.height()
            
            if self.__bckSize != (neww, newh):
                if self.bckPixmap is not None:
                    self.bckPixmap.resize(neww, newh)
                else:
                    self.bckPixmap = qt.QPixmap(neww, newh)
                self.__bckSize = (neww, newh)
                update = 1
                
            if self.__oldDataPixmap != self.dataPixmap:
                self.__oldDataPixmap = self.dataPixmap
                update = 1           
                
        if update:
            painter  = qt.QPainter()
            painter.begin(self.bckPixmap)
            painter.setWorldMatrix(self.matrix)
            painter.drawPixmap(0, 0, self.dataPixmap)
            painter.end()

            self.canvas().resize(self.bckPixmap.width(),
                                 self.bckPixmap.height())
            self.canvas().setBackgroundPixmap(self.bckPixmap)

            self.__emitUpdate()
            
        print "Display no thread (ms): %d"%(int((time.time()-self.time)*1000),)
        self.time = -1

    def __calcZoom(self, w, h):
        if self.__scrollbarMode == "Fit2Screen" or \
           self.__scrollbarMode == "FullScreen":
            dataW = self.dataPixmap.width()
            dataH = self.dataPixmap.height()
        
            zoomx = 1
            if dataW != 0:
                zoomx = float(w) / float(self.dataPixmap.width())

            zoomy = 1
            if dataH != 0:
                zoomy = float(h) / float(self.dataPixmap.height())
            
            if self.__scrollbarMode == "Fit2Screen":
                zoomx = min(zoomx, zoomy)
                zoomy = zoomx
        else:
            (zoomx, zoomy) = (self.__zoomx, self.__zoomy)
            
                
        return (zoomx,zoomy)
    
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

    def contentsMousePressEvent(self, event):
        """
        Mouse has been pressed, tells the actions
        if right button is set, this press is for context menu only
        """
        if event.button() != qt.Qt.RightButton:   
            self.emit(qt.PYSIGNAL("MousePressed"), (event,))
            self.canvas().update()        

    def contentsMouseReleaseEvent(self, event):
        """
        Mouse has been pressed, tells the actions
        if right button is set, this press is for context menu only
        """
        if event.button() != qt.Qt.RightButton:   
            self.emit(qt.PYSIGNAL("MouseReleased"), (event,))
            self.canvas().update()

    def viewportResizeEvent(self, event):
        """
        Viewport has been resized, tells the actions
        """
        self.time = time.time()
        if self.__scrollbarMode == "Fit2Screen" or \
           self.__scrollbarMode == "FullScreen":
            (zoomx, zoomy) = self.__calcZoom(event.size().width(),
                                             event.size().height())            
            self.setZoom(zoomx, zoomy)
            
        #self.emit(qt.PYSIGNAL("ViewportResized"), (event,))
        #self.canvas().update()
          
    def contentsContextMenuEvent(self, event):
        """
        right mouse button has been hit. make the context menu appears
        """
        if self.__contextMenu is not None:
            if event.reason() == qt.QContextMenuEvent.Mouse:
                self.__contextMenu.exec_loop(qt.QCursor.pos())

    def customEvent(self, event):
        """
        when useThread is set to true, this methos is called after 
        bckPixmap has been rebuild by the thread
        """
        if event.event_name == "Pixmap2CanvasUpdated":
            if self.bckPixmap is not None:
                self.canvas().resize(self.bckPixmap.width(),
                                     self.bckPixmap.height())
                self.canvas().setBackgroundPixmap(self.bckPixmap)

            self.__emitUpdate()
        
        if self.time > 1:
            print "Display thread (ms): %d"%(int((time.time()-self.time)*1000),)
        self.time = -1
        
    ##################################################
    ## PUBLIC METHOD    
    ##################################################    
    def setContextMenu(self, menu):
        """
        set the QPopupMenu to be used as context menu
        """
        self.__contextMenu = menu 

    def getPPP(self):
        """
        return the pixmap to print
        """
        return self.bckPixmap

    def setForegroundColor(self, color):
        """
        change the color used for drawing on the bckPixmap
        tells the actions
        """
        self.__foregroundColor = color
        self.emit(qt.PYSIGNAL("ForegroundColorChanged"), 
                       (self.__foregroundColor,))
    
    def foregroundColor(self):
        """
        Return the foreground QubImage foreground Color
        """
        return self.__foregroundColor
        
    def setZoom(self, zoomx, zoomy):
        try:
            """
            change zoom factor, redisplay image and
            send update signal for actions
            """
            if self.time == -1:
                self.time = time.time()

            if self.__zoomx != zoomx or self.__zoomy != zoomy:
                self.matrix.setMatrix(zoomx, 0, 0, zoomy, 0, 0)
                self.__zoomx = zoomx
                self.__zoomy = zoomy

            if self.__useThread:
                self.__pixmapUpdater.update()
            else:
                self.__updatePixmap()
                self.__emitUpdate()
        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])

    def setImagePos(x=0, y=0, center=False):
        """
        Change the visible part of the pixmap.
        "center"=True: the (x,y) point of the pixmap is moved to the center of
        the visible part of the QubImage Widget
        "center"=False: the (x,y) point of the pixmap is moved to the upper
        left corner of the visible part of th QubImage object
        """            
        (px, py) = self.matrix.map(x, y)
        
        if center:
            self.center(px, py)
        else:
            self.setContentsPos(px, py)
                        
    def setPixmap(self, pixmap):
        """
        New pixmap to be displayed
        """
        self.time = time.time()
                
        self.dataPixmap = pixmap

        (zoomx, zoomy) = self.__calcZoom(self.viewport().width(),
                                         self.viewport().height())
            
        self.setZoom(zoomx, zoomy)

    def setThread(self, onoff):
        """
        tells the object to use thread or not to build the bckPixmap
        """
        if onoff and not self.__useThread:
            if self.__pixmapUpdater is None:
                self.__pixmapUpdater = QubPixmap2Canvas(self, "display")
            self.__pixmapUpdater.start()

        if not onoff and self.__useThread:
            self.__bckSize = (-1, -1)
            self.__oldDataPixmap = None
            if self.__pixmapUpdater is not None:
                self.__pixmapUpdater.stop()
                
        self.__useThread = onoff
   
    def setScrollbarMode(self, mode):
        """
        Change the scroll bar policy
        accepted values:
            "Auto":         Scrollbars are shown if needed
            "AlwaysOff" :   Scrollbars are never displayed
            "Fit2Screen" :  Displayed pixmap size follow CanvasView size 
                            keeping data pixmap ratio
            "FullScreen":   Displayed pixmap size is CanvasView size without 
                            keeping data pixmap ratio
        """
        if mode in ["Auto", "AlwaysOff", "Fit2Screen", "FullScreen"]:
            self.__scrollbarMode = mode
            
            if mode == "Auto":
                self.setHScrollBarMode(self.Auto)
                self.setVScrollBarMode(self.Auto)
                
            if mode == "AlwaysOff":
                self.setHScrollBarMode(self.AlwaysOff)
                self.setVScrollBarMode(self.AlwaysOff)

            if mode == "Fit2Screen" or mode == "FullScreen":
                self.setHScrollBarMode(self.AlwaysOff)
                self.setVScrollBarMode(self.AlwaysOff)
                if self.dataPixmap is not None:
                    (zoomx, zoomy) = self.__calcZoom(self.viewport().width(),
                                                     self.viewport().height())
                    self.setZoom(zoomx, zoomy)
                

#########################################################################
###  CLASS TEST PART
#########################################################################
class QubImageTest(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        self.__scrollbarMode = ["Auto", "AlwaysOff", "Fit2Screen", "FullScreen"]
        
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
 
