import weakref
import qt
import numpy # TODO REMOVE AS SOON AS EDF MODULE USE NUMPY

if __name__ == "__main__" :
    a = qt.QApplication([])

import os.path

from Qub.Tools.QubWeakref import createWeakrefMethod

from Qub.Data.Plug.QubPlug import QubPlug
from Qub.Data.Source.QubSpecSource import getSpecVersions

from Qub.Objects.QubPixmapDisplayView import QubPixmapDisplayView

from Qub.Objects.QubImage2Pixmap import QubImage2Pixmap,QubImage2PixmapPlug
from Qub.Objects.QubRawData2Image import QubRawData2Image,QubRawData2ImagePlug

from Qub.Widget.QubActionSet import QubZoomListAction
from Qub.Widget.QubActionSet import QubZoomAction
from Qub.Widget.QubActionSet import QubOpenDialogAction
from Qub.Widget.QubActionSet import QubPrintPreviewAction
from Qub.Widget.QubActionSet import QubSubDataViewAction
from Qub.Widget.QubActionSet import QubQuickScroll
from Qub.Widget.QubActionSet import QubForegroundColorAction
from Qub.Widget.QubActionSet import QubHLineDataSelectionAction
from Qub.Widget.QubActionSet import QubVLineDataSelectionAction
from Qub.Widget.QubActionSet import QubLineDataSelectionAction
from Qub.Widget.QubActionSet import QubDataPositionValueAction

from Qub.Widget.QubAction import QubToggleAction

from Qub.Widget.QubColormap import QubColormapDialog

from Qub.Widget.QubDialog import QubSaveImageWidget,QubSaveImageDialog
from Qub.Widget.QubDialog import QubDataStatWidget,QubDataStatDialog

from Qub.Print.QubPrintPreview import getPrintPreviewDialog

from Qub.Widget.QubMdi import QubMdiCheckIfParentIsMdi

