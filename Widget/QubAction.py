import weakref
import qt
import sys
import types

from Qub.Icons.QubIcons import loadIcon

        
################################################################################
####################                QubAction               ####################
################################################################################
class QubAction(qt.QObject):
    """
    Associated with a QubView widget, QubAction is the base Class to perform
    interaction with Qub display widgets (QubImage, QubGraph, QubTable).
    QubAction take care of the creation of action widget and their
    placement in the QubView widget, either in the ToolBar/ContextMenu or in the
    StatusBar. This class is responsible for placement, creation/destruction
    and show/hide of the action widgets.
    Inheriting from QubAction and reimpleting methods allows to perform actions 
    acting on different Display Widgets.
    In order to keep track of all action class, there is a global array
    ACTION_LIST, indexing by the name of the action and containing the class
    name.
    """
    def __init__(self,name = None,place = 'toolbar',show = True,
                 group = '',index = -1,**keys) :
     
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
        
        qt.QObject.__init__(self)
        self._name  = name
        
        self.__place    = place
        self.__show     = show
        self.__groupName = group
        self.__index     = index
        
        self._widget = None
        self._item   = None
        
        self._view = None
        self.__actionList = []
        
    ##################################################
    ## PRIVATE METHODS   
    ##################################################                 

    ##################################################
    ## PUBLIC METHODS   
    ##################################################
    def name(self):
        """
        Return the name of the action as set as the ACTION_LIST global array
        """
        return self._name
                        
    def setPlace(self, place, show):
        """
        Possible values for "place" are "toolbar" or "statusbar".
        the "show" parameter tells in case of "toolbar" place if container is
        shown in ToolBar (True) or ContextMenu (False)
        """
        self.__place = place
        self.__show  = show
    
    def place(self):
        """
        return the place where the action will be put 
        ("toolbar" or "statusbar")
        """
        return self.__place
        
    def show(self):
        """
        In case the action is placed in "toolbar", return the default place of 
        the "group" the action belongs to: 
        "toolbar" (True) or "contextmenu" (False)
        Not significant in case the action is placed in "statusbar"
        """
        return self.__show
        
    def group(self):
        """
        return the name of th group the action belongs to
        """
        return self.__groupName
        
    def index(self):
        """
        Return the position of the group the action belongs to if placed 
        in "toolbar"
        Return the position of the action widget in the "statusbar"
        """
        return self.__index
        
    def addToolWidget(self, parent):
        """
        This method should be reimplemented.
        Creates action widget to put in "group" dockarea of the "toolbar"
        Return this widget
        This method should return the widget to add stored self._widget
        which is deleted in delToolWidget method.
        """
        if self._widget is None:
            self._widget = qt.QLabel(self._name, parent)
        
        return self._widget
        
    def delToolWidget(self):
        """
        This method should be reimplemented.
        Deletes action widget put in "group" dockarea of the "toolbar"
        Self._widget is deleted
        """
        if self._widget is not None:
            self._widget.close(1)
            del self._widget
            self._widget = None
        
    def addMenuWidget(self, menu):
        """
        This method should be reimplemented.
        Creates item in contextmenu "menu" for the action
        items are stored in self._item which can be a list in case
        of multiple items
        """
        if self._item is None:
            self._menu = menu
            self._item = menu.insertItem(qt.QString(self._name))

    def delMenuWidget(self):
        """
        This method should be reimplemented.
        Deletes action item from the popupmenu
        self._item is remove even if it is a list
        """
        if self._item is not None:
            if type(self._item) is types.ListType:
                map(self.removeItem, self._item)
            else:
                self._menu.removeItem(self._item)
            self._item = None
        
        
    def addStatusWidget(self, parent):
        """
        This method should be reimplemented.
        Creates action widget to put in "statusbar"
        Return this widget
        By default creates a QLabel with the name of the action
        """
        if self._widget is None:
            self._widget = qt.QLabel(self._name, parent)
        
        return self._widget
        
    def delStatusWidget(self):
        """
        This method should be reimplemented.
        Deletes action widget put in "statusbar"
        """
        if self._widget is not None:
            self._widget.close(1)
            del self._widget
            self._widget = None        
                
    def viewConnect(self, parent):
        """
        Slot to connect to "ViewConnect" signal of the Qub Display widgets.
        Its main usage is to store the Qub display widget reference and to
        connect the action to the Qub display widget signals needed to perform
        the desired action.
        """
        pass
        
