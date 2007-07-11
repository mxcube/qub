###############################################################################
###############################################################################
####################                                       ####################
####################         Miscallenous Dialog           ####################
####################                                       ####################
###############################################################################
###############################################################################
import qt
import qtcanvas
import glob
import sys
import os.path

from Qub.Icons.QubIcons import loadIcon

####################################################################
##########                                                ##########
##########                 file dialog                    ##########
##########                                                ##########
####################################################################\
from Qub.CTools import qttools

class QubFileDialog(qt.QDialog):

    (ShowAll, ShowDir) = (0, 1)
    (SelectAny, SelectFile, SelectDir) = (0, 1, 2)
    (SelectAll, SelectExist, SelectNew) = (0, 1, 2)
    
    def __init__(self, startdir=".", filtre="*",
                 showMode=ShowAll, selectMode=SelectAny, fileMode=SelectAll):
        qt.QDialog.__init__(self, None, "Qub File Selector")
        
        self.showMode =   showMode
        self.selectMode = selectMode
        self.fileMode =   fileMode
        
        self.resize(600, 400)
        
        self.__buildInterface()
        
        self.qdir = qt.QDir(startdir, filtre)
        
        cleanDir = self.qdir.cleanDirPath(self.qdir.path())
        self.__setDirectory(cleanDir)
        self.dirCombo.insertItem(cleanDir, -1)
        
        self.filterCombo.insertItem(filtre, -1)
    
    ####################################################################
    ##########               Public method                    ##########    
    ####################################################################
    def __setDirectory(self, path):
        self.qdir.setPath(path)
        self.selectionText.setText("")
        
        allList = self.qdir.entryInfoList()
        fileList = []
        itemList = []
        self.fileList = {}
        
        self.iconView.clear()
        
        if allList is not None:
            
            for elem in allList:           
                if elem.isDir():
                    if elem.isSymLink():
                        iconFile = "file_link_dir.xpm"
                    else:
                        iconFile = "file_dir.xpm"
                    itemList.append(qt.QIconViewItem(self.iconView,
                                                     elem.fileName(), 
                                                     loadIcon(iconFile)))
                else:
                    if self.showMode == QubFileDialog.ShowAll:
                        fileList.append(elem)
            
            if self.showMode == QubFileDialog.ShowAll:
                for elem in fileList:
                    if elem.isSymLink():
                        iconFile = "file_link_file.xpm"
                    else:
                        iconFile = "file_file.xpm"
                    itemList.append(qt.QIconViewItem(self.iconView, elem.fileName(), 
                                        loadIcon(iconFile)))

            for elem in allList:
                self.fileList[str(elem.fileName())] = elem

            for item in itemList:
                item.setDragEnabled(False)
        
    def __dirChanged(self, ind):
        newdir = self.dirCombo.text(ind)
        self.__setDirectory(newdir)
        
    def __goBackDirectory(self):
        currentIndex = self.dirCombo.currentItem()
        
        if currentIndex != 0:
            newdir = self.dirCombo.text(currentIndex-1)
            self.__setDirectory(newdir)
            self.dirCombo.setCurrentItem(currentIndex-1)
            
    def __goUpDirectory(self):
        self.qdir.cdUp()
        cleanDir = self.qdir.cleanDirPath(self.qdir.path())
        self.__setDirectory(cleanDir)
        self.dirCombo.insertItem(cleanDir, -1)
        self.dirCombo.setCurrentItem(self.dirCombo.count()-1)
            
    def __goDownDirectory(self, directory):
        cleanDir = self.qdir.cleanDirPath(directory)
        self.__setDirectory(cleanDir)
        self.dirCombo.insertItem(cleanDir, -1)
        self.dirCombo.setCurrentItem(self.dirCombo.count()-1)
    
    def __iconViewDoubleClick(self, item):
        filename = item.text()
        
        itemFile = self.fileList[str(filename)]
        
        if not itemFile.isFile():
            self.__goDownDirectory(itemFile.filePath())
            
    def __selectionChanged(self, item):
        filename = item.text()
        itemFile = self.fileList[str(filename)]
        
        self.selectionChanged(str(filename), itemFile)
           
    def __buildInterface(self):
        fixedPolicy=qt.QSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        
        vlayout = qt.QVBoxLayout(self)
        vlayout.setMargin(5)
        vlayout.setSpacing(5)
        
        hlayout1 = qt.QHBoxLayout(vlayout)
        

        label = qt.QLabel("Look in:", self)
        label.setSizePolicy(fixedPolicy)
        hlayout1.addWidget(label)
        
        self.dirCombo = qt.QComboBox(self)
        self.dirCombo.setEditable(True)
        self.connect(self.dirCombo, qt.SIGNAL("activated(int)"),
                     self.__dirChanged)
        hlayout1.addWidget(self.dirCombo)
        
        self.backButton = qt.QToolButton(self)
        self.backButton.setAutoRaise(True)
        self.backButton.setSizePolicy(fixedPolicy)
        self.backButton.setIconSet(qt.QIconSet(loadIcon("file_back.xpm")))
        qt.QToolTip.add(self.backButton, "Go last directory")
        self.connect(self.backButton, qt.SIGNAL("clicked()"),
                     self.__goBackDirectory)
        hlayout1.addWidget(self.backButton)
        
        self.upButton = qt.QToolButton(self)
        self.upButton.setAutoRaise(True)
        self.upButton.setSizePolicy(fixedPolicy)
        self.upButton.setIconSet(qt.QIconSet(loadIcon("file_cdtoparent.xpm")))
        qt.QToolTip.add(self.upButton, "Go upper directory")
        self.connect(self.upButton, qt.SIGNAL("clicked()"),
                     self.__goUpDirectory)
        hlayout1.addWidget(self.upButton)
        
        self.iconView = qt.QIconView(self)
        self.iconView.setItemTextPos(qt.QIconView.Right)
        self.iconView.setResizeMode(qt.QIconView.Adjust)
        self.iconView.setArrangement(qt.QIconView.TopToBottom)
        self.iconView.setWordWrapIconText(False)
        self.iconView.setVScrollBarMode(qt.QScrollView.AlwaysOff)
        self.connect(self.iconView, qt.SIGNAL("doubleClicked(QIconViewItem *)"),
                     self.__iconViewDoubleClick)
        self.connect(self.iconView, qt.SIGNAL("selectionChanged(QIconViewItem *)"),
                     self.__selectionChanged)
        vlayout.addWidget(self.iconView)
        
        hlayout2 = qt.QHBoxLayout(vlayout)
        
        vlayout1 = qt.QVBoxLayout(hlayout2)
        
        self.selectionLabel = qt.QLabel("Selection", self)
        vlayout1.addWidget(self.selectionLabel)
        
        label = qt.QLabel("File type:", self)
        vlayout1.addWidget(label)
        
        vlayout2 = qt.QVBoxLayout(hlayout2)
        
        self.selectionText = qt.QLineEdit(self)
        vlayout2.addWidget(self.selectionText)
        
        self.filterCombo = qt.QComboBox(self)
        vlayout2.addWidget(self.filterCombo)
        
        vlayout3 = qt.QVBoxLayout(hlayout2)
        
        self.okButton = qt.QPushButton("Ok", self)
        self.connect(self.okButton, qt.SIGNAL("clicked()"),
                     self.okCallback)
        vlayout3.addWidget(self.okButton)
        
        self.cancelButton = qt.QPushButton("Cancel", self)
        self.connect(self.cancelButton, qt.SIGNAL("clicked()"),
                     self.cancelCallback)
        vlayout3.addWidget(self.cancelButton)

    ####################################################################
    ##########               Public method                    ##########    
    ####################################################################
    """
    OK button has been selected
    To change the behaviour of the QubFileDialog reimplement this function
    """        
    def okCallback(self):
        filename = self.selectionText.text()
        
        if str(filename) == "":
            errMsg = 'No File Selected'%filename
            qt.QMessageBox.warning(None, "File Selection", errMsg) 
        else:
            path = self.qdir.path()
            fpath = path + "/" + filename
            if self.fileMode == QubFileDialog.SelectAll:
                self.selection = fpath
                self.accept()
            elif self.fileMode == QubFileDialog.SelectExist:
                if self.qdir.exists(fpath, True):
                    self.selection = fpath
                    self.accept()
                else:
                    errMsg = 'File %s does not exist'%filename
                    qt.QMessageBox.warning(None, "File Selection", errMsg)
            else:
                if self.qdir.exists(fpath, True):
                    errMsg = 'File %s already exists'%filename
                    qt.QMessageBox.warning(None, "File Selection", errMsg)
                else:
                    self.selection = fpath
                    self.accept()
        
    def cancelCallback(self):
        self.reject()
        
    """
    a new file or directory has been selected    
    the parameter is a QFileInfo element.
    To change the behaviour of the QubFileDialog reimplement this function
    """
    def selectionChanged(self, filename, itemFile):
        
        if itemFile.isFile() and self.fileMode != QubFileDialog.SelectNew:
            if self.selectMode == QubFileDialog.SelectAny or \
               self.selectMode == QubFileDialog.SelectFile:
                self.selectionText.setText(filename)
        
        if itemFile.isDir() and self.fileMode != QubFileDialog.SelectNew:
            if self.selectMode == QubFileDialog.SelectAny or \
               self.selectMode == QubFileDialog.SelectDir:
                self.selectionText.setText(filename)
                   
    def selectedFile(self):
        return self.selection
        
    def setOkButton(self, text):
        self.okButton.setText(text)
        
    def setLabelSelection(self, text):
        self.selectionLabel.setText(text)