import EdfFile
##@brief This class display all kind of 2D data
#
class QubDataDisplay(qt.QWidget) :
    ##@brief Constuctor
    #
    #@param data :
    # - in case of spec shm data="specversion:arrayname"
    # - in case of file the file path
    #@param zoomValList a zoom list default [0.1,0.25,0.5,0.75,1,1.5,2]
    def __init__(self,parent=None,data=None,name='',
                 zoomValList = [0.1,0.25,0.5,0.75,1,1.5,2],**keys) :
        qt.QWidget.__init__(self,parent,name,qt.Qt.WDestructiveClose)

        self.__curentdata = None

        _,mainWidget = QubMdiCheckIfParentIsMdi(self)

        self.__dataPlug = None
        layout = qt.QHBoxLayout(self)
        self.__mainView = QubPixmapDisplayView(parent=self)
        self.__mainView.show()
        layout.addWidget(self.__mainView)

        #LINK IMAGE 2 DISPLAY
        self.__image2Pixmap = QubImage2Pixmap()
        self.__mainviewPlug = _MainViewPlug(self.__mainView)
        self.__image2Pixmap.plug(self.__mainviewPlug)

        #LINK RAW DATA 2 IMAGE
        self.__rawData2Image = QubRawData2Image()
        self.__ImageNViewPlug = _ImageNViewPlug(self,self.__image2Pixmap,self.__mainView)
        self.__rawData2Image.plug(self.__ImageNViewPlug)


        self.__idle = qt.QTimer(self)
        self.connect(self.__idle,qt.SIGNAL('timeout()'),self.__refresh)
                         ####### ACTION #######
        actions = []
        self.__actionDataActionPlug = []          # action witch need data
                     ####### QUICK SCROLL #######
        self.quickScrollAction = QubQuickScroll(parent=self,group="image",place="statusbar")
        actions.append(self.quickScrollAction)
                       ####### SUB VIEW #######
        self.__subDataView = QubSubDataViewAction(parent=self,group="image",place="statusbar")
        self.__subDataView.setColormapObject(self.__ImageNViewPlug.colormap())
        self.__actionDataActionPlug.append(self.__subDataView)
        actions.append(self.__subDataView)
            ####### MOUSE POSITION AND DATA VALUE #######
        self.__posaction = 1
        dataArray = None
        captionName = 'Data Display'
        if data:
            #test if want to poll a shm
            try:
                specv,shmname = data.split(':')
                specVersions = getSpecVersions()
                self.__source = specVersions.getObjects(specv)
                if self.__source :
                    self.__specShm = self.__source.getObjects(shmname)
                    if self.__specShm is None :
                        raise StandardError("There is no shm array %s" % data)
                    
                        ####### UPDATE #######
                    update = QubToggleAction(name="update",group="image",initState=True)
                    actions.append(update)
                    captionName = 'Spec shm : %s' % data

                    self.__dataPlug = _ShmDataPlug(self.__specShm,update,self)
                    self.__dataPlug.setDataReceiver(self.__rawData2Image)
                    self.__specShm.plug(self.__dataPlug)
                    self.connect(update,qt.PYSIGNAL("StateChanged"),self.__dataPlug.updateCBK)
                else:
                    raise StandardError("Can't find the spec version %s" % specv)
            except ValueError:          # MAY BE a FILE
                captionName = 'File : %s' % os.path.split(data)[1]
                self.__file = EdfFile.EdfFile(data)
                print "Number of Record",self.__file.GetNumImages()
                dataArray = self.__file.GetData(0)
                     ####### PRINT ACTION #######
        printAction = QubPrintPreviewAction(name="print",group="admin",withVectorMenu=True)
        printAction.previewConnect(getPrintPreviewDialog())
        actions.append(printAction)
                      ####### SAVE IMAGE #######
        self.__saveDialog = None
        saveAction = QubOpenDialogAction(parent=mainWidget,label='Save image',name="save", iconName='save',group="admin")
        saveAction.setConnectCallBack(self._save_dialog_new)
        actions.append(saveAction)
                     ####### STAT ACTION #######
        mdiParent,mainWindow = QubMdiCheckIfParentIsMdi(self)
        if mdiParent :
            self.__dataStat = QubDataStatWidget(parent = mdiParent)
            mdiParent.addNewChildOfMainWindow(mainWindow,self.__dataStat)
        else: self.__dataStat = QubDataStatDialog(parent = mainWidget)
        dataStatAction = QubOpenDialogAction(parent=mainWidget,name='Data statistic',iconName='histogram',group='admin')
        dataStatAction.setDialog(self.__dataStat)
        actions.append(dataStatAction)
        self.__actionDataActionPlug.append(self.__dataStat)
                       ####### ZOOM LIST #######
        zoomActionList = QubZoomListAction(place = "toolbar",
                                           initZoom = 1,zoomValList = zoomValList,
                                           show = 1,group = "image")
        actions.append(zoomActionList)
                     ####### ZOOM Action #######
        zoomFitOrFill = QubZoomAction(place = "toolbar",group = "image")
        actions.append(zoomFitOrFill)
        

                   ####### LINK ZOOM ACTION #######
        zoomFitOrFill.setList(zoomActionList)
        zoomActionList.setActionZoomMode(zoomFitOrFill)
                   ####### COLORMAP ACTION #######
        self.__colormapDialog = None
        colorMapAction = QubOpenDialogAction(parent=self,name='colormap',iconName='colormap',
                                             label='ColorMap',group="color")
        actions.append(colorMapAction)

        if mdiParent:
            self.__colormapDialog = QubColormapDialog(parent=mdiParent)
            mdiParent.addNewChildOfMainWindow(mainWindow,self.__colormapDialog)
        else:
            self.__colormapDialog = QubColormapDialog(parent=None)
        colorMapAction.setDialog(self.__colormapDialog)
        self.__colormapDialog.setColormapNRefreshCallBack(self.__ImageNViewPlug.colormap(),
                                                          self.refresh)
        self.__ImageNViewPlug.setColorMapDialog(self.__colormapDialog)
               ####### CHANGE FOREGROUND COLOR #######
        fcoloraction = QubForegroundColorAction(name="color", group="selection")
        actions.append(fcoloraction)

                 ####### Horizontal selection #######
        self.__hLineSelection = QubHLineDataSelectionAction(parent=mainWidget,group="selection")
        self.__hLineSelection.setDataZoom(self.__ImageNViewPlug.zoom())
        actions.append(self.__hLineSelection)
        self.__actionDataActionPlug.append(self.__hLineSelection)
                 ####### Vertical selection #######
        self.__vLineSelection = QubVLineDataSelectionAction(parent=mainWidget,group="selection")
        self.__vLineSelection.setDataZoom(self.__ImageNViewPlug.zoom())
        actions.append(self.__vLineSelection)
        self.__actionDataActionPlug.append(self.__vLineSelection)
                    ####### Line selection #######
        self.__lineSelection = QubLineDataSelectionAction(parent=mainWidget,group="selection")
        self.__lineSelection.setDataZoom(self.__ImageNViewPlug.zoom())
        actions.append(self.__lineSelection)
        self.__actionDataActionPlug.append(self.__lineSelection)
                  ####### Position and Value #######
        self.__dataPositionValueAction = QubDataPositionValueAction(name="position",
                                                                    group="image",place="statusbar")

        self.__ImageNViewPlug.setDataPositionValue(self.__dataPositionValueAction)
        actions.append(self.__dataPositionValueAction)

        try:
            self.__mainView.addAction(actions)
        except:
            import traceback
            traceback.print_exc()
        self.__setCaption(captionName)
        if dataArray is not None :
            self.__rawData2Image.putRawData(dataArray)
            self.setData4Action(dataArray)

        
    def __del__(self) :
        if self.__dataPlug:
            self.__specShm.unplug(self.__dataPlug)

    ##@brief get the drawing view for QubDrawingManager Object
    #@return a QubPixmapDisplay
    def getDrawing(self) :
        return self.__mainView.view()
    ##@brief get the view to add some action
    #@return a QubPixmapDisplayView
    def getView(self) :
        return self.__mainView
    ##@brief add an action witch need data
    #
    #@param action a QubAction
    #@param dataActionplug a class with a methode setData
    def addDataAction(self,action,dataActionplug) :
        self.__mainView.addAction([action])
        self.__actionDataActionPlug.append(dataActionplug)
        dataActionplug.setData(self.__curentdata)
    ##@brief add a simple action which doesn't need data
    #
    #@param action one or a list of QubAction
    def addAction(self,action) :
        if not isinstance(action,list) :
            action = [action]
        self.__mainView.addDataAction(action)
    ##@brief set data from an external source
    #@param data a numpy 2 dimension array
    def setData(self,data) :
        self.__rawData2Image.putRawData(data)
        self.setData4Action(data)
    
    ##@brief set data to all action which need it
    #
    #Dont call this methode (internal call)
    #@see setData
    def setData4Action(self,data) :
        self.__curentdata = data
        for action in self.__actionDataActionPlug :
            try:
                action.setData(data)
            except:
                import traceback
                traceback.print_exc()
    ##@brief set caption for windows and subwindows
    def setCaption(self,name):
        qt.QWidget.setCaption(self,name)
        self.__setCaption(name)
    ##@brief Caption Window
    def __setCaption(self,name) :
        if isinstance(name,qt.QString) :
            name = name.latin1()
        qt.QWidget.setCaption(self,name)
        self.__hLineSelection.setCaptionPrefix(name)
        self.__vLineSelection.setCaptionPrefix(name)
        self.__lineSelection.setCaptionPrefix(name)
        self.__colormapDialog.setCaptionPrefix(name)
        self.__saveDialog.setCaptionPrefix(name)
        self.__dataStat.setCaption(name)
        
    def resizeEvent(self,event):
        try:
            sMode = self.__mainView.view().scrollbarMode()
            if sMode == "Fit2Screen" or sMode == "FillScreen":
                self.refresh()
        except AttributeError,err:
            pass

    def closeEvent(self,ev) :
        parent = self.parent()
        while parent :
            if hasattr(parent,'windowList') :
                break
            parent = parent.parent()
        if parent:
            for window in parent.windowList() :
                if window == self:
                    window.close(1)
        else:
            self.close(1)
        ev.accept()

    def __refresh(self) :
        self.__idle.stop()
        self.__ImageNViewPlug.refresh()
        
    def refresh(self) :
        try:
            if not self.__idle.isActive() :
                self.__idle.start(0)
        except AttributeError,err:
            pass

    def _save_dialog_new(self,openDialogAction,aQubImage) :
        mdiParent,mainWindow = QubMdiCheckIfParentIsMdi(self)
        if mdiParent:
            self.__saveDialog = QubSaveImageWidget(parent=mdiParent,canvas=aQubImage.canvas(),matrix=aQubImage.matrix())
            mdiParent.addNewChildOfMainWindow(mainWindow,self.__saveDialog)
        else:
            self.__saveDialog = QubSaveImageDialog(self,canvas=aQubImage.canvas(),matrix=aQubImage.matrix())
        self.__saveDialog.setImage2Pixmap(self.__image2Pixmap)
        self.__saveDialog.setDataZoom(self.__ImageNViewPlug.zoom())
        openDialogAction.setDialog(self.__saveDialog)

                ############### PLUGS ###############
            
