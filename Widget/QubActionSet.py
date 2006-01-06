import qt
import qtcanvas
import sys
import math

from Qub.Widget.QubAction import QubAction, QubImageAction, QubToggleImageAction
from Qub.Icons.QubIcons import loadIcon

  
###############################################################################
###############################################################################
####################                                       ####################
####################         Miscallenous Actions          ####################
####################                                       ####################
###############################################################################
###############################################################################


###############################################################################
####################             QubButtonAction           ####################
###############################################################################
class QubButtonAction(QubAction):
    """
    This action send a signal "ButtonPressed" when user hit the button
    It creates a pushbutton in the toolbar/contextmenu or statusbar
    """
    def __init__(self, label="", *args, **keys):
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
        
        Store in self._label the pushbutton label
        """
        QubAction.__init__(self, *args, **keys)
        
        self._item  = None
        self._label = label
        
    def addToolWidget(self, parent):
        """
        create default pushbutton (with a label) in the toolbar of the view.
        """
        if self._widget is None:
            self._widget = qt.QPushButton(self._label, parent, "addtoppbutton")
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.sendSignal)
            qt.QToolTip.add(self._widget, self._label)
            
        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        self._menu = menu
        self._item = menu.insertItem(qt.QString(self._label),
                                      self.sendSignal)
        
    def addStatusWidget(self, parent):
        """
        create pushbutton in the statusbar of the view
        """
        if self._widget is None:
            self._widget = qt.QPushButton(self._label, parent, "addtoppbutton")
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.sendSignal)
            qt.QToolTip.add(self._widget, self._label)
            
        return self._widget
         
    def sendSignal(self):
        """
        User have hit toolbar/contextmenu or statusbar pushbutton
        send "ButtonPressed" signal
        """ 
        self.emit(qt.PYSIGNAL("ButtonPressed"), ())

  
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
####################          QubSeparatorAction           ####################
###############################################################################
class QubSeparatorAction(QubAction):
    """
    """
    def __init__(self,  *args, **keys):
        QubAction.__init__(self, *args, **keys)
        
    def addToolWidget(self, parent):
        """
        create widget for the view toolbar
        """
                
        if self._widget is None:
            self._widget = qt.QLabel("", parent)
            
        return self._widget
    
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
        QubToggleImageAction.__init__(self, *args, **keys)

        self.__rectCoord = qt.QRect(0, 0, 1, 1)

        self._name = "rectangle"
    
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__rectangle = qtcanvas.QCanvasRectangle(self.__rectCoord,
                                                     self._qubImage.canvas()
                                                     )
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
    PYSIGNAL("LineSelected")
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
        QubToggleImageAction.__init__(self, *args, **keys)

        self.__startPt = qt.QPoint(0,0)
        self.__endPt   = qt.QPoint(1,1)

        self._name = "line"
        
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
        line coordinates have been changed by the user
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


###############################################################################
####################            QubVLineSelection           ###################
###############################################################################

class QubVLineSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select a vertical line and send x position using PYSIGNAL("VLineSelected").
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
        Use name of the action to find icon file.
        Initialise line start and end points variables.
        """
        QubToggleImageAction.__init__(self, *args, **keys)
        
        self.__cursorPos  = 0
        self.__imageHeight = 50

        if self._qubImage != None:
            self.__imageHeight = self._qubImage.visibleHeight()
        else:
            self.__imageHeight = 50

        self.__startPt = qt.QPoint(0, 0)
        self.__endPt   = qt.QPoint(0, self.__imageHeight)

        self._name = "vline"
        
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__line = qtcanvas.QCanvasLine(self._qubImage.canvas())
        self.__line.setPoints(self.__startPt.x(), self.__startPt.y(),
                              self.__endPt.x(), self.__endPt.y())

        self.__VLineCursor = qtcanvas.QCanvasLine(self._qubImage.canvas())
        self.__VLineCursor.setPoints(self.__cursorPos, 0,
                                     self.__cursorPos,
                                     self._qubImage.visibleHeight())

        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """
        set foreground color
        """
        self.__line.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__line.setPen(qt.QPen(color))
        self.__line.update()

        self.__VLineCursor.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__VLineCursor.setPen(qt.QPen(color))
        self.__VLineCursor.update()

    def _setState(self, bool):
        """
        Draw or Hide line canvas item
        """
        self.__state = bool
        if self.__line is not None:
            if self.__state:
                self._connect(self._qubImage)
                self.__line.show()
                self.__VLineCursor.show()
            else:
                self._disconnect(self._qubImage)
                self.__line.hide()
                self.__VLineCursor.hide()
            
            self.__line.update()
            self.__VLineCursor.update()
                
    def mousePress(self, event):
        """
        Update start and end point of the line to be the same on the mouse
        position
        """ 
        (x, y) = self._qubImage.matrix.invert()[0].map(event.x(), event.y())
        self.__startPt.setX(x)
        self.__startPt.setY(0)
        self.__endPt.setX(x)
        self.__endPt.setY(self._qubImage.visibleHeight())

        try:
            self.emit(qt.PYSIGNAL("VLineSelected"), (x,))
            self.viewportUpdate()
        except:
            sys.excepthook(sys.exc_info()[0],
                           sys.exc_info()[1],
                           sys.exc_info()[2])
            
    def mouseMove(self, event):
        """
        Move the VLine cursor.
        """
        (x, y) = self._qubImage.matrix.invert()[0].map(event.x(),
                                                       event.y())
        self.__cursorPos = x

        self.viewportUpdate()

    def mouseRelease(self, event):
        """
        """
        pass 

    def viewportUpdate(self):
        """
        Draw line either if qubImage pixmap has been updated or
        line coordinates have been changed by the user
        """
        try:
            startPt = self._qubImage.matrix.map(self.__startPt)
            endPt = self._qubImage.matrix.map(self.__endPt)

            self.__line.setPoints(startPt.x(),startPt.y(), endPt.x(), endPt.y())
            self.__VLineCursor.setPoints(self.__cursorPos, 0,
                                         self.__cursorPos,
                                         self._qubImage.visibleHeight())
                
            self.__line.update()
            self.__VLineCursor.update()

        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])