########################################################################
##########               Convenience Functions                ##########            
########################################################################
def QubGetDirectory(startDir, filtre):
    qt_resolve_links_old = qttools.qttools.get_qt_resolve_symlinks()

    dialog = QubFileDialog(startDir, filtre,
                           QubFileDialog.ShowDir,
                           QubFileDialog.SelectDir,
                           QubFileDialog.SelectAll)
    dialog.setLabelSelection("Selected Directory")
    
    qttools.qttools.set_qt_resolve_symlinks(qt_resolve_links_old)
    
    if dialog.exec_loop() == qt.QDialog.Accepted:
        return dialog.selectedFile()
                           
    return None
        
def QubGetNewDirectory(startDir, filtre):
    qt_resolve_links_old = qttools.qttools.get_qt_resolve_symlinks()

    dialog = QubFileDialog(startDir, filtre,
                           QubFileDialog.ShowDir,
                           QubFileDialog.SelectDir,
                           QubFileDialog.SelectNew)
    dialog.setLabelSelection("New Directory")
    
    qttools.qttools.set_qt_resolve_symlinks(qt_resolve_links_old)
    
    if dialog.exec_loop() == qt.QDialog.Accepted:
        return dialog.selectedFile()
                           
    return None
    
def QubGetFile(startDir, filtre):
    qt_resolve_links_old = qttools.qttools.get_qt_resolve_symlinks()

    dialog = QubFileDialog(startDir, filtre,
                           QubFileDialog.ShowAll,
                           QubFileDialog.SelectFile,
                           QubFileDialog.SelectAll)
    dialog.setLabelSelection("Selected File")
    
    qttools.qttools.set_qt_resolve_symlinks(qt_resolve_links_old)
    
    if dialog.exec_loop() == qt.QDialog.Accepted:
        return dialog.selectedFile()
                           
    return None
    
