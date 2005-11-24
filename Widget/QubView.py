import qt
import sys


################################################################################
####################                 QubView                ####################
################################################################################
class QubView(qt.QWidget):
    """
    The QubView is a base class to build Widget to display data with the same
    protocol.
    Data display widgets should inherits this class and add their own 
    functionalities.
    QubView defines the 3 parts:
        toolbar/contextmenu
            "toolbar" is a dockarea on the top of the QubView widget.
            The dockaArea is the parent of Container which holds group of action
            widgets.
            Container (group) are defined by actions: as many containers as
            defined by QubView action list.
            One container is automatically added if at least one action return
            empty string calling its "group()" method 
            Container can be switch from the toolbar to contextmenu which
            appears on a right button click on the "view" widget
        view
            data visualization widget
        statusbar
            Like "toolbar", "statusbar" is foreseen to show action widgets.
            This is a simple QWidget holding a QHBoxLayout.
            Action widgets are put in it according to their index() method.
            "statusbar" is principaly foreseen to display TEXT action widget.
    """
    def __init__(self, parent=None, name=None, flags=qt.Qt.WDestructiveClose):
        """
        Constructor method:
            Layout creation
            Variables initialization
        """
        qt.QWidget.__init__(self, parent, name, flags)
        
        """
        create high level widget of QubImageView
        """
        self.__vlayout = qt.QVBoxLayout(self)
        
        """
        widget initialization
        """
        self.__toolbar   = None
        self.__view      = None
        self.__statusbar = None
        self.__actionList = {}
 
    ##################################################
    ## PRIVATE METHODS   
    ################################################## 

    ##################################################
    ## PUBLIC METHODS   
    ##################################################
    def setView(self, widget):
        """
        add widget "widget" as QubView view object
        """
        self.__view = widget
        if self.__toolbar is None:
            self.__vlayout.insertWidget(0, self.__view)
        else:
            self.__vlayout.insertWidget(1, self.__view)
        
    def view(self):
        """
        return data display widget
        """
        return self.__view
    
    def setToolbar(self, widget):   
        """
        add widget "widget" as "toolbar" view object
        """
        self.__toolbar = widget
        self.__vlayout.insertWidget(0, widget)

    def toolbar(self):
        """
        return toolbar widget (QubViewToolbar)
        """
        return self.__toolbar
        
    def setStatusbar(self, widget):   
        """
        add widget "widget" as "statusbar" view object
        """
        self.__statusbar = widget
        if self.__toolbar is None:
            if self.__view is None:
                self.__vlayout.insertWidget(0, widget)
            else:
                self.__vlayout.insertWidget(1, widget)
        else:
            if self.__view is None:
                self.__vlayout.insertWidget(1, widget)
            else:
                self.__vlayout.insertWidget(2, widget)
            

    def statusbar(self):
        """
        return statusbar widget (QubViewStatusBar)
        """
        return self.__statusbar
        
    def addAction(self, actions):
        """
        Add action(s) in the QubView environment 
        Generates Toolbar/Contextmenu, Statusbar ... if not already done
        If action in "actions" list already exists, modify it in the QubView.
        This method does not connect the action to its its view !!!
        """
        
        for action in actions:
            """
            remove action from list if exists and type, group or index are
            different
            """
            if action.name() in self.__actionList.keys():
                oldAction = self.__actionList[action.name()]
                if oldAction.place() != action.place() or \
                   oldAction.group() != action.group() or \
                   oldAction.index() != action.index():
                    self.delAction(action)
                else:
                    """
                    nothing change in this action, nothing to do
                    """
                    return
        
            """
            this is now a real new action, add it
            """
            self.__actionList[action.name()] = action
        
            """
            according of what action belong (statusbar or toolbar/contextmenu,
            create it if necessary
            """
            if action.place() == "toolbar":
                if self.toolbar() is None:
                    widget = QubViewToolbar(self)
                    self.setToolbar(widget)
                self.__toolbar.addAction(action)                
                
            if action.place() == "statusbar":
                if self.statusbar() is None:
                    widget = QubViewStatusbar(self)
                    self.setStatusbar(widget)
                self.__statusbar.addAction(action)

    def delAction(self, actions):
        """
        Remove actions in the "actions" list from the QubView widget.
        Related widgets are destroyed.
        TO DO    TO DO    TO DO
        """
        pass
            
    def getPPP(self):
        """
        Should return the printable pixmap of the QubView object.
        This method must be reimplemented.
        """
        return qt.QPixmap()



