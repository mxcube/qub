import qt
import qtcanvas
import sys

from Qub.Widget.QubAction import QubAction, QubToggleImageAction
from Qub.Icons.QubIcons import loadIcon

  
###############################################################################
###############################################################################
####################                                       ####################
####################            Print Actions              ####################
####################                                       ####################
###############################################################################
###############################################################################

###############################################################################
####################          QubPrintPreviewAction        ####################
###############################################################################
class QubPrintPreviewAction(QubAction):
    """
    This action send the pixmap of its associated view to a PrinPreview Widget.
    It creates a pushbutton in the toolbar/contextmenu.
    It uses the "getPPP" method of the "view" to get the pixmap.
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        name ... :  string name of the action.
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None).
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu.
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it.
        index .. :  Position of the selection widget of the action in its
                    group.
        Initialise print preview widget parameter.
        """
        QubAction.__init__(self, *args, **keys)

        self._preview = None
        
        self._item = None
        
    def addToolWidget(self, parent):
        """
        create print preview pushbutton in the toolbar of the view
        """
        if self._widget is None:
            self._widget = qt.QToolButton(parent, "addtoppbutton")
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("addpreview.png")))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.addPixmapToPP)
            qt.QToolTip.add(self._widget, "add this window to print preview")
            
        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        iconSet = qt.QIconSet(loadIcon("addpreview.png"))
        self._menu = menu
        self._item = menu.insertItem(iconSet, qt.QString("Print preview"),
                                      self.addPixmapToPP)
        
    def addStatusWidget(self, parent):
        """
        create print preview pushbutton in the toolbar of the view
        """
        if self._widget is None:
            self._widget = qt.QToolButton(parent, "addtoppbutton")
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("addpreview.png")))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.addPixmapToPP)
            qt.QToolTip.add(self._widget, "add this window to print preview")

        return self._widget
         
    def addPixmapToPP(self):
        """
        if the print preview widget parameter is set, show the print preview
        widget and send it the pixmap of the associated view
        """ 
        if self._preview is not None:
            if self._view is not None:
                if hasattr(self._view, "getPPP"):
                    self._preview.show()
                    self._preview.addPixmap(self._view.getPPP())

    def viewConnect(self, view):
        """
        register the view.
        This action will call the "getPPP" method of the view and send it
        to the print preview widget
        """
        self._view = view

    def previewConnect(self, preview):
        self._preview = preview

  
###############################################################################
###############################################################################
####################                                       ####################
####################      Actions form QubImageView        ####################
####################                                       ####################
###############################################################################
###############################################################################

###############################################################################
####################            QubColormapAction          ####################
###############################################################################
from Qub.Widget.QubColormap import QubColormapDialog

class QubColormapAction(QubAction):
    """
    This action will allow in a display widget to open the QubColormap dialog
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        name ... :  string name of the action.
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None).
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu.
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it.
        index .. :  Position of the selection widget of the action in its
                    group.
        """
        QubAction.__init__(self, *args, **keys)
        
        self._item = None
        self._colormapDialog = None
        self.colormap = 0
        self.colorMin = 50
        self.colorMax = 150
        self.dataMin = 0
        self.dataMax = 200
        self.autoscale = 0
        
    def addToolWidget(self, parent):
        """
        create colormap pushbutton in the toolbar of the view
        create the colormap dialog if not already done
        """
        
        """
        create colormap dialog
        """
        if self._colormapDialog is None:
            self._colormapDialog = QubColormapDialog(parent)
            self._colormapDialog.setParam(self.colormap, self.colorMin,
                                          self.colorMax, self.dataMin,
                                          self.dataMax, self.autoscale)
            self.connect(self._colormapDialog, qt.PYSIGNAL("ColormapChanged"),
                         self.sendColormap)
        
        """
        create widget for the view toolbar
        """   
        if self._widget is None:
            self._widget = qt.QToolButton(parent, "colormap")
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("colormap.png")))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                            self.showColormapDialog)
            qt.QToolTip.add(self._widget, "Open colormap selector")

        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        self._menu = menu
        iconSet = qt.QIconSet(loadIcon("colormap.png"))
        self._item = menu.insertItem(iconSet, qt.QString("Colormap"),
                                      self.showColormapDialog)
        
    def addStatusWidget(self, parent):
        """
        create print preview pushbutton in the toolbar of the view
        """
        if self._widget is None:
            self._widget = qt.QToolButton(parent, "colormap")
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("colormap.png")))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.showColormapDialog)
            qt.QToolTip.add(self._widget, "Open colormap selector")

        return self._widget
        
    def showColormapDialog(self):
        self._colormapDialog.show()
         
    def setParam(self, colormap=None, colorMin=None, colorMax=None,
                 dataMin=None, dataMax=None, autoscale=None):
        """
        send the parameters to the QubDialog
        save them in case QubColormapDialog does not exists in order to
        send them later
        """
        self.colormap = colormap
        self.colorMin = colorMin
        self.colorMax = colorMax
        self.dataMin = dataMin
        self.dataMax = dataMax
        self.autoscale = autoscale
        if self._colormapDialog is not None:
            self._colormapDialog.setParam(colormap, colorMin, colorMax, 
                                          dataMin, dataMax, autoscale)

    def sendColormap(self, colormap, autoscale, colorMin, colorMax):
        self.emit(qt.PYSIGNAL("ColormapChanged"),
                  (colormap, autoscale, colorMin, colorMax))
                         
                         
