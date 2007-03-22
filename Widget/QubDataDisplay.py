import weakref
import qt
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
from Qub.Widget.QubActionSet import QubForegroundColorAction
from Qub.Widget.QubActionSet import QubHLineDataSelectionAction
from Qub.Widget.QubActionSet import QubVLineDataSelectionAction
from Qub.Widget.QubActionSet import QubLineDataSelectionAction
from Qub.Widget.QubActionSet import QubDataPositionValueAction

from Qub.Widget.QubAction import QubToggleAction

from Qub.Widget.QubColormap import QubColormapDialog

from Qub.Widget.QubDialog import QubSaveImageWidget,QubSaveImageDialog

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
    def __init__(self,parent=None,data=None,name='',**keys) :
        qt.QWidget.__init__(self,parent,name,qt.Qt.WDestructiveClose)

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
        self.__ImageNViewPlug = _ImageNViewPlug(self.__image2Pixmap,self.__mainView)
        self.__rawData2Image.plug(self.__ImageNViewPlug)


        self.__idle = qt.QTimer(self)
        self.connect(self.__idle,qt.SIGNAL('timeout()'),self.__refresh)
                         ####### ACTION #######
        actions = []
                       ####### SUB VIEW #######
        self.__subDataView = QubSubDataViewAction(parent=self,group="image",place="statusbar")
        self.__subDataView.setColormapObject(self.__ImageNViewPlug.colormap())

        actions.append(self.__subDataView)
            ####### MOUSE POSITION AND DATA VALUE #######
        self.__posaction = 1
        dataArray = None
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
                    captionName = 'Spec Array : %s' % data

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

                       ####### ZOOM LIST #######
        zoomActionList = QubZoomListAction(place = "toolbar",
                                           initZoom = 1,zoomValList = [0.1,0.25,0.5,0.75,1,1.5,2],
                                           show = 1,group = "image")
        actions.append(zoomActionList)
                     ####### ZOOM Action #######
        zoomFitOrFill = QubZoomAction(place = "toolbar",keepROI = True,group = "image")
        actions.append(zoomFitOrFill)
                   ####### LINK ZOOM ACTION #######
        zoomFitOrFill.setList(zoomActionList)
        zoomActionList.setActionZoomMode(zoomFitOrFill)

        self.__colormapDialog = None
        colorMapAction = QubOpenDialogAction(parent=self,name='colormap',iconName='colormap',
                                             label='ColorMap',group="color")
        colorMapAction.setConnectCallBack(self.__colorMap_dialog_new)
        actions.append(colorMapAction)

                     ####### PRINT ACTION #######
        printAction = QubPrintPreviewAction(name="print",group="admin")
        printAction.previewConnect(getPrintPreviewDialog())
        actions.append(printAction)
                              ####### SAVE IMAGE #######
        self.__saveDialog = None
        saveAction = QubOpenDialogAction(parent=mainWidget,label='Save image',name="save", iconName='save',group="admin")
        saveAction.setConnectCallBack(self._save_dialog_new)
        actions.append(saveAction)
               ####### CHANGE FOREGROUND COLOR #######
        fcoloraction = QubForegroundColorAction(name="color", group="selection")
        actions.append(fcoloraction)

                 ####### Horizontal selection #######
        self.__hLineSelection = QubHLineDataSelectionAction(parent=mainWidget,group="selection")
        self.__hLineSelection.setDataZoom(self.__ImageNViewPlug.zoom())
        actions.append(self.__hLineSelection)
                 ####### Vertical selection #######
        self.__vLineSelection = QubVLineDataSelectionAction(parent=mainWidget,group="selection")
        self.__vLineSelection.setDataZoom(self.__ImageNViewPlug.zoom())
        actions.append(self.__vLineSelection)
                    ####### Line selection #######
        self.__lineSelection = QubLineDataSelectionAction(parent=mainWidget,group="selection")
        self.__lineSelection.setDataZoom(self.__ImageNViewPlug.zoom())
        actions.append(self.__lineSelection)
                  ####### Position and Value #######
        self.__dataPositionValueAction = QubDataPositionValueAction(name="position",
                                                                    group="image",place="statusbar")

        self.__ImageNViewPlug.setDataPositionValue(self.__dataPositionValueAction)
        actions.append(self.__dataPositionValueAction)


        self.__mainView.addAction(actions)
        self.__setCaption(captionName)
        if dataArray :
            self.__rawData2Image.putRawData(dataArray)
            self.setData(dataArray)

    def __del__(self) :
        if self.__dataPlug:
            self.__specShm.unplug(self.__dataPlug)
            
    ##@brief set data to all action which need it
    def setData(self,data) :
        self.__subDataView.setData(data)
        self.__hLineSelection.setData(data)
        self.__vLineSelection.setData(data)
        self.__lineSelection.setData(data)
        
    ##@brief Caption Window
    def __setCaption(self,name) :
        self.setCaption(name)
        self.__hLineSelection.setCaptionPrefix(name)
        self.__vLineSelection.setCaptionPrefix(name)
        self.__lineSelection.setCaptionPrefix(name)
        self.__colormapDialog.setCaptionPrefix(name)
        self.__saveDialog.setCaptionPrefix(name)
        
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

##        import gc
##        for variable in [self.__rawData2Image] :
##            print variable
##            for obj in gc.get_referrers(variable) :
##                print obj
##                print '---------------'
##            import sys
##            print sys.getrefcount(variable)

    def __refresh(self) :
        self.__idle.stop()
        self.__ImageNViewPlug.refresh()
        
    def refresh(self) :
        try:
            if not self.__idle.isActive() :
                self.__idle.start(0)
        except AttributeError,err:
            pass

    def __colorMap_dialog_new(self,openDialogAction,aQubImage) :
        try:
            mdiParent,mainWindow = QubMdiCheckIfParentIsMdi(self)
            if mdiParent:
                self.__colormapDialog = QubColormapDialog(parent=mdiParent)
                mdiParent.addNewChildOfMainWindow(mainWindow,self.__colormapDialog)
            else:
                self.__colormapDialog = QubColormapDialog(parent=None)
                
            openDialogAction.setDialog(self.__colormapDialog)
            self.__colormapDialog.setColormapNRefreshCallBack(self.__ImageNViewPlug.colormap(),
                                                              self.refresh)
            self.__ImageNViewPlug.setColorMapDialog(self.__colormapDialog)
        except:
            import traceback
            traceback.print_exc()

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
        QubPlug.__init__(self)
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
                cnt.setData(dataArray)
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
    def __init__(self,image2Pixmap,mainView) :
        QubRawData2ImagePlug.__init__(self)
        mainView.setPixmapPlug(self)
        self.__receiver = weakref.ref(image2Pixmap)
        self.__colormapDialog = None

    def setImage(self,imagezoomed,fullimage) :
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
            w = QubDataDisplay(data=arg)
            w.show()
            widgets.append(w)
        except :
            import traceback
            traceback.print_exc()
    if widgets :
        qt.QObject.connect(a, qt.SIGNAL("lastWindowClosed()"),
                           a, qt.SLOT("quit()"))
        a.exec_loop()
