import qt
import qtcanvas
import sys
from Qub.Widget.QubAction import QubAction
from Qub.Icons.QubIcons import loadIcon

        
################################################################################
####################              QubImageAction            ####################
################################################################################
class QubImageAction(QubAction):
    """
    This inherits QubAction and add empty method for action acting on
    QubImage Object.
    Main adds on are slots for drawings
    """
    def __init__(self, name=None, qubImage=None, place="toolbar",
                 show=1, group="", index=-1):
        """
        Constructor method
        name ... :  string name of the action
        qubImage :  action will act on a QubImage object. It can be set in
                    the constructor method or using the "viewConnect" method
                    of the class 
        palce .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None)
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group
        """
        QubAction.__init__(self, name, place, show, group, index)
        
        self._qubImage = None
        
        if qubImage is not None:
            self.viewConnect(qubImage)

    def viewConnect(self, qubImage):
        """
        Register the "qubImage" object
        Connect action to "qubImage" signals:
            "ForegroundColorChanged" : Foreground color has been changed
            "MouseMoved" : Mouse has been moved inside the viewport of the
                           "qubImage"
            "MousePressed" : Mouse has been pressed inside he viewport of the
                             "qubImage"
            "MouseReleased" : Mouse has been released inside he viewport of
                              the "qubImage"
            "ViewportUpdated" : displayed pixmap of "qubImage" has changed 
                                (new pixmap or new size)
        """
        if self._qubImage is not None and qubImage is not None and \
           self._qubImage != qubImage:
            """
            disconnect action from previous qubImage
            """
            self._disconnect(self._qubImage)
            self._qubImage = None

        if qubImage is not None:
            self._qubImage = qubImage
            self._connect(self._qubImage)
            
    def _connect(self, view):
        """
        Connect action to view signals
        """
        self.connect(view, qt.PYSIGNAL("ForegroundColorChanged"),
                        self.setColor)
        self.connect(view, qt.PYSIGNAL("MouseMoved"),
                        self.mouseMove)
        self.connect(view, qt.PYSIGNAL("MousePressed"),
                        self.mousePress)
        self.connect(view, qt.PYSIGNAL("MouseReleased"),
                        self.mouseRelease)
        self.connect(view, qt.PYSIGNAL("ViewportUpdated"),
                        self.viewportUpdate)
    
    def _disconnect(self, view):
        """
        Disconnect action to view signals
        """
        self.disconnect(view, qt.PYSIGNAL("ForegroundColorChanged"),
                        self.setColor)
        self.disconnect(view, qt.PYSIGNAL("MouseMoved"),
                        self.mouseMove)
        self.disconnect(view, qt.PYSIGNAL("MousePressed"),
                        self.mousePress)
        self.disconnect(view, qt.PYSIGNAL("MouseReleased"),
                        self.mouseRelease)
        self.disconnect(view, qt.PYSIGNAL("ViewportUpdated"),
                        self.viewportUpdate)
                            
    def setColor(self, color):
        """
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        To be reimplemented.
        """
        pass
        
    def mouseMove(self, event):
        """
        Slot connected to "MouseMoved" "qubImage" signal
        To be reimplemented.
        """
        pass

    def mousePress(self,  event):
        """
        Slot connected to "MousePressed" "qubImage" signal
        To be reimplemented.
        """
        pass

    def mouseRelease(self, event):
        """
        Slot connected to "MouseReleased" "qubImage" signal
        To be reimplemented.
        """
        pass
    
    def viewportUpdate(self):
        """ 
        Slot connected to "ViewportUpdate" "qubImage" signal
        To be reimplemented.
        """
        pass
        
###############################################################################
####################            QubToggleImageAction        ###################
###############################################################################
class QubToggleImageAction(QubImageAction):
    """
    Base class for all action acting on image, representing by a toggle button
    in the menubar of the QubView.
    The name of the action will be used to find the icon file.
    """
    def __init__(self,*args, **keys):
        """
        Constructor method
        name ... :  string name of the action
        qubImage :  action will act on a QubImage object. It can be set in
                    the constructor method or using the "viewConnect" method
                    of the class 
        palce .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None)
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group
        """
        QubImageAction.__init__(self, *args, **keys)
            
    def addToolWidget(self, parent):
        """
        Creates action widget to put in "group" dockarea of the "toolbar"
        Return this widget.
        Use name of the action to find icon file
        """
        if self._widget is None:
            self._widget = qt.QToolButton(parent, "%s"%self._name)
            self._widget.setIconSet(qt.QIconSet(loadIcon("%s.png"%self._name)))
            self._widget.setAutoRaise(True)
            self._widget.setToggleButton(True)
            self.connect(self._widget, qt.SIGNAL("toggled(bool)"),
                         self.setState)
            qt.QToolTip.add(self._widget, "%s"%self._name)
        
        return self._widget
        
    def addMenuWidget(self, menu):
        """
        This method should be reimplemented.
        Creates item in contextmenu "menu" for the action
        """
        if self._item is None:
            self._menu = menu
            iconSet = qt.QIconSet(loadIcon("%s.png"%self._name))
            self._item = menu.insertItem(iconSet, qt.QString(self._name),
                                          self.menuChecked)

    def addStatusWidget(self, parent):
        """
        Creates action widget to put in  the "statusbar"
        Return this widget.
        Use name of the action to find icon file
        """
        if self._widget is None:
            self._widget = qt.QToolButton(parent, "%s"%self._name)
            self._widget.setIconSet(qt.QIconSet(loadIcon("%s.png"%self._name)))
            self._widget.setAutoRaise(True)
            self._widget.setToggleButton(True)
            self.connect(self._widget, qt.SIGNAL("toggled(bool)"),
                         self.setState)
            qt.QToolTip.add(self._widget, "%s"%self._name)
        
        return self._widget
       
    def menuChecked(self):
        """
        Slot connected to clicked() signal of menu item.
        As there is no parameter on the state of the toglle menu item,
        we build it and call the setState method of the class
        """
        if self._menu.isItemChecked(self._item):
            checked = 0
        else:
            checked = 1
        self.setState(checked)
        
            
    def setState(self, state):
        """
        "state" is True or False.
        Set toolbar, contextmenu or statusbar widgets of the action to
        the "state" value.
        Call the internal method _setState which is specific for each subclass
        and which manage the behavior.
        """
        if self._widget is not None:
            self._widget.setOn(state)
        
        if self._item is not None:
            self._menu.setItemChecked(self._item, state)
        
        self._setState(state)
        
    def _setState(self, state):
        """
        Set action behavior to "state".
        Should be reimplemented
        """
        pass
        
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
        palce .. :  where to put in the view widget, the selection widget
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
        palce .. :  where to put in the view widget, the selection widget
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
from Qub.Widget.QubImageView import QubImageView
        
class QubMain(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        pixmap = qt.QPixmap(file)
        
        actions = []
        action = QubRectangleSelection(show=1, group="selection")
        actions.append(action)
        action = QubLineSelection(show=1,group="selection")
        actions.append(action)
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
    
        qubImage = QubImageView(container, "Test QubImageAction's",
                                       pixmap, actions)
                                       
        hlayout.addWidget(qubImage)
    
        self.setCentralWidget(container)
               
##  MAIN   
if  __name__ == '__main__':
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubMain(file=sys.argv[1])
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