def QubGetNewFile(startDir, filtre):
    qt_resolve_links_old = qttools.qttools.get_qt_resolve_symlinks()

    dialog = QubFileDialog(startDir, filtre,
                           QubFileDialog.ShowAll,
                           QubFileDialog.SelectFile,
                           QubFileDialog.SelectNew)
    dialog.setLabelSelection("New File")
    
    qttools.qttools.set_qt_resolve_symlinks(qt_resolve_links_old)
    
    if dialog.exec_loop() == qt.QDialog.Accepted:
        return dialog.selectedFile()
                           
    return None
    
def QubGetZapRadix(startDir, filtre):
    qt_resolve_links_old = qttools.qttools.get_qt_resolve_symlinks()

    dialog = QubFileDialog(startDir, filtre,
                           QubFileDialog.ShowAll,
                           QubFileDialog.SelectDir,
                           QubFileDialog.SelectNew)
    dialog.setLabelSelection("Zap Radix")
    
    qttools.qttools.set_qt_resolve_symlinks(qt_resolve_links_old)
    
    if dialog.exec_loop() == qt.QDialog.Accepted:
        return dialog.selectedFile()
                           
    return None
 
        
################################################################################
####################    TEST --                   -- TEST   ####################
################################################################################
from Qub.Icons.QubIcons import loadIcon
class QubMain(qt.QMainWindow):
    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent)

        self.resize(500, 100)

        container = qt.QWidget(self)
        self.setCentralWidget(container)
        
        gridlayout = qt.QGridLayout(container, 6, 3)
        gridlayout.setSpacing(5)
        gridlayout.setMargin(5)
        
        label = qt.QLabel("Select Directory", container)
        labelSize = label.sizeHint()
        label.setMaximumSize(labelSize)
        gridlayout.addWidget(label, 0, 0)
        self.dirLabel = qt.QLabel(container)
        gridlayout.addWidget(self.dirLabel, 0, 1)        
        self.dirButton = qt.QToolButton(container)
        self.dirButton.setIconSet(qt.QIconSet(loadIcon("fileopen.png")))
        buttonSize = self.dirButton.sizeHint()
        self.dirButton.setMaximumSize(buttonSize)
        self.connect(self.dirButton, qt.SIGNAL("clicked()"), 
                     self.changeDirectory)
        gridlayout.addWidget(self.dirButton, 0, 2)
        
        label = qt.QLabel("New Directory", container)
        label.setMaximumSize(labelSize)
        gridlayout.addWidget(label, 1, 0)
        self.newDirLabel = qt.QLabel(container)
        gridlayout.addWidget(self.newDirLabel, 1, 1)        
        self.newDirButton = qt.QToolButton(container)
        self.newDirButton.setIconSet(qt.QIconSet(loadIcon("fileopen.png")))
        self.newDirButton.setMaximumSize(buttonSize)
        self.connect(self.newDirButton, qt.SIGNAL("clicked()"), 
                     self.changeNewDirectory)
        gridlayout.addWidget(self.newDirButton, 1, 2)
        
        label = qt.QLabel("Select File", container)
        label.setMaximumSize(labelSize)
        gridlayout.addWidget(label, 2, 0)
        self.fileLabel = qt.QLabel(container)
        gridlayout.addWidget(self.fileLabel, 2, 1)        
        self.fileButton = qt.QToolButton(container)
        self.fileButton.setIconSet(qt.QIconSet(loadIcon("fileopen.png")))
        self.fileButton.setMaximumSize(buttonSize)
        self.connect(self.fileButton, qt.SIGNAL("clicked()"), 
                     self.changeFile)
        gridlayout.addWidget(self.fileButton, 2, 2)
        
        label = qt.QLabel("New File", container)
        label.setMaximumSize(labelSize)
        gridlayout.addWidget(label, 3, 0)
        self.newFileLabel = qt.QLabel(container)
        gridlayout.addWidget(self.newFileLabel, 3, 1)        
        self.newFileButton = qt.QToolButton(container)
        self.newFileButton.setIconSet(qt.QIconSet(loadIcon("fileopen.png")))
        self.newFileButton.setMaximumSize(buttonSize)
        self.connect(self.newFileButton, qt.SIGNAL("clicked()"), 
                     self.changeNewFile)
        gridlayout.addWidget(self.newFileButton, 3, 2)
        
        label = qt.QLabel("Zap Radix", container)
        label.setMaximumSize(labelSize)
        gridlayout.addWidget(label, 4, 0)
        self.zapRadixLabel = qt.QLabel(container)
        gridlayout.addWidget(self.zapRadixLabel, 4, 1)        
        self.zapRadixButton = qt.QToolButton(container)
        self.zapRadixButton.setIconSet(qt.QIconSet(loadIcon("fileopen.png")))
        self.zapRadixButton.setMaximumSize(buttonSize)
        self.connect(self.zapRadixButton, qt.SIGNAL("clicked()"), 
                     self.changeZapRadix)
        gridlayout.addWidget(self.zapRadixButton, 4, 2)
        
        label = qt.QLabel("Qt File", container)
        label.setMaximumSize(labelSize)
        gridlayout.addWidget(label, 5, 0)
        self.qtFileLabel = qt.QLabel(container)
        gridlayout.addWidget(self.qtFileLabel, 5, 1)        
        self.qtFileButton = qt.QToolButton(container)
        self.qtFileButton.setIconSet(qt.QIconSet(loadIcon("fileopen.png")))
        self.qtFileButton.setMaximumSize(buttonSize)
        self.connect(self.qtFileButton, qt.SIGNAL("clicked()"), 
                     self.changeQtFile)
        gridlayout.addWidget(self.qtFileButton, 5, 2)
        
    def changeDirectory(self):
        qfilename = QubGetDirectory("/bliss/users/berruyer", "*")        
        if qfilename is not None:
            self.dirLabel.setText(qfilename)
        
    def changeNewDirectory(self):
        qfilename = QubGetNewDirectory("/bliss/users/berruyer", "*")        
        if qfilename is not None:
            self.newDirLabel.setText(qfilename)
        
    def changeFile(self):
        qfilename = QubGetFile("/bliss/users/berruyer", "*") 
        if qfilename is not None:
            self.fileLabel.setText(qfilename)
        
    def changeNewFile(self):
        qfilename = QubGetNewFile("/bliss/users/berruyer", "*") 
        if qfilename is not None:
            self.newFileLabel.setText(qfilename)
        
    def changeZapRadix(self):
        qfilename = QubGetZapRadix("/bliss/users/berruyer", "*")        
        if qfilename is not None:
            self.zapRadixLabel.setText(qfilename)
        
    def changeQtFile(self):
        qfilename = qt.QFileDialog.getOpenFileName("/bliss/users/berruyer/tmp",
                            "*", None)
        if qfilename is not None:
            self.qtFileLabel.setText(qfilename)
        
               
##  MAIN   
if  __name__ == '__main__':    
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubMain()
    
    window.resize(500,100)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