###############################################################################
####################            QubHLineSelection           ###################
###############################################################################

class QubHLineSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select an horizontal line and send position using PYSIGNAL("HLineSelected").
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
        Use name of the action to find icon file.
        Initialise line start and end points variables.
        """
        QubToggleImageAction.__init__(self, *args, **keys)
        
        self.__cursorPos  = 0
        self.__imageWidth = 50

        if self._qubImage != None:
            __imgWidth = self._qubImage.visibleWidth()
        else:
            __imgWidth = 50
            
        self.__startPt = qt.QPoint(0, 0)
        self.__endPt   = qt.QPoint(0, __imgWidth)

        self._name = "hline"
        
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__line = qtcanvas.QCanvasLine(self._qubImage.canvas())
        self.__line.setPoints(self.__startPt.x(), self.__startPt.y(),
                              self.__endPt.x(), self.__endPt.y())

        self.__HLineCursor = qtcanvas.QCanvasLine(self._qubImage.canvas())
        self.__HLineCursor.setPoints(0, self.__cursorPos,
                                     self._qubImage.visibleWidth(),
                                     self.__cursorPos )

        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """
        set foreground color
        """
        self.__line.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__line.setPen(qt.QPen(color))
        self.__line.update()

        self.__HLineCursor.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__HLineCursor.setPen(qt.QPen(color))
        self.__HLineCursor.update()

    def _setState(self, bool):
        """
        Draw or Hide Hline canvas item
        """
        self.__state = bool
        if self.__line is not None:
            if self.__state:
                self._connect(self._qubImage)
                self.__line.show()
                self.__HLineCursor.show()
            else:
                self._disconnect(self._qubImage)
                self.__line.hide()
                self.__HLineCursor.hide()
            
            self.__line.update()
            self.__HLineCursor.update()
                
    def mousePress(self, event):
        """
        Update start and end point of the line to be the same on the mouse
        position
        """ 
        (x, y) = self._qubImage.matrix.invert()[0].map(event.x(), event.y())
        self.__startPt.setX(0)
        self.__startPt.setY(y)
        self.__endPt.setX(self._qubImage.visibleWidth())
        self.__endPt.setY(y)

        try:
            self.emit(qt.PYSIGNAL("HLineSelected"), (y,))
            self.viewportUpdate()
        except:
            sys.excepthook(sys.exc_info()[0],
                           sys.exc_info()[1],
                           sys.exc_info()[2])
            
    def mouseMove(self, event):
        """
        Move the VLine cursor.
        """
        (x, y) = self._qubImage.matrix.invert()[0].map(event.x(),
                                                       event.y())
        self.__cursorPos = y

        self.viewportUpdate()

    def mouseRelease(self, event):
        """
        """
        pass 

    def viewportUpdate(self):
        """
        Draw line either if qubImage pixmap has been updated or
        line coordinates have been changed by the user
        """
        try:
            startPt = self._qubImage.matrix.map(self.__startPt)
            endPt = self._qubImage.matrix.map(self.__endPt)

            self.__line.setPoints(startPt.x(),startPt.y(), endPt.x(), endPt.y())
            self.__HLineCursor.setPoints(0, self.__cursorPos,
                                         self._qubImage.visibleWidth(),
                                         self.__cursorPos )
                
            self.__line.update()
            self.__HLineCursor.update()

        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])








class QubCanvasEllipse(qtcanvas.QCanvasEllipse):      
    def drawShape(self, p):
        p.drawArc(int(self.x()-self.width()/2+0.5), 
                  int(self.y()-self.height()/2+0.5), 
                  self.width(), self.height(), 
                  self.angleStart(), self.angleLength())       

class QubCanvasDonut(qtcanvas.QCanvasEllipse):
    """
    """
    def setClip(self, w, h):
        self.win = w
        self.hin = h
             
    def drawShape(self, p):
        try:
            xout = int(self.x() - self.width()/2+0.5)
            yout = int(self.y() - self.height()/2+0.5)
            
            xin  = int(self.x() - self.win/2+0.5)
            yin  = int(self.y() - self.hin/2+0.5)
            
            self.regionout = QRegion(xout, yout,
                                     self.width() + 2,
                                     self.height()+2, 
                                     QRegion.Ellipse)
            
            self.regionin  = QRegion(xin, yin, self.win, self.hin,
                                     QRegion.Ellipse)
            self.region = self.regionout.subtract(self.regionin)
            
            p.setClipRegion(self.region, QPainter.CoordPainter)
            p.setPen(Qt.NoPen)
            p.drawEllipse(xout, yout, self.width(), self.height())
            
            p.setClipping(0)       
        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])



###############################################################################
#####################          QubCircleSelection        ######################
###############################################################################
class QubCircleSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select a circle and send its (center, radius) parameters using
    PYSIGNAL("CircleSelected")
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
        Initialyse circle position variables
        """
        QubToggleImageAction.__init__(self, *args, **keys)

        self.__rectCoord = qt.QRect(0, 0, 1, 1)
        self.__x0 = 0
        self.__y0 = 0

        self._name = "circle"
    
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__circle = QubCanvasEllipse( self.__rectCoord.width(),
                                         self.__rectCoord.height(),
                                         self._qubImage.canvas()
                                         )
        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """   
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        """
        #self.__circle.setBrush(qt.QBrush(color,  qt.Qt.NoBrush ))
        self.__circle.setPen(qt.QPen(color))
        self.__circle.update()

    def _setState(self, bool):
        """
        Draw or Hide circle canvas item
        """
        self.__state = bool
        if self.__circle is not None:
            if self.__state:
                self._connect(self._qubImage)
                self.__circle.show()
            else:
                self._disconnect(self._qubImage)
                self.__circle.hide()
            
            self.__circle.update()

    def mousePress(self, event):
        """
        Update upper-left corner position of the rectangle and sets its
        width and height to 1
        """ 
        (x, y) = self._qubImage.matrix.invert()[0].map(event.x(), event.y())
        self.__x0 = x
        self.__y0 = y
        self.__rectCoord.setRect(x, y, 1, 1)
        self.viewportUpdate()
    
    def mouseMove(self, event):
        """
        Upper-left corner of the rectangle has been fixed when mouse press,
        Updates now the width and height to follow the mouse position
        """
        if event.state() == qt.Qt.LeftButton:
            (x, y) = self._qubImage.matrix.invert()[0].map(event.x(), 
                                                           event.y())

            dx = x - self.__x0
            dy = y - self.__y0
            radius = math.sqrt( pow(dx,2) + pow(dy,2) )
            w = radius * 2.0
            h = radius * 2.0
            xc = self.__x0 - radius
            yc = self.__y0 - radius
            self.__rectCoord.setRect(xc, yc, w, h)
            self.viewportUpdate()
            
    def mouseRelease(self, event):
        """
        Rectangle selection is finished, send corresponding signal
        with coordinates
        """
        self.emit(qt.PYSIGNAL("CircleSelected"), 
                  (0, 0, 0))

        self.viewportUpdate()
        
    def viewportUpdate(self):
        """
        Draw Circle either if qubImage pixmap has been updated or
        rectangle coordinates have been changed by the user
        """
        rect = self._qubImage.matrix.map(self.__rectCoord)
        (x,y) = self._qubImage.matrix.map(self.__x0, self.__y0)

        self.__circle.setSize(rect.width(), rect.height())
        self.__circle.move(x, y)
        
        self.__circle.update()            






