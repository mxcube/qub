import weakref
import qt

if __name__ == "__main__" :
    a = qt.QApplication([])

import os.path

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
from Qub.Widget.QubDialog import QubInfoTableWidget,QubInfoTableDialog

from Qub.Print.QubPrintPreview import getPrintPreviewDialog

from Qub.Widget.QubMdi import QubMdiCheckIfParentIsMdi

import EdfFile
##@brief This class display all kind of 2D data image
#
#This class can display:
# - edf file -> call Qub.Widget.QubDataDisplay.setDataSource with the full path
# - spec shm -> call Qub.Widget.QubDataDisplay.setDataSource with "specversion:array_name"
# - 2D array -> call Qub.Widget.QubDataDisplay.setData with your array
#
class QubDataDisplay(qt.QWidget) :
    (QUICK_SCROLL,SUB_DATA_VIEW,PRINT_PREVIEW,SAVE_IMAGE,
     STAT_ACTION,HEADER_INFO,ZOOM,COLORMAP,CHANGE_FOREGROUND_COLOR,
     HORIZONTAL_SELECTION, VERTICAL_SELECTION,LINE_SELECTION,
     POSITION_AND_VALUE) = range(13)

    ##@brief Constuctor
    #
    #@param data :
    # - in case of spec shm data="specversion:arrayname"
    # - in case of file the file path (only Edf)
    #@param zoomValList a zoom list default [0.1,0.25,0.5,0.75,1,1.5,2]
    #@param noAction if True no action will be created
    #@param noToolbarAction if True no toolbar action will be created
    def __init__(self,parent=None,data=None,name='',
                 zoomValList = [0.1,0.25,0.5,0.75,1,1.5,2],keepROI=False,
                 noAction=False,noToolbarAction=False,**keys) :
        qt.QWidget.__init__(self,parent,name,qt.Qt.WDestructiveClose)
        
        self.__curentdata = None
        self.__roi = None
        self.__dataPlug = None
        layout = qt.QHBoxLayout(self)
        self.__mainView = QubPixmapDisplayView(parent=self)
        self.__mainView.show()
        layout.addWidget(self.__mainView)

        #LINK IMAGE 2 DISPLAY
        self.__image2Pixmap = QubImage2Pixmap()
        self.__mainviewPlug = _MainViewPlug(self.__mainView)
        self.__image2Pixmap.plug(self.__mainviewPlug)
        qt.QObject.connect(self.__mainView.view(),qt.PYSIGNAL("ContentViewChanged"),self.__mainviewPlug.setViewPortPoseNSize)
        
        #LINK RAW DATA 2 IMAGE
        self.__rawData2Image = QubRawData2Image()
        self.__ImageNViewPlug = _ImageNViewPlug(self,self.__image2Pixmap,self.__mainView)
        self.__rawData2Image.plug(self.__ImageNViewPlug)


        self.__idle = qt.QTimer(self)
        self.connect(self.__idle,qt.SIGNAL('timeout()'),self.__refresh)
                         ####### ACTION #######
        self.__actionDataActionPlug = []          # action witch need data
        self.quickScrollAction = None
        self.__posaction = 1
        self.__updateAction = None
        self.__saveDialog = None
        self.__dataStat = None
        self.__headerInfo = None
        self.__colormapDialog = None
        self.__hLineSelection = None
        self.__vLineSelection = None
        self.__lineSelection = None
        self.__dataPositionValueAction = None
        self.__zoomValList = zoomValList
        self.__keepROI = keepROI
        action_enum = []

        if not noAction:
            action_enum.extend([QubDataDisplay.QUICK_SCROLL,
                                QubDataDisplay.SUB_DATA_VIEW,
                                QubDataDisplay.HEADER_INFO,
                                QubDataDisplay.POSITION_AND_VALUE])
                        
        if not noAction and not noToolbarAction:
            action_enum.extend([QubDataDisplay.PRINT_PREVIEW,
                                QubDataDisplay.SAVE_IMAGE,
                                QubDataDisplay.STAT_ACTION,
                                QubDataDisplay.ZOOM,
                                QubDataDisplay.COLORMAP,
                                QubDataDisplay.CHANGE_FOREGROUND_COLOR,
                                QubDataDisplay.HORIZONTAL_SELECTION,
                                QubDataDisplay.VERTICAL_SELECTION,
                                QubDataDisplay.LINE_SELECTION])
        self.addStdAction(action_enum)
                
        dataArray,captionName = self.setDataSource(data)
        self.__setCaption(captionName)
        if dataArray is not None :
            self.__rawData2Image.putRawData(dataArray)
            self.setData4Action(dataArray)

    ##@brief get the drawing view for QubDrawingManager Object
    #@return a QubPixmapDisplay (Qub.Objects.QubPixmapDisplay.QubPixmapDisplay)
    def getDrawing(self) :
        return self.__mainView.view()
    ##@brief get the view to add some action
    #@return a QubPixmapDisplayView (Qub.Objects.QubPixmapDisplayView.QubPixmapDisplayView)
    def getView(self) :
        return self.__mainView
    ##@brief get the colormap controler
    #
    #This is a low level object (Qub.Objects.QubRawData2Image.QubRawData2ImagePlug.Colormap)
    def getColormapPlug(self) :
        return self.__ImageNViewPlug.colormap()
    ##@brief add an action witch need data
    #
    #@param action a QubAction
    #@param dataActionplug a class with :
    # - a methode setData (mandatory) called when source data change
    # - a methode setScaleClass (optional) to set the scale class (Qub.Data.Scale.QubDataScale.QubDataScale)
    #
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
        self.__mainView.addAction(action)
    ##@brief add standard action
    #@param action can be one or a list of this enum:
    # - QubDataDisplay.QUICK_SCROLL
    # - QubDataDisplay.SUB_DATA_VIEW
    # - QubDataDisplay.PRINT_PREVIEW
    # - QubDataDisplay.SAVE_IMAGE
    # - QubDataDisplay.STAT_ACTION
    # - QubDataDisplay.HEADER_INFO
    # - QubDataDisplay.ZOOM
    # - QubDataDisplay.COLORMAP
    # - QubDataDisplay.CHANGE_FOREGROUND_COLOR
    # - QubDataDisplay.HORIZONTAL_SELECTION
    # - QubDataDisplay.VERTICAL_SELECTION
    # - QubDataDisplay.LINE_SELECTION
    # - QubDataDisplay.POSITION_AND_VALUE
    def addStdAction(self,action_enum) :
        _,mainWidget = QubMdiCheckIfParentIsMdi(self)

        if not isinstance(action_enum,list) :
            action_enum = [action_enum]
                        ####### ACTION #######
        action_list = []
                     ####### QUICK SCROLL #######
        if QubDataDisplay.QUICK_SCROLL in action_enum :
            self.quickScrollAction = QubQuickScroll(parent=self,group="image",place="statusbar")
            action_list.append(self.quickScrollAction)
                       ####### SUB VIEW #######
        if QubDataDisplay.SUB_DATA_VIEW in action_enum:
            subDataView = QubSubDataViewAction(parent=self,group="image",place="statusbar")
            subDataView.setColormapObject(self.__ImageNViewPlug.colormap())
            self.__actionDataActionPlug.append(subDataView)
            action_list.append(subDataView)
            ####### MOUSE POSITION AND DATA VALUE #######
                     ####### PRINT ACTION #######
        if QubDataDisplay.PRINT_PREVIEW in action_enum:
            printAction = QubPrintPreviewAction(name="print",group="admin",withVectorMenu=True)
            printAction.previewConnect(getPrintPreviewDialog())
            action_list.append(printAction)
                      ####### SAVE IMAGE #######
        if QubDataDisplay.SAVE_IMAGE in action_enum:
            saveAction = QubOpenDialogAction(parent=mainWidget,label='Save image',name="save", iconName='save',group="admin")
            saveAction.setConnectCallBack(self._save_dialog_new)
            action_list.append(saveAction)
                     ####### STAT ACTION #######
        mdiParent,mainWindow = QubMdiCheckIfParentIsMdi(self)
        if QubDataDisplay.STAT_ACTION in action_enum:
            if mdiParent :
                self.__dataStat = QubDataStatWidget(parent = mdiParent)
                mdiParent.addNewChildOfMainWindow(mainWindow,self.__dataStat)
            else: self.__dataStat = QubDataStatDialog(parent = mainWidget)
            dataStatAction = QubOpenDialogAction(parent=mainWidget,name='Data statistic',iconName='histogram',group='admin')
            dataStatAction.setDialog(self.__dataStat)
            action_list.append(dataStatAction)
            self.__actionDataActionPlug.append(self.__dataStat)
                     ####### HEADER INFO #######
        if QubDataDisplay.HEADER_INFO in action_enum:
            if mdiParent:
                self.__headerInfo = QubInfoTableWidget(parent = mdiParent,iconName='datatable',name = 'Header Info')
                mdiParent.addNewChildOfMainWindow(mainWindow,self.__headerInfo)
            else: self.__headerInfo = QubInfoTableDialog(parent = mainWidget,iconName='datatable',name = 'Header Info')
            headerInfoAction = QubOpenDialogAction(parent=mainWidget,name='Header info',iconName='datatable',group='admin',
                                                   place='contextmenu')
            headerInfoAction.setDialog(self.__headerInfo)
            action_list.append(headerInfoAction)
                       ####### ZOOM LIST #######
        if QubDataDisplay.ZOOM in action_enum:
            zoomActionList = QubZoomListAction(place = "toolbar",
                                               initZoom = 1,zoomValList = self.__zoomValList,keepROI = self.__keepROI,
                                               show = 1,group = "image")
            action_list.append(zoomActionList)
                     ####### ZOOM Action #######
            self.__zoomFitOrFill = QubZoomAction(keepROI = self.__keepROI,place = "toolbar",group = "image")
            action_list.append(self.__zoomFitOrFill)

                   ####### LINK ZOOM ACTION #######
            self.__zoomFitOrFill.setList(zoomActionList)
            zoomActionList.setActionZoomMode(self.__zoomFitOrFill)
                   ####### COLORMAP ACTION #######
        if QubDataDisplay.COLORMAP in action_enum:
            colorMapAction = QubOpenDialogAction(parent=self,name='colormap',iconName='colormap',
                                                 label='ColorMap',group="color")
            action_list.append(colorMapAction)

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
        if QubDataDisplay.CHANGE_FOREGROUND_COLOR in action_enum:
            fcoloraction = QubForegroundColorAction(name="color", group="selection")
            action_list.append(fcoloraction)

        ####### Horizontal selection #######
        if QubDataDisplay.HORIZONTAL_SELECTION in action_enum:
            self.__hLineSelection = QubHLineDataSelectionAction(parent=mainWidget,group="selection")
            self.__hLineSelection.setDataZoom(self.__ImageNViewPlug.zoom())
            action_list.append(self.__hLineSelection)
            self.__actionDataActionPlug.append(self.__hLineSelection)

        ####### Vertical selection #######
        if QubDataDisplay.VERTICAL_SELECTION in action_enum:
            self.__vLineSelection = QubVLineDataSelectionAction(parent=mainWidget,group="selection")
            self.__vLineSelection.setDataZoom(self.__ImageNViewPlug.zoom())
            action_list.append(self.__vLineSelection)
            self.__actionDataActionPlug.append(self.__vLineSelection)

        ####### Line selection #######
        if QubDataDisplay.LINE_SELECTION in action_enum:
            self.__lineSelection = QubLineDataSelectionAction(parent=mainWidget,group="selection")
            self.__lineSelection.setDataZoom(self.__ImageNViewPlug.zoom())
            action_list.append(self.__lineSelection)
            self.__actionDataActionPlug.append(self.__lineSelection)

        ####### Position and Value #######
        if QubDataDisplay.POSITION_AND_VALUE in action_enum:
            self.__dataPositionValueAction = QubDataPositionValueAction(name="position",
                                                                        group="image",place="statusbar")

            self.__ImageNViewPlug.setDataPositionValue(self.__dataPositionValueAction)
            action_list.append(self.__dataPositionValueAction)

        try:
            self.__mainView.addAction(action_list)
        except:
            import traceback
            traceback.print_exc()

    ##@brief set data from an external source
    #@param data a numpy 2 dimension array
    def setData(self,data) :
        self.__rawData2Image.putRawData(data)
        self.setData4Action(data)
    ##@brief set data description
    #
    #@param data :
    # - in case of spec shm data="specversion:arrayname"
    # - in case of file the file path (Edf only)
    def setDataSource(self,data) :
        dataArray = None
        captionName = 'Data Display'
        if data:
            #test if want to poll a shm
            try:
                specv,shmname = data.split(':')
                specVersions = getSpecVersions()
                source = specVersions.getObjects(specv)
                if source :
                    self.__specShm = source.getObjects(shmname)
                    if self.__specShm is None :
                        raise StandardError("There is no shm array %s" % data)
                    

                        ####### UPDATE #######
                    needConnection = False
                    if not self.__updateAction:
                        self.__updateAction = QubToggleAction(name="update",group="image",index=0,initState=True)
                        needConnection = True
                    if self.__dataPlug:
                        qt.QObject.disconnect(self.__updateAction,qt.PYSIGNAL("StateChanged"),self.__dataPlug.updateCBK)

                    self.__dataPlug = _ShmDataPlug(self.__specShm,self.__updateAction,self)
                    self.__dataPlug.setDataReceiver(self.__rawData2Image)
                    self.__specShm.plug(self.__dataPlug)
                    
                    qt.QObject.connect(self.__updateAction,qt.PYSIGNAL("StateChanged"),self.__dataPlug.updateCBK)
                    
                    if needConnection:
                        self.__mainView.addAction([self.__updateAction])
                    self.__updateAction.setState(True)

                    captionName = 'Spec shm : %s' % data
                    self.tryReconnect = None
                else:
                    raise StandardError("Can't find the spec version %s" % specv)
            except ValueError:          # MAY BE a FILE
                captionName = 'File : %s' % os.path.split(data)[1]
                self.__file = EdfFile.EdfFile(data)
                dataArray = self.__file.GetData(0)

                if self.__updateAction :
                    self.__mainView.delAction(self.__updateAction)
                    qt.QObject.disconnect(self.__updateAction,qt.PYSIGNAL("StateChanged"),self.__dataPlug.updateCBK)
                    self.__dataPlug = None
                    self.__updateAction = None
                self.setData(dataArray)
            try:
                self.__setCaption(captionName)
            except AttributeError: pass # INIT
        return dataArray,captionName
    ##@brief set info
    #
    #@param info must be a dictionnary
    def setInfo(self,info) :
        if self.__headerInfo :
            self.__headerInfo.setInfo(info)

    ##@brief set scale class for data
    #
    #@param scaleClass usualy a Qub.Data.Scale.QubDataScale.QubDataScale
    def setScaleClass(self,scaleClass) :
        for action in self.__actionDataActionPlug :
            if hasattr(action,'setScaleClass') :
                action.setScaleClass(scaleClass)
        if self.__dataPositionValueAction:
            self.__dataPositionValueAction.setScaleClass(scaleClass)
                
    ##@brief get current data
    #@return a numpy 2 dimension array
    def getData(self) :
        return self.__curentdata

    ##@brief set data roi
    def setDataRoi(self,x,y,width,height) :
        zoomClass = self.__ImageNViewPlug.zoom()
        zoomClass.setRoiNZoom(x,y,width,height,*zoomClass.zoom())
        if self.__dataStat:
            self.__dataStat.setDataRoi(x,y,width,height)

    ##@brief set data roi
    def setDataRoiNoImg(self,x,y,width,height) :
        if self.__dataStat:
            self.__dataStat.setDataRoi(x,y,width,height)

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
        if self.__hLineSelection: self.__hLineSelection.setCaptionPrefix(name)
        if self.__vLineSelection: self.__vLineSelection.setCaptionPrefix(name)
        if self.__lineSelection: self.__lineSelection.setCaptionPrefix(name)
        if self.__colormapDialog: self.__colormapDialog.setCaptionPrefix(name)
        if self.__saveDialog: self.__saveDialog.setCaptionPrefix(name)
        if self.__dataStat: self.__dataStat.setCaption(name)
        if self.__headerInfo: self.__headerInfo.setCaption(name)
        
    ##@brief activated fit 2 screen
    def setFit2Screen(self,aFlag) :
        if self.__zoomFitOrFill:
           self.__zoomFitOrFill.setState(aFlag)
           
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
        self.__refreshFlag = True

    def setDataReceiver(self,dataReceiver) :
        self.__dataReceiver = weakref.ref(dataReceiver)

    def update(self,specVersion,specShm,dataArray) :
        if dataArray is None: return
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
            cnt = self.__cnt()
            if cnt:
                cnt._QubDataDisplay__dataPlug = None
                cnt._QubDataDisplay__specShm = None
                cnt._QubDataDisplay__mainView.delAction([cnt._QubDataDisplay__updateAction])
                cnt._QubDataDisplay__updateAction = None
                class TryReconnect:
                    def __init__(self,cnt,specSourceName) : 
                        cnt.tryReconnect = self
                        self.__specSourceName = specSourceName
                        self.__cnt = weakref.ref(cnt)

                        self.__timer = qt.QTimer(cnt)
                        qt.QObject.connect(self.__timer,qt.SIGNAL('timeout()'),self.__tryReconnect)
                        self.__timer.start(1000)
                    def __del__(self) :
                        self.__timer.stop()
                        
                    def __tryReconnect(self) :
                        cnt = self.__cnt()
                        if cnt:
                            try:
                                cnt.setDataSource(self.__specSourceName)
                            except: return

                        self.__timer.stop()
            else:
                try: self.__updateToggle().delToolWidget()
                except: pass

            TryReconnect(cnt,'%s:%s' % (specVersion.name(),self.__specShm.name()))
                            
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
        self.__dataPositionValueAction = None
        
    def setImage(self,imagezoomed,fullimage) :
        dataDisplay = self.__dataDisplay()
        if dataDisplay and not imagezoomed.isNull() and not fullimage.isNull():
            iconPixmap = qt.QPixmap(imagezoomed.smoothScale(22,22,fullimage.ScaleMin))
            dataDisplay.setIcon(iconPixmap)
            if dataDisplay.quickScrollAction :
                dataDisplay.quickScrollAction.setImageNPixmap(imagezoomed,iconPixmap)
            
        
        fulldata,resizedData = self.data()
        if resizedData is not None :
            if self.__colormapDialog: self.__colormapDialog.setData(resizedData)
            if self.__dataPositionValueAction: self.__dataPositionValueAction.setData(resizedData)
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