class _ShmDataPlug(QubPlug) :
    def __init__(self,specShm,updateToggle,cnt) :
        QubPlug.__init__(self,200)      # 5 image/second max
        self.__dataReceiver = None
        self.__specShm = specShm
        self.__cnt = weakref.ref(cnt)
        self.__updateToggle = weakref.ref(updateToggle)

    def setDataReceiver(self,dataReceiver) :
        self.__dataReceiver = weakref.ref(dataReceiver)

    def update(self,specVersion,specShm,dataArray) :
        aEndFlag = False
        if self.__refreshFlag:
            dataReceiver = self.__dataReceiver()
            cnt = self.__cnt()
            if cnt and dataReceiver:
                dataReceiver.putRawData(dataArray)
                cnt.setData4Action(dataArray)
            else: aEndFlag = True
        return aEndFlag

    def updateCBK(self,onOff) :
        self.__refreshFlag = onOff
        if onOff:
            self.update(self.__specShm.container(),self.__specShm,self.__specShm.getSpecArray())
        
    def destroy(self,specVersion,shmObjects) :
        aEndFlag = False
        if self.__specShm.name() in shmObjects :
            aEndFlag = True
            try: self.__updateToggle().delToolWidget()
            except: pass
        return aEndFlag

class _MainViewPlug(QubImage2PixmapPlug) :
    def __init__(self,receiver) :
        QubImage2PixmapPlug.__init__(self)
        self.__receiver = weakref.ref(receiver)

    def setPixmap(self,pixmap,image) :
        try:
            self.__receiver().setPixmap(pixmap,image)
        except:
            pass
        return False

