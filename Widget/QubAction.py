import qt
import sys

from Qub.Icons.QubIcons import loadIcon

        
################################################################################
####################                QubAction               ####################
################################################################################
class QubAction(qt.QObject):
    """
    Associated with a QubView widget, QubAction is the base Class to perform
    interaction with Qub display widgets (QubImage, QubGraph).
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
    def __init__(self, name="action", place="toolbar", show=1, group="", index=-1):
        """
        Constructor method
        name ... :  string name of the action
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
        
        qt.QObject.__init__(self)
        
        self._name      = name
        self.__place     = place
        self.__show      = show
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
        """
        if self._widget is None:
            self._widget = qt.QLabel(self._name, parent)
        
        return self._widget
        
    def delToolWidget(self):
        """
        This method should be reimplemented.
        Deletes action widget put in "group" dockarea of the "toolbar"
        """
        if self._widget is not None:
            del self._widget
            self._widget = None
        
    def addMenuWidget(self, menu):
        """
        This method should be reimplemented.
        Creates item in contextmenu "menu" for the action
        """
        if self._item is None:
            self._menu = menu
            self._item = menu.insertItem(qt.QString(self._name))

    def delMenuWidget(self):
        """
        This method should be reimplemented.
        Deletes action item from the popupmenu
        """
        if self._item is not None:
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
            del self._widget
            self._widget = None        
                
    def viewConnect(self):
        """
        Slot to connect to "ViewConnect" signal of the Qub Display widgets.
        Its main usage is to store the Qub display widget reference and to
        connect the action to the Qub display widget signals needed to perform
        the desired action.
        """
        pass
              
################################################################################
####################    TEST -- QubViewActionTest -- TEST   ####################
################################################################################
from Qub.Widget.QubImageView import QubImageView
from Qub.Print.QubPrintPreviewAction import QubPrintPreviewAction
        
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
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubMain(file=sys.argv[1])
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