###############################################################################
#####################          QubDiscSelection        ######################
###############################################################################
class QubDiscSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select a disc and send its (center, radius) parameters using
    PYSIGNAL("DiscSelected")
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
        Initialyse disc position variables
        """
        QubToggleImageAction.__init__(self, *args, **keys)

        self.__rectCoord = qt.QRect(0, 0, 1, 1)
        self.__x0 = 0
        self.__y0 = 0

        self._name = "disc"
    
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__disc = qtcanvas.QCanvasEllipse( self.__rectCoord.width(),
                                         self.__rectCoord.height(),
                                         self._qubImage.canvas()
                                         )
        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """   
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        """
        self.__disc.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__disc.setPen(qt.QPen(color))
        self.__disc.update()

    def _setState(self, bool):
        """
        Draw or Hide disc canvas item
        """
        self.__state = bool
        if self.__disc is not None:
            if self.__state:
                self._connect(self._qubImage)
                self.__disc.show()
            else:
                self._disconnect(self._qubImage)
                self.__disc.hide()
            
            self.__disc.update()

    def mousePress(self, event):
        """
        Update upper-left corner position of the rectangle and sets its
        width and height to 1
        """ 
        (x, y) = self._qubImage.matrix.invert()[0].map(event.x(), event.y())
        self.__x0 = x
        self.__y0 = y
        self.__rectCoord.setRect(x, y, 1, 1)
        self.viewportUpdate()
    
    def mouseMove(self, event):
        """
        Upper-left corner of the rectangle has been fixed when mouse press,
        Updates now the width and height to follow the mouse position
        """
        if event.state() == qt.Qt.LeftButton:
            (x, y) = self._qubImage.matrix.invert()[0].map(event.x(), 
                                                           event.y())

            dx = x - self.__x0
            dy = y - self.__y0
            radius = math.sqrt( pow(dx,2) + pow(dy,2) )
            w = radius * 2.0
            h = radius * 2.0
            xc = self.__x0 - radius
            yc = self.__y0 - radius
            self.__rectCoord.setRect(xc, yc, w, h)
            self.viewportUpdate()
            
    def mouseRelease(self, event):
        """
        Rectangle selection is finished, send corresponding signal
        with coordinates
        """
        self.emit(qt.PYSIGNAL("DiscSelected"), 
                  (0, 0, 0))

        self.viewportUpdate()
        
    def viewportUpdate(self):
        """
        Draw Disc either if qubImage pixmap has been updated or
        rectangle coordinates have been changed by the user
        """
        rect = self._qubImage.matrix.map(self.__rectCoord)
        (x,y) = self._qubImage.matrix.map(self.__x0, self.__y0)

        self.__disc.setSize(rect.width(), rect.height())
        self.__disc.move(x, y)
        
        self.__disc.update()            






###############################################################################
####################            QubZoomListAction          ####################
###############################################################################
class QubZoomListAction(QubAction):
    """
    This class add a zoom facility for QubImageView as a list of zoom factor:
        10, 25, 50, 75, 100, 200, 300, 400, 500%
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        Initialyse variables
        """
        QubAction.__init__(self, *args, **keys)
        
        self._zoomStrList = ["10%", "25%", "50%", "75%", "100%", "200%",
                             "300%", "400%", "500%"] 
        self._zoomValList = [0.1, 0.25, 0.5, 0.75, 1, 2, 3, 4, 5]
        
        self._item = None
        
        self._qubImage = None

    def viewConnect(self, qubImage):
        """
        connect actio0n with the QubImage object on which it will be applied
        """
        self._qubImage = qubImage
              
    def addToolWidget(self, parent):
        """
        Creates widgets to be added in the toolbar
        """

        """
        menu to select zoom value
        """
        self._listPopupMenu = qt.QPopupMenu(parent)
        for i in range(len(self._zoomStrList)):
            self._listPopupMenu.insertItem(self._zoomStrList[i], i)
        self.connect(self._listPopupMenu, qt.SIGNAL("activated(int )"),
                        self._applyZoomFromList)
                                                          
        """
        tool button to use selected zoom value
        """
        self._widget = qt.QToolButton(parent)
        self._widget.setAutoRaise(True)
        self._widget.setPopup(self._listPopupMenu)
        self._widget.setPopupDelay(0)
        self._widget.setIconSet(qt.QIconSet(loadIcon("zoomrect.png")))
        #self._widget.setText(qt.QString(self._zoomStrList[4]))

        self._widget.setFixedSize(75,27)
        
        qt.QToolTip.add(self._widget, "Zoom List")
                                     
        return self._widget
        
    def addMenuWidget(self, menu):
        self._menu = menu
        
        if self._item is None:
            qstr = qt.QString("%d%%"%(int(self.zoomVal*100)))
            self._item = menu.insertItem(qstr, self._ListPopupMenu)
            menu.connectItem(self._item, self._listPopupMenu.exec_loop)

    def _applyZoomFromList(self, index):
        if self._qubImage is not None:
            """
            set wait cursor as changing zoom factor could take some times
            """
            self._qubImage.setCursor(qt.QCursor(qt.Qt.WaitCursor))

            """
            Calculate zoom value from array
            """        
            zoomVal = self._zoomValList[index]

            """
            check zoom value
            """
            zoomVal = self._checkZoomVal(zoomVal)

            """
            update zoom value as percentage in toolbar and menu widget
            """        
            qstr = qt.QString("%d%%"%(int(zoomVal*100)))
            self._widget.setText(qstr)
            if self._item is not None:
                self.menu.changeItem(self._item, qstr)

            """
            calculate and display new pixmap not centered
            """
            self._qubImage.setZoom(zoomVal, zoomVal)

            """
            restore cursor
            """
            self._qubImage.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
        
    def _checkZoomVal(self, zoom):
        maxVal = 3000
        
        newzoom = zoom
        
        w = self._qubImage.dataPixmap.width() * zoom
        h = self._qubImage.dataPixmap.height() * zoom
        
        if w > maxVal or h > maxVal:
            if w > h:
                newzoom = float(maxVal) / float(self.drawable.dataPixmap.width())
            else:
                newzoom = float(maxVal) / float(self.drawable.dataPixmap.height())
                
        return newzoom
       
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
        

        # A1
        action = QubColormapAction(show=1, group="color")
        actions.append(action)
        
        action.setParam(self.colormap, self.colorMin, self.colorMax,
                        self.dataMin, self.dataMax, self.autoscale)
        self.connect(action, qt.PYSIGNAL("ColormapChanged"),
                        self.colormapChanged)
        
        # A2
        action = QubPrintPreviewAction(show=1, group="admin")
        actions.append(action)
        
        # A3
        action = QubSeparatorAction(show=1)
        actions.append(action)
        
        action = QubHLineSelection(show=1, group="selection")
        actions.append(action)

        action = QubVLineSelection(show=1, group="selection")
        actions.append(action)

        action = QubLineSelection(show=1, group="selection")
        actions.append(action)

        action = QubRectangleSelection(show=1, group="selection")
        actions.append(action)

        action = QubCircleSelection(show=1, group="selection")
        actions.append(action)

        action = QubDiscSelection(show=1, group="selection")
        actions.append(action)

        action = QubZoomListAction(show=1, group="zoom")
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
        image = qt.QImage(image_str, size[0], size[1], 32, None, 0,
                          qt.QImage.IgnoreEndian)
        pixmap = qt.QPixmap()
        pixmap.convertFromImage(image)         	      
        
        if self.qubImage is not None:
            self.qubImage.setPixmap(pixmap)       
        
    def readEdfFile(self, file):    
        edf = EdfFile.EdfFile(file)
        self.data = edf.GetData(0)
        self.dataMin = min(Numeric.ravel(self.data))
        self.dataMax = min(Numeric.ravel(self.data))

                       
##  MAIN   
if  __name__ == '__main__':
    from Qub.Widget.QubImageView import QubImageView
    import EdfFile
    import Numeric
    import spslut
    
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubMain(None, file = sys.argv[1])
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
