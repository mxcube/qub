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
        mainWindowDic = None
        try:
            mainWindowDic = self.__mdiTreeChild[mainWindowRef]
        except KeyError:
            for m,d in self.__mdiTreeChild.iteritems() :
                parentWindow,mainWindowDic = self.__findWindRefInTree(m,mainWindowRef,d)
                if parentWindow is not None:
                    break

        if mainWindowDic is None:  # mainWindow is not in the Tree create it
            mainWindowDic = {}
            self.__mdiTreeChild[mainWindowRef] = mainWindowDic
            
        if child:
            grandChildDic = None
            try:
                childRef = weakref.ref(child,self.__closeMainWindowCbk)
                grandChildDic = self.__mdiTreeChild.pop(childRef) # could be a previously a main window
            except KeyError:
                for m,d in self.__mdiTreeChild.iteritems() :
                    parentWindow,childSubWindow = self.__findWindRefInTree(m,childRef,d)
                    if parentWindow is not None:
                        grandChildDic = childSubWindow.pop(childRef)
                        break
                if grandChildDic is None: # Create it
                    grandChildDic = {}
            mainWindowDic[childRef] = grandChildDic

        for cbk in self.__childWindowCbks:
            cbk(self.__mdiTreeChild)
            
            
    def addRefreshOnChildWindows(self,cbk) :
        self.__childWindowCbks.append(cbk)

    def __closeMainWindowCbk(self,mainWindowsRef) :
        try:
            childSubWindow = None
            for m,d in self.__mdiTreeChild.iteritems() :
                if m != mainWindowsRef :
                    parentWindow,childSubWindow = self.__findWindRefInTree(m,mainWindowsRef,d)
                    if parentWindow is not None:
                        childSubWindow = childSubWindow.pop(mainWindowsRef)
                        break
                else:
                    childSubWindow = self.__mdiTreeChild.pop(m)
                    break
            if childSubWindow is not None:
                for subWindowRef,subWindowDic in childSubWindow.iteritems() :
                    try:
                        self.__closeWindowRecurs(subWindowRef,subWindowDic)
                    except:
                        import traceback
                        traceback.print_exc()
                        
            for cbk in self.__childWindowCbks:
                cbk(self.__mdiTreeChild)
        except KeyError:
            pass
        except:
            import traceback
            traceback.print_exc()
            
    def __findWindRefInTree(self,parentWindow,searchWindow,windowDico) :
        retParentWindow,retDico = None,None
        for childWindow,d in windowDico.iteritems() :
            if childWindow == searchWindow :
                retParentWindow,retDico = parentWindow,windowDico
                break
            else:
                p,dic = self.__findWindRefInTree(childWindow,searchWindow,d)
                if p is not None:
                    retParentWindow,retDico = p,dic
                    break
        return (retParentWindow,retDico)

    def __closeWindowRecurs(self,subRef,subWindowDic) :
        window = subRef()
        for subWindowRef,subWindowDic in subWindowDic.iteritems() :
            self.__closeWindowRecurs(subWindowRef,subWindowDic)
        if window:
            window.close(1)
            
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

        self.__popUpMenu = qt.QPopupMenu(self)
        self.__popUpMenu.insertItem('close',self.__closeCBK)

        qt.QObject.connect(self,qt.SIGNAL('rightButtonPressed(QListViewItem*,const QPoint &,int)'),
                           self.__popUpDisplay)

    def __popUpDisplay(self,item,point,columnid) :
        self.__popUpMenu.exec_loop(point)

    def __closeCBK(self,i) :
        for item in self.__getIterator():
            self.__close_recurse(item)
            if item.isSelected() :
                item.window().close()
                
    def __close_recurse(self,parentItem) :
        for item in self.__getIterator(parentItem) :
            self.__close_recurse(item)
            if item.isSelected() :
                item.window().close()
    def __insertRecurseItem(self,parentItem,parentWindowRef,childDico) :
        if parentItem is None:
            try:
                name = parentWindowRef().caption()
                icon = parentWindowRef().icon()
            except AttributeError: return
            newItem = qt.QListViewItem(self)
        else:
            try:
                name = parentWindowRef().name()
                icon = parentWindowRef().icon()
            except AttributeError: return
            newItem = qt.QListViewItem(parentItem)

        newItem.window = parentWindowRef
        newItem.setText(0,name)
        newItem.setOpen(True)
        if icon:
            newItem.setPixmap(0,icon)
            
        for childWindowRef,grandChilddoc in childDico.iteritems() :
            self.__insertRecurseItem(newItem,childWindowRef,grandChilddoc)
            
    def __recurseRefresh(self,parentItem,windowDico) :
        leavesItemWindows = []
        for item in self.__getIterator(parentItem) :
            childDico = windowDico.get(item.window,None)
            if childDico is not None:
               self.__recurseRefresh(item,childDico)
               leavesItemWindows.append(item.window)
            else:
                if parentItem is None:
                    self.takeItem(item)
                else:
                    parentItem.takeItem(item)
        for windowRef,childDico in windowDico.iteritems() :
            if windowRef not in leavesItemWindows:
                self.__insertRecurseItem(parentItem,windowRef,childDico)
                
            
    def __refresh(self,windowList) :
        self.__recurseRefresh(None,windowList)

    def __refresh_subItem(self,mainItem,wList) :
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
                subItem = qt.QListViewItem(mainItem)
                subItem.window = subWindow
                subItem.setText(0,name)
                subItem.setVisible(False)
                if subWindow.icon():
                    subItem.setPixmap(0,subWindow.icon())
        
    def __checkWindowState(self) :
        for item in self.__getIterator(None) :
            try:
                item.setText(0,item.window().caption())
                icon = item.window().icon()
                if icon:
                    item.setPixmap(0,icon)
            except AttributeError:
                pass
            self.__recurseCheckState(item)

    def __recurseCheckState(self,parentIterator) :
        if parentIterator:
            for item in self.__getIterator(parentIterator) :
                try:
                    w = item.window()
                    item.setVisible(w.isShown())
                    if w.isShown() :
                        icon = w.icon()
                        name = w.name()
                        if icon :
                            item.setPixmap(0,icon)
                        item.setText(0,name)
                except AttributeError: continue
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
        if item :
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
