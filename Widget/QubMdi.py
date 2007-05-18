import itertools
import weakref
import qt
import os
import sys

from Qub.Icons.QubIcons import loadIcon

def QubMdiCheckIfParentIsMdi(parent) :
    mdiParent = parent
    mainWindow = None
    while mdiParent :
        if isinstance(mdiParent,qt.QWorkspace) :
            if mainWindow not in mdiParent.windowList() :
                break
        mainWindow = mdiParent
        mdiParent = mdiParent.parent()
    if not mdiParent: mainWindow = None
    return (mdiParent,mainWindow)
################################################################################
####################                  QubMdi                ####################
################################################################################
class QubMdi(qt.QWorkspace):
    def __init__(self, parent=None, name=None):
        """
        """
        qt.QWorkspace.__init__(self, parent, name)

        self.actions = {}
                
        self.setScrollBarsEnabled(1)
        self.__connectFollow()
        self.__mdiTreeChild = {}        # Tree of all main window and sub windows (key == mainWindow,val = list of window)
        self.__childWindowCbks = []
    """
    MDI WINDOW MANAGER                      
    """
    def windowCascade(self):
        """
        """
        self.__disconnectFollow()

        self.cascade()
        for window in self.windowList():
            if window.isShown() :
                window.resize(0.7 * self.width(), 0.7 * self.height())
		    
        self.__connectFollow()

    def windowTile(self):
        """
        """
        self.__disconnectFollow()
        self.tile()
        self.__connectFollow()

    def windowHorizontal(self):
        """
        """
        shownWindow = [x for x in itertools.ifilter(lambda w : w.isShown(),self.windowList())]
        windowHeight=float(self.height())/len(shownWindow)
        for i,window in enumerate(shownWindow) :
            window.parentWidget().showNormal()
            window.parentWidget().setGeometry(0, int(windowHeight*i),
                                        self.width(),int(windowHeight))
            window.parentWidget().raiseW()
                
        self.update()

    def windowVertical(self):
        """
        """
        shownWindow = [x for x in itertools.ifilter(lambda w : w.isShown(),self.windowList())]
        windowWidth = float(self.width()) / len(shownWindow)
        for i,window in enumerate(shownWindow) :
            window.parentWidget().showNormal()
            window.parentWidget().setGeometry(int(windowWidth*i),0,
                                              int(windowWidth),self.height())
            window.parentWidget().raiseW()
            
        self.update()


    def addNewChildOfMainWindow(self,mainWindow,child) :
        mainWindowRef = weakref.ref(mainWindow,self.__closeMainWindowCbk)
        subWindowList = self.__mdiTreeChild.get(mainWindowRef,[])
        if child:
            subWindowList.append(child)
        self.__mdiTreeChild[mainWindowRef] = subWindowList
        for cbk in self.__childWindowCbks:
            cbk(self.__mdiTreeChild)
        
    def addRefreshOnChildWindows(self,cbk) :
        self.__childWindowCbks.append(cbk)

    def __closeMainWindowCbk(self,mainWindowsRef) :
        try:
            for subWindow in self.__mdiTreeChild[mainWindowsRef] :
                try:
                    subWindow.close(True)
                except:
                    import traceback
                    traceback.print_exc()
            self.__mdiTreeChild.pop(mainWindowsRef)
            for cbk in self.__childWindowCbks:
                cbk(self.__mdiTreeChild)
        except KeyError:
            pass
        
    def __connectFollow(self):
        """
        """
        self.connect(self, qt.SIGNAL("windowActivated(QWidget*)"), 
                         self.onWindowActivated)

    def __disconnectFollow(self):
        """
        """
        self.disconnect(self, qt.SIGNAL("windowActivated(QWidget*)"), 
                            self.onWindowActivated)

    def onWindowActivated(self, win):
        """
        """
        pass

    """
    MENU                      
    """
    def __createAction(self, name, fct, icon=None, help=None, key=None):
        """
        """
        aName= name.replace("&", "")
        self.actions[aName]= qt.QAction(self, aName)
        self.actions[aName].setMenuText(qt.QString(name))
        if icon is not None:
            self.actions[aName].setIconSet(qt.QIconSet(loadIcon(icon)))
            
        if key is not None:
            self.actions[aName].setAccel(key)
            
        if help is not None:
            self.actions[aName].setWhatsThis(help)
            
        self.connect(self.actions[aName], qt.SIGNAL("activated()"), fct)

    """
    WINDOW MENU                      
    """
    def addWindowMenu(self, mainwin):
        """
        """
        self.__createAction("&Tile", self.windowTile, None, None,
                            qt.Qt.SHIFT+qt.Qt.Key_T)
        self.__createAction("&Cascade", self.windowCascade, None, None,
                            qt.Qt.SHIFT+qt.Qt.Key_C)
        self.__createAction("&Horizontal", self.windowHorizontal, None, None,
                            qt.Qt.SHIFT+qt.Qt.Key_H)
        self.__createAction("&Vertical", self.windowVertical, None, None,
                            qt.Qt.SHIFT+qt.Qt.Key_V)
                            
        self.menuWindow = qt.QPopupMenu(mainwin.menuBar())
        self.menuWindow.setCheckable(1)
        self.connect(self.menuWindow, qt.SIGNAL("aboutToShow()"), 
                     self.__displayWindowMenu)
        mainwin.menuBar().insertItem("&Window", self.menuWindow)

    def __displayWindowMenu(self):
        """
        """                   
        self.menuWindow.clear()
        
        self.actions["Tile"].addTo(self.menuWindow)
        self.actions["Cascade"].addTo(self.menuWindow)
        self.actions["Horizontal"].addTo(self.menuWindow)
        self.actions["Vertical"].addTo(self.menuWindow)
        
        self.menuWindow.insertSeparator()

    """
    WINDOW TOOLBAR                      
    """
    def addWindowToolBar(self, mainwin):
        """
        """
        self.winToolBar= qt.QToolBar(mainwin, "wintoolbar")
        self.winToolBar.setLabel("MDI")
        
        MainWindow = self.parent()
        while MainWindow:
            if hasattr(MainWindow,'addDockWindow') :
                break
            MainWindow = MainWindow.parent()
        if MainWindow:
            self.__windowDocWindow = qt.QDockWindow(self)
            self.__windowDocWindow.setCloseMode(qt.QDockWindow.Always)
            windowToolBox = qt.QToolBox(self.__windowDocWindow)
            self.__windowDocWindow.setWidget(windowToolBox)
            self.__windowDocWindow.setCaption('Opened window')
            self.__windowDocWindow.setResizeEnabled(True)
            windowToolBox.addItem(QubMdiTree(self,windowToolBox),'Opened window')
            MainWindow.addDockWindow(self.__windowDocWindow,qt.Qt.DockLeft)
            self.__windowDocWindow.hide()

            self.__windowControl = qt.QToolButton(self.winToolBar,"Opened Window")
            self.__windowControl.setIconSet(qt.QIconSet(loadIcon("gears.png")))
            qt.QObject.connect(self.__windowControl,qt.SIGNAL("clicked()"),self.__showWindowToolBox)

        self.fullscreen = qt.QToolButton(self.winToolBar,"Full Screen")
        self.fullscreen.setIconSet(qt.QIconSet(loadIcon("fullscreen.png")))
        qt.QObject.connect(self.fullscreen,qt.SIGNAL("clicked()"),self.windowFullScreen)
        
        self.winToolButton = qt.QToolButton(self.winToolBar,"Tile")
        self.winToolButton.setIconSet(qt.QIconSet(loadIcon("nofullscreen.png")))
        qt.QObject.connect(self.winToolButton,qt.SIGNAL("clicked()"),self.onWinToolAction)
        self.winToolMenu= qt.QPopupMenu(self.winToolButton)
        self.winToolMenu.setCheckable(1)
        self.winToolMenuText = ["Cascade", "Tile", "Tile Horizontally", "Tile Vertically"]
        self.winToolMenuIndex = []
        for text in self.winToolMenuText:
            self.winToolMenuIndex.append(self.winToolMenu.insertItem(text, self.onWinToolMenu))

        self.winToolMenu.setItemChecked(self.winToolMenuIndex[1], 1)
        self.winToolMenuAction= self.windowTile
        self.winToolButton.setPopup(self.winToolMenu)
        self.winToolButton.setPopupDelay(0)
        
    def onWinToolMenu(self, idx):
        """
        """
        for midx in self.winToolMenuIndex:
            self.winToolMenu.setItemChecked(midx, midx==idx)
        act= self.winToolMenuIndex.index(idx)
        self.winToolButton.setTextLabel(self.winToolMenuText[act])
        cbks = [self.windowCascade,self.windowTile,self.windowHorizontal,self.windowVertical]
        self.winToolMenuAction = cbks[act]
        self.onWinToolAction()

    def onWinToolAction(self):
        """
        """
        self.winToolMenuAction()
    
    def windowFullScreen(self) :
        window = self.activeWindow()
        if window: window.showMaximized()

    def __showWindowToolBox(self) :
        self.__windowDocWindow.show()
        self.__windowDocWindow.dock()