###############################################################################
####################          QubRectangleSelection        ####################
###############################################################################
class QubRectangleSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select a rectangle and send its (x,y,width,height) parameters using
    PYSIGNAL("RectangleSelected")
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        name ... :  string name of the action
        qubImage :  action will act on a QubImage object. It can be set in
                    the constructor method or using the "viewConnect" method
                    of the class 
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None)
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group
        Creates action widget to put in "group" dockarea of the "toolbar"
        Return this widget.
        Use name of the action to find icon file
        Initialyse rectangle position variables
        """
        QubToggleImageAction.__init__(self, name="rectangle", *args, **keys)

        self.__rectCoord = qt.QRect(0, 0, 1, 1)
    
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__rectangle = qtcanvas.QCanvasRectangle(self.__rectCoord,
                                               self._qubImage.canvas())
        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """   
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        """
        self.__rectangle.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__rectangle.setPen(qt.QPen(color))
        self.__rectangle.update()
       
    def _setState(self, bool):
        """
        Draw or Hide rectangle canvas item
        """
        self.__state = bool
        if self.__rectangle is not None:
            if self.__state:
                self._connect(self._qubImage)
                self.__rectangle.show()
            else:
                self._disconnect(self._qubImage)
                self.__rectangle.hide()
            
            self.__rectangle.update()

    def mousePress(self, event):
        """
        Update upper-left corner position of the rectangle and sets its
        width and height to 1
        """ 
        (x, y)=self._qubImage.matrix.invert()[0].map(event.x(), event.y())
        self.__rectCoord.setRect(x, y, 1, 1)
        self.viewportUpdate()
    
    def mouseMove(self, event):
        """
        Upper-left corener of the rectangle has been fixed when mouse press,
        Updates now the width and height to follow the mouse position
        """
        if event.state() == qt.Qt.LeftButton:
            (x, y) = self._qubImage.matrix.invert()[0].map(event.x(), 
                                                          event.y())
            w = x - self.__rectCoord.x()
            h = y - self.__rectCoord.y()
            self.__rectCoord.setSize(qt.QSize(w, h))

            self.viewportUpdate()
    
    def mouseRelease(self, event):
        """
        Rectangle selection is finished, send corresponding signal
        with coordinates
        """
        (x, y)=self._qubImage.matrix.invert()[0].map(event.x(), event.y())
        w = x - self.__rectCoord.x()
        h = y - self.__rectCoord.y()
        self.__rectCoord.setSize(qt.QSize(w, h))

        self.emit(qt.PYSIGNAL("RectangleSelected"), 
                  (self.__rectCoord.x(), self.__rectCoord.y(), 
                   self.__rectCoord.width(), self.__rectCoord.height()))

        self.viewportUpdate()
        
    def viewportUpdate(self):
        """
        Draw rectangle either if qubImage pixmap has been updated or
        rectangle coordinates have been changed by the user
        """
        rect = self._qubImage.matrix.map(self.__rectCoord)

        self.__rectangle.setSize(rect.width(), rect.height())
        self.__rectangle.move(rect.x(), rect.y())

        self.__rectangle.update()            

        
###############################################################################
####################            QubLineSelection           ####################
###############################################################################
class QubLineSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select a line and send the start and end point coordinates using
    PYSIGNAL("RectangleSelected")
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        name ... :  string name of the action
        qubImage :  action will act on a QubImage object. It can be set in
                    the constructor method or using the "viewConnect" method
                    of the class 
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None)
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group
        Creates action widget to put in "group" dockarea of the "toolbar"
        Return this widget.
        Use name of the action to find icon file
        Initialyse line start and end points variables
        """
        QubToggleImageAction.__init__(self, name="line", *args, **keys)

        self.__startPt = qt.QPoint(0,0)
        self.__endPt   = qt.QPoint(1,1)
    
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__line = qtcanvas.QCanvasLine(self._qubImage.canvas())
        self.__line.setPoints(self.__startPt.x(), self.__startPt.y(),
                              self.__endPt.x(), self.__endPt.y())

        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """
        set foreground color
        """
        self.__line.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__line.setPen(qt.QPen(color))
        self.__line.update()
       
    def _setState(self, bool):
        """
        Draw or Hide line canvas item
        """
        self.__state = bool
        if self.__line is not None:
            if self.__state:
                self._connect(self._qubImage)
                self.__line.show()
            else:
                self._disconnect(self._qubImage)
                self.__line.hide()
            
            self.__line.update()

    def mousePress(self, event):
        """
        Update start and end point of the line to be the same on the mouse
        position
        """ 
        (x, y) = self._qubImage.matrix.invert()[0].map(event.x(), event.y())
        self.__startPt.setX(x)
        self.__startPt.setY(y)
        self.__endPt.setX(x)
        self.__endPt.setY(y)

        self.viewportUpdate()

    def mouseMove(self, event):
        """
        Start point has been fixed by press event, make end point followed
        the mouse
        """
        if event.state() == qt.Qt.LeftButton:
            (x, y) = self._qubImage.matrix.invert()[0].map(event.x(),
                                                           event.y())
            self.__endPt.setX(x)
            self.__endPt.setY(y)

            self.viewportUpdate()

    def mouseRelease(self, event):
        """
        Line selection is finished, send start and end point coordinates
        with PYSIGNAL("LineSelected")
        """
        try:
            (x, y) = self._qubImage.matrix.invert()[0].map(event.x(), event.y())
            
            self.__endPt.setX(x)
            self.__endPt.setY(y)
            (x1,y1,x2,y2) = (self.__startPt.x(), self.__startPt.y(),
                             self.__endPt.x(), self.__endPt.y())
            
            self.emit(qt.PYSIGNAL("LineSelected"), (x1, y1, x2, y2))

            self.viewportUpdate()
        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])

    def viewportUpdate(self):
        """
        Draw line either if qubImage pixmap has been updated or
        rectangle coordinates have been changed by the user
        """
        try:
            startPt = self._qubImage.matrix.map(self.__startPt)
            endPt = self._qubImage.matrix.map(self.__endPt)

            self.__line.setPoints(startPt.x(),startPt.y(), endPt.x(), endPt.y())

            self.__line.update()
        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])

       