###############################################################################
####################               QubToggleAction          ###################
###############################################################################
class QubToggleAction(QubAction):
    """
    Base class for all action represented by a toggle button
    in the menubar or statusbar of the QubView.
    The name of the action will be used to find the icon file.
    Signal "StateChanged"
    """
    def __init__(self,initState = False,*args, **keys):
        """
        Constructor method.
        name ... :  string name of the action. Will be used to get the icon
                    file
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None).
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu.
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group.
        initState : set the init state ie: if True Toggle is On
        """
        QubAction.__init__(self,*args, **keys)
        self.__initState = initState
        
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
            if self.__initState :
                self._widget.toggle()
        return self._widget
        
    def addMenuWidget(self, menu):
        """
        This method should be reimplemented.
        Creates item in contextmenu "menu" for the action.
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
        
        self.emit(qt.PYSIGNAL("StateChanged"), (state,))
        
    def _setState(self, state):
        """
        Set action behavior to "state".
        Should be reimplemented
        """
        pass
        
################################################################################
####################              QubImageAction            ####################
################################################################################
class QubImageAction(QubAction):
    """
    This inherits QubAction and add empty method for action acting on
    QubImage Object.
    Main adds on are slots for drawings.
    """
    def __init__(self,qubImage=None,autoConnect=False, **keys):
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
        """
##        name = keys.get("name",None)
##        qubImage = keys.get("qubImage",None)
##        autoConnect = keys.get("autoConnect",False)
##        place = keys.get("place","toolbar")
##        show = keys.get("show",1)
##        group = keys.get("group","")
##        index = keys.get("index",-1)
        
        #QubAction.__init__(self, name, place, show, group, index)
        QubAction.__init__(self,**keys)
        if qubImage: self._qubImage = weakref.ref(qubImage)
        else: self._qubImage = None
        
        self._sigConnected = False
        self._autoConnect = autoConnect
        
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
        if self._autoConnect:
            connect = True
        else:
            connect = self._sigConnected

        oldQImage = self._qubImage and self._qubImage() or None
        
        if oldQImage and qubImage and oldQImage != qubImage:
            """
            disconnect action from previous qubImage
            """
            self.signalDisconnect(oldQImage)
            self._qubImage = None

        if qubImage is not None:
            self._qubImage = weakref.ref(qubImage)
            if connect:
                self.signalConnect(qubImage)
            else:
                self.signalDisconnect(qubImage)

    def signalConnect(self, view):
        """
        Connect action to view signals
        """
        if not self._sigConnected:
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

            self._sigConnected = True

    def signalDisconnect(self, view):
        """
        Disconnect action to view signals
        """
        if self._sigConnected:
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

            self._sigConnected = False
        
                            
    def setColor(self, color):
        """
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        To be reimplemented.
        """
        pass
        
    def mouseMove(self, event):
        """
        Slot connected to "MouseMoved" "qubImage" signal.
        To be reimplemented.
        """
        pass

    def mousePress(self,  event):
        """
        Slot connected to "MousePressed" "qubImage" signal.
        To be reimplemented.
        """
        pass

    def mouseRelease(self, event):
        """
        Slot connected to "MouseReleased" "qubImage" signal.
        To be reimplemented.
        """
        pass
    
    def viewportUpdate(self):
        """ 
        Slot connected to "ViewportUpdate" "qubImage" signal.
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
    def __init__(self,**keys):
        """
        Constructor method.
        name ... :  string name of the action.
        qubImage :  action will act on a QubImage object. It can be set in
                    the constructor method or using the "viewConnect" method
                    of the class.
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None).
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu.
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group.
        """
        QubImageAction.__init__(self,**keys)

        
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
        Creates item in contextmenu "menu" for the action.
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
              
################################################################################
####################    TEST -- QubViewActionTest -- TEST   ####################
################################################################################
class QubMain(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        pixmap = qt.QPixmap(file)
        
        actions = []
        action = QubPrintPreviewAction(show=1, group="admin")
        actions.append(action)
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
    
        qubImage = QubImageView(container, "Test QubImageAction's",
                                       pixmap, actions)
                                       
        hlayout.addWidget(qubImage)
    
        self.setCentralWidget(container)
               
##  MAIN   
if  __name__ == '__main__':
    from Qub.Widget.QubImageView import QubImageView
    from Qub.Print.QubPrintPreviewAction import QubPrintPreviewAction
    
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubMain(file=sys.argv[1])
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
