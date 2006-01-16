import qt
import os

from Qub.Icons.QubIcons import loadIcon

        
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
        
    """
    MDI WINDOW MANAGER                      
    """
    def windowCascade(self):
        """
        """
        self.__disconnectFollow()

        self.cascade()
        for window in self.windowList():
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
        if not len(self.windowList()): 
            return

        windowHeight=float(self.height())/len(self.windowList())
        i=0
        for window in self.windowList():
            window.parentWidget().showNormal()
            window.parentWidget().setGeometry(0, int(windowHeight*i),
                                        self.width(),int(windowHeight))
            window.parentWidget().raiseW()
            i+=1

        self.update()

    def windowVertical(self):
        """
        """
        if not len(self.windowList()):
            return

        windowWidth = float(self.width()) / len(self.windowList())
        i=0
        for window in self.windowList():
            window.parentWidget().showNormal()
            window.parentWidget().setGeometry(int(windowWidth*i),0,
                                            int(windowWidth),self.height())
            window.parentWidget().raiseW()
            i+=1
            
        self.update()

    def windowFullScreen(self):
        """
        """
        if len(self.windowList()):
            self.activeWindow().showMaximized()

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

        num= 0
        self.menuWindowMap= {}
        for window in self.windowList():
            auxStr = "&%d %s"%(num, str(window.caption()))
            idx = self.menuWindow.insertItem(auxStr,
                                             self.__activateWindowMenu)
            self.menuWindowMap[idx] = window
            num += 1
            if  window == self.activeWindow():
                self.menuWindow.setItemChecked(idx, 1)

    def __activateWindowMenu(self, idx):
        """
        """
        self.menuWindowMap[idx].setFocus()

    """
    WINDOW TOOLBAR                      
    """
    def addWindowToolBar(self, mainwin):
        """
        """
        self.winToolBar= qt.QToolBar(mainwin, "wintoolbar")
        self.winToolBar.setLabel("MDI")
        
        icon = qt.QIconSet(loadIcon("fullscreen.png"))
        self.fullscreen = qt.QToolButton(icon, "Full Screen",
                                None, 
                                self.windowFullScreen,
                                self.winToolBar,
                                "fullscreen")
                                
        icon = qt.QIconSet(loadIcon("nofullscreen.png"))
        self.winToolButton = qt.QToolButton(icon, "Tile",
                                        None,
                                        self.onWinToolAction,
                                        self.winToolBar,
                                        "wintile")
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
        if act==0:	self.winToolMenuAction= self.windowCascade
        elif act==1:	self.winToolMenuAction= self.windowTile
        elif act==2:	self.winToolMenuAction= self.windowHorizontal
        elif act==3:	self.winToolMenuAction= self.windowVertical
        self.onWinToolAction()

    def onWinToolAction(self):
        """
        """
        apply(self.winToolMenuAction, ())
    
        
################################################################################
####################             QubMdiChild                ####################
################################################################################
class QubMdiChild(qt.QWidget):
    """
    Parent window must be a QWorkspace
    """
    def __init__(self, parent=None, name=None, master=None,
                      flags=qt.Qt.WDestructiveClose):
        
        """
        """
        qt.QWidget.__init__(self, parent, name, flags)
        self.parentWindow = parent
        self.masterWindow = master
        self.name = name
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
        for window in self.parentWindow.windowList():
            if window.masterWindow is self:
                window.close(1)
        ce.accept()
    
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