################################################################################
####################             QubMdiChild                ####################
################################################################################
class QubMdiChild(qt.QWidget):
    """
    Parent window must be a QWorkspace
    """
    def __init__(self, parent=None, name=None, master=None,
                 flags=qt.Qt.WDestructiveClose,**keys):
        
        """
        """
        qt.QWidget.__init__(self, parent, name, flags)
        self.parentWindow = parent
        self.masterWindow = master
        
        self.name = name
        if name == None:
            self.name = ""
            
        self.setTitle()
        self.resize(0.5*self.parentWindow.width(), 
                    0.5*self.parentWindow.height())
        self.show()

    def setTitle(self):
        """
        """
        if self.masterWindow is not None:
            self.title = self.masterWindow.getTitle() + "-" + self.name
        else:
            self.title = self.name

        self.setCaption(self.title)

    def getTitle(self):
        """
        """
        return self.title

    def closeEvent(self, ce):
        """
        """
        try:
            for window in self.parentWindow.windowList():
                if window.masterWindow is self:
                    window.close(1)

            self.emit(qt.PYSIGNAL("MDIChildClose"), ())

            ce.accept()
        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])
        
class QubMdiTree(qt.QListView) :
    def __init__(self,mdi,parent = None,name = "",f = 0) :
        qt.QListView.__init__(self,parent,name,f)
        self.__openCbk = None
        self.__mdi = mdi
        self.addColumn('Windows')
        mdi.addRefreshOnChildWindows(self.__refresh)
        self.__timer = qt.QTimer(self)
        qt.QObject.connect(self.__timer,qt.SIGNAL('timeout()'),self.__checkWindowState)
        self.__timer.start(1500)
        qt.QObject.connect(self,qt.SIGNAL('clicked(QListViewItem*)'),self.__clickedCBK)

    def __refresh(self,windowList) :
        try:
            currentWindow = set()
            for item in self.__getIterator():
                if not windowList.has_key(item.window):
                    self.takeItem(item)
                    continue
                else:
                    try:
                        name = item.window().caption()
                        item.setText(0,name)
                    except AttributeError:
                        pass

                    currentWindow.add(item.window)
            newWindow = set(windowList.keys())
            newWindow = newWindow.difference(currentWindow)
            for window in newWindow :
                try:
                    name = window().caption()
                    icon = window().icon()
                except AttributeError:
                    continue
                item = qt.QListViewItem(self)
                item.window = window
                item.setText(0,name)
                item.setOpen(True)
                if icon:
                    item.setPixmap(0,icon)
            for mainWindow,wList in windowList.iteritems():
                for mainItem in self.__getIterator() :
                    if mainItem.window == mainWindow :
                        for subWindow in wList:
                            findFlag = False
                            for subItem in self.__getIterator(mainItem) :
                                if subItem.window == subWindow:
                                    findFlag = True
                                    break
                            if not findFlag :
                                try:
                                    name = subWindow.name()
                                except AttributeError:
                                    continue
                                subItem = qt.QListViewItem(item)
                                subItem.window = subWindow
                                subItem.setText(0,name)
                                subItem.setVisible(False)
                                if subWindow.icon():
                                    subItem.setPixmap(0,subWindow.icon())
                        break
        except:
            import traceback
            traceback.print_exc()

    def __checkWindowState(self) :
        for item in self.__getIterator(None) :
            try: item.setText(0,item.window().caption())
            except AttributeError:
                pass
            self.__recurseCheckState(item)

    def __recurseCheckState(self,parentIterator) :
        if parentIterator:
            for item in self.__getIterator(parentIterator) :
                item.setVisible(item.window.isShown())
                self.__recurseCheckState(item)
                
    def __getIterator(self,parentIterator = None) :
        if parentIterator is not None :
            Item = parentIterator.firstChild()
        else :
            Item = self.firstChild()
        while Item :
            NextItem = Item.nextSibling()
            yield Item
            Item = NextItem

    def __clickedCBK(self,item) :
        try:
            if isinstance(item.window,qt.QWidget) :
                item.window.setFocus()
            else:
                item.window().setFocus()
        except ValueError:
            return

#############################################################################
##########                                                         ##########
##########                         MAIN                            ##########
##########                                                         ##########
############################################################################# 
if  __name__ == '__main__':
    
    import sys
    
    class QubMain(qt.QMainWindow):
        def __init__(self, parent=None, file=None):
            qt.QMainWindow.__init__(self, parent)

            self.mdi = QubMdi(self)
            self.mdi.addWindowMenu(self)
            self.mdi.addWindowToolBar(self)

            myToolBar= qt.QToolBar(self, "wintoolbar")
            myToolBar.setLabel("other toolbar")
            addButton = qt.QPushButton("Add Mdi Child", myToolBar)
            self.connect(addButton, qt.SIGNAL("clicked()"), self.addMdiChild)

            self.setCentralWidget(self.mdi)
        
        def addMdiChild(self):
            child = QubMdiChild(self.mdi, "titre")
            
            
            
    """
    MAIN
    """
    app = qt.QApplication(sys.argv)
    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))
    window = QubMain()
    app.setMainWidget(window)
    window.show()
    app.exec_loop()