class _ImageNViewPlug(QubRawData2ImagePlug) :
    def __init__(self,dataDisplay,image2Pixmap,mainView) :
        QubRawData2ImagePlug.__init__(self)
        mainView.setPixmapPlug(self)
        self.__receiver = weakref.ref(image2Pixmap)
        self.__colormapDialog = None
        self.__dataDisplay = weakref.ref(dataDisplay)
        
    def setImage(self,imagezoomed,fullimage) :
        dataDisplay = self.__dataDisplay()
        if dataDisplay:
            iconPixmap = qt.QPixmap(imagezoomed.smoothScale(22,22,fullimage.ScaleMin))
            dataDisplay.setIcon(iconPixmap)
            dataDisplay.quickScrollAction.setImageNPixmap(imagezoomed,iconPixmap)
            
        if self.__colormapDialog:
            fulldata,resizedData = self.data()
            self.__colormapDialog.update(resizedData)
            self.__dataPositionValueAction.setData(resizedData)
        receiver = self.__receiver()
        if receiver:
            receiver.putImage(imagezoomed,fullimage)
        return False

    def setColorMapDialog(self,colorMapDialog) :
        self.__colormapDialog = colorMapDialog
        fulldata,resizedData = self.data()
            
    def setDataPositionValue(self,dataValuePosition) :
        self.__dataPositionValueAction = dataValuePosition




if __name__ == "__main__" :
    import qt
    import sys
    if len(sys.argv) < 2:
        print sys.argv,"<filepath> or specversion:shmname"
        sys.exit(0)
    widgets = []
    for arg in sys.argv[1:] :
        try:
            w = QubDataDisplay(data=arg,withSubZoom = True)
            w.show()
            widgets.append(w)
        except :
            import traceback
            traceback.print_exc()
    if widgets :
        qt.QObject.connect(a, qt.SIGNAL("lastWindowClosed()"),
                           a, qt.SLOT("quit()"))
        a.exec_loop()