################################################################################
####################    TEST -- QubViewActionTest -- TEST   ####################
################################################################################        
class QubMain(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        self.colormapSps = [spslut.GREYSCALE, spslut.REVERSEGREY, spslut.TEMP,
                             spslut.RED, spslut.GREEN, spslut.BLUE, spslut.MANY]
        #pixmap = qt.QPixmap(file)
        self.readEdfFile(file)
        self.colormap = 0
        self.colorMin = self.dataMin
        self.colorMax = self.dataMax
        self.autoscale = 0
        
        actions = []
        
        action = QubColormapAction(show=1, group="color")
        actions.append(action)
        action.setParam(self.colormap, self.colorMin, self.colorMax,
                        self.dataMin, self.dataMax, self.autoscale)
        self.connect(action, qt.PYSIGNAL("ColormapChanged"),
                        self.colormapChanged)
        
        action = QubPrintPreviewAction(show=1, group="admin")
        actions.append(action)
        
        action = QubRectangleSelection(show=1, group="selection")
        actions.append(action)
        
        action = QubLineSelection(show=1,group="selection")
        actions.append(action)
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
    
        self.qubImage = QubImageView(container, "actions", None, actions)                             
        hlayout.addWidget(self.qubImage)
        self.updatePixmap()
    
        self.setCentralWidget(container)

    def colormapChanged(self, colormap, autoscale, colorMin, colorMax):
        print "ColormapChanged (TEST)"
        self.colormap  = colormap
        self.autoscale = autoscale
        self.colorMin  = colorMin
        self.colorMax  = colorMax
        self.updatePixmap()
        
    def updatePixmap(self):
        (image_str, size, minmax) = spslut.transform(self.data ,
                                               (1,0), 
                                               (spslut.LINEAR, 3.0),
                                               "BGRX", 
                                               self.colormapSps[self.colormap],
                                               self.autoscale, 
                                               (self.colorMin, self.colorMax))            
        image = qt.QImage(image_str,size[0],size[1],32,None,0,
                      qt.QImage.IgnoreEndian)
        pixmap = qt.QPixmap()
        pixmap.convertFromImage(image)         	      
        
        if self.qubImage is not None:
            self.qubImage.setPixmap(pixmap)       
        
    def readEdfFile(self, file):    
        edf = EdfFile.EdfFile(file)
        self.data = edf.GetData(0)
        self.dataMin = Numeric.minimum.reduce(Numeric.minimum.reduce(self.data))
        self.dataMax = Numeric.maximum.reduce(Numeric.maximum.reduce(self.data))

                       
##  MAIN   
if  __name__ == '__main__':
    from Qub.Widget.QubImageView import QubImageView
    import EdfFile
    import Numeric
    import spslut
    
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubMain(file=sys.argv[1])
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