################################################################################
####################              QubViewToolbar            ####################
################################################################################
class QubViewToolbar(qt.QDockArea):
    """
    QubViewToolbar is a QDockArea appearing in the top of a QubView widget
    It creates and manages QToolbar and a Context menu on the view()
    of its parent.
    It adds and manages action widgets.
    It manages switch of container (group) of action widgets between toolbar
    and context menu
    """
    def __init__(self, parent=None):
        """
        constructor method
            Creates dockaArea
            Creates and connect contexmenu if possible
        """
        qt.QDockArea.__init__(self, qt.Qt.Horizontal,qt.QDockArea.Normal,parent)
        
        self.__groupList = {}
        
        if parent is not None: 
            self.__contextMenu = qt.QPopupMenu(parent)
            self.__contextMenu.setCheckable(1)
        
            self.connectContextMenu(parent.view())
    
    ##################################################
    ## PRIVATE METHODS   
    ################################################## 
    def __addGroup(self, groupName, index):
        """
        Add a new group of actions:
            add a DockArea in the toolbar
            add an entry in the first part of contextmenu to 
            switch between toolbar and context menu
        """
        
        """
        add entry ion the group list
        """
        self.__groupList[groupName] = {}
        newGroup = self.__groupList[groupName]
        newGroup["action"] = []
        newGroup["separator"] = None
        
        """
        create group dockwindow in toolbar
        """
        newGroup["toolbar"] = qt.QDockWindow(self)
        newGroup["toolbar"].hide()
        newGroup["toolbar"].setOrientation(qt.Qt.Horizontal)
        newGroup["toolbar"].setHorizontallyStretchable(False)
        self.moveDockWindow(newGroup["toolbar"], index)

        """
        create group entry in contextmenu
        """
        strGroupName = qt.QString(groupName)
        newGroup["menubar"] = self.__contextMenu.insertItem(strGroupName,
                                                            self.__changeGroup)
        
    def __changeGroup(self):
        """
        method call when user presses on a "group" toggle button in 
        contextmenu to switch the display of a "group from "contextmenu" to
        "toolbar" or vice versa
        """    
        for groupName in self.__groupList.keys():
            groupObject = self.__groupList[groupName]
            status=self.__contextMenu.isItemChecked(groupObject["menubar"])
            if  groupObject["visible"]:
                self.__showGroup(groupName, 0)
            else:
                self.__showGroup(groupName, 1)
        
    def __showGroup(self, gName, inToolbar):
        """
        show group (dockarea) in "toolbar" widget of the Qubview if 
        "inToolbar" is True, in the context menu if "inToolbar" is False
        """
        groupName = gName
        if groupName == "":
            groupName = "Misc."
            
        if groupName in self.__groupList.keys():
            groupObject = self.__groupList[groupName]
            groupObject["visible"] = inToolbar
            
            if inToolbar:
                """
                Remove "groupName" from contextmenu
                """
                self.__contextMenu.setItemChecked(groupObject["menubar"], 1)

                """
                remove separator
                """
                if groupObject["separator"] is not None:
                    self.__contextMenu.removeItem(groupObject["separator"])
                    groupObject["separator"] = None
                
                """
                remove action items
                """
                for action in groupObject["action"]:
                    action.delMenuWidget()
                    
                """
                show group in toolbar
                """
                groupObject["toolbar"].show()
                    
            else:
                self.__contextMenu.setItemChecked(groupObject["menubar"], 0)
                """
                hide group in toolbar
                """
                groupObject["toolbar"].hide()
                
                """
                Create separator item in contextmenu
                """
                widget = qt.QFrame(self.__contextMenu)
                widget.setFrameShape(qt.QFrame.HLine)
                widget.setFrameShadow(qt.QFrame.Sunken)
                groupObject["separator"] = self.__contextMenu.insertItem(widget)
                
                """
                Create group action item
                """
                for action in groupObject["action"]:
                    action.addMenuWidget(self.__contextMenu)
  
    ##################################################
    ## PUBLIC METHODS   
    ##################################################                 
    def connectContextMenu(self, widget):
        """
        connect the context menu on the widget it should appears in
        This method is normally called by the constructor but, if the connected
        widget does not exists when the QubViewToolbar is created it can be
        connected later. 
        This is the only reason this method is not a private method
        """
        if widget is not None:
            widget.setContextMenu(self.__contextMenu)

    def addAction(self, action):
        """
        Get the "group" the action belongs to.
        If none, action belongs to the automatically created "Misc." group
        """
        actionGroup      = action.group()
        actionGroupIndex = action.index()
        if actionGroup == "":
            actionGroup = "Misc."
            actionGroupIndex = -1

        """
        If group "actionGroup" does not already exist, creates it
        """
        if actionGroup not in self.__groupList.keys():
            self.__addGroup(actionGroup, actionGroupIndex)
        
        """
        Add action to group action list
        """
        self.__groupList[actionGroup]["action"].append(action)

        """
        Create action widgets belonging to the toolbar widget
        """
        widget = action.addToolWidget(self.__groupList[actionGroup]["toolbar"])
        self.__groupList[actionGroup]["toolbar"].boxLayout().addWidget(widget)

        
        """
        Show group as specified (toolbar or contextmenu) by the action
        """
        self.__showGroup(action.group(), action.show())
        
    def delAction(self, action):
        """
        Remove "action" from the class
        """
        groupName = action.group()
        if groupName in self__groupList.keys():
            groupObject = self.__groupList[groupName]
            
            if action in groupObject["action"]:    
                action.delToolWidget()
                if not groupObject["visible"]:
                    action.delMenuWidget(self.__contextMenu)
            
                groupObject["action"].remove(action)
                    



        
################################################################################
####################             QubViewStatusbar           ####################
################################################################################
class QubViewStatusbar(qt.QWidget):
    """
    QubViewStatusBar is a QWidget appearing in the bottom of a QubView widget
    It adds and manages action widgets.
    """
    def __init__(self, parent):
        """
        constructor method
            Creates QWidget container and its horizontal layout
            Add the container at the bottom of the QubView Widget
        """
        qt.QWidget.__init__(self, parent)
        
        self.__hlayout = qt.QHBoxLayout(self)
        
        self.__actionList = []
        
    ##################################################
    ## PUBLIC METHODS   
    ##################################################                 
    def addAction(self, action):
        """
        Add action widget in the "statusbar" of the QubView Widget
        """
        widget = action.addStatusWidget(self)
            
        self.__hlayout.insertWidget(action.index(), widget)
            
        self.__actionList.append(action)
            
    def delAction(self, action):
        """
        Remove action from the "statusbar"
        """
        if action in self.__actionList:
            action.delStatusWidget()
            self.__actionList.remove(action)
            
       
################################################################################
####################    TEST -- QubViewActionTest -- TEST   ####################
################################################################################
from Qub.Widget.QubImage import QubImage

class QubTestView(QubView):
    def __init__(self, parent, name, actions, file):
        QubView.__init__(self, parent, name)
                
        widget = QubImage(self, "QubImage", qt.QPixmap(file), 0)
        self.setView(widget)
        
        self.addAction(actions)
        
class QubMain(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
    
        self.qubImage = QubTestView(container, "QubTestView",
                                    [], file)
        hlayout.addWidget(self.qubImage)
    
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
 
