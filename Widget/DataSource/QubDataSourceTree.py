import weakref

import qt

from Qub.Data.Source import QubInputType

from Qub.Data.Class.QubDataClass import QubDataContainerClass,QubDataGroup

from Qub.Widget.QubDataDisplay import QubDataDisplay

from Qub.Widget.QubActionSet import QubSliderNSpinAction

##@brief this class is a container for data source widget
#
#To display data source in that tree you have to interface it with the
#QubDataSourceTreeItem
#@param refresh_time the time between 2 refresh
class QubDataSourceTree(qt.QListView) :
    def __init__(self,parent = None,name = "",f = 0,refresh_time = 2000,mdi = None,**keys) :
        qt.QListView.__init__(self,parent,name,f)
        self.__refreshTimer = qt.QTimer()
        qt.QObject.connect(self.__refreshTimer,qt.SIGNAL('timeout()'),self.__refresh_recurs)
        qt.QObject.connect(self,qt.SIGNAL('doubleClicked (QListViewItem *,const QPoint &,int )'),
                           self.__dbclickedCBK)
        self.addColumn('Source Name')
        self.setRootIsDecorated(True)
        self.setSelectionMode(self.Extended)
        self.__key2Items = weakref.WeakValueDictionary()
        #PopUp Menu
        self.__popUpMenu = qt.QPopupMenu(self)
        self.__popUpMenu.insertItem('display',self.__displaySourceRecurse)
        self.__popUpMenu.insertItem('remove',self.__removeSource)
        qt.QObject.connect(self,qt.SIGNAL('rightButtonPressed(QListViewItem*,const QPoint &,int)'),
                           self.__popUpDisplay)
        self.__mdi = mdi
        self.__dataActionClass = []
        
    def insertDataSourceInTree(self,dico,parent = None) :
        if parent is None :
            parent = self
        for dicParent,childdico in dico.iteritems() :
            dataSource = self.__key2Items.get(dicParent.key(),None)
            if dataSource is None :
                dataSource = QubDataSourceTreeItem(parent,key = dicParent.key(),dataSource = dicParent)
                dataSource.setText(0,dicParent.name())
                self.__key2Items[dataSource.getKey()] = dataSource
            self.insertDataSourceInTree(childdico,dataSource)

            if isinstance(dicParent,QubDataGroup) and hasattr(dataSource,'sliderAction') : # refresh slider action
                sliderAction = dataSource.sliderAction()
                if sliderAction:
                    sliderAction.setMaxVal(dataSource.childCount())

    def display(self,data) :
        if isinstance(data,QubDataContainerClass) :
            item = self.__key2Items[data.key()]
            item.setSelected(True)
            self.__displaySource(item)
    ##@brief set actions data plugins
    #
    #Those action will be add to the data display
    def setDataActions(self,actions) :
        self.__dataActionClass = actions
        
    def __popUpDisplay(self,item,point,columnid) :
        self.__popUpMenu.exec_loop(point)

    def __displaySourceRecurse(self,i,parent = None) :
        for item in self.__getIterator(parent) :
            if item.isSelected() :
                self.__displaySource(item)
            else:
                self.__displaySourceRecurse(i,item)

    def __displaySource(self,item) :
        try:
            item.dataDisplay().setFocus()
        except (TypeError,AttributeError):
            dataClass = item.getDataClass()
            try:
                actionsNcallback = []
                if isinstance(dataClass,QubDataGroup) :
                    try:
                        child = self.__getIterator(item).next()
                        dataClass = child.getDataClass()
                        sliderAction = QubSliderNSpinAction(name = 'slider',group='image_chose',
                                                            place='statusbar')
                        item.sliderAction = weakref.ref(sliderAction)
                        
                        class _sliderCallback:
                            def __init__(self,item,getIteratorMethode) :
                                self.__item = weakref.ref(item)
                                self.__getMethode = getIteratorMethode
                                self.__idle = qt.QTimer(None)
                                self.__currentID = 0
                                qt.QObject.connect(self.__idle,qt.SIGNAL('timeout()'),self.__refresh)
                                
                            def valueChanged(self,val) :
                                self.__currentID = val
                                if not self.__idle.isActive():
                                    self.__idle.start(0)
                            def setDataDisplay(self,dataDisplay) :
                                self.__dataDisplay = weakref.ref(dataDisplay)
                                
                            def __refresh(self) :
                                self.__idle.stop()
                                parentItem = self.__item()
                                for i,item in enumerate(self.__getMethode(parentItem)) :
                                    if i == self.__currentID:
                                        dataClass = item.getDataClass()
                                        try:
                                            dataArray,info = dataClass.data()
                                            dataDisplay = self.__dataDisplay()
                                            dataDisplay.setData(dataArray)
                                            dataDisplay.setCaption(dataClass.name())
                                        except: break
                        cbk = _sliderCallback(item,self.__getIterator)
                        actionsNcallback.append((sliderAction,cbk))
                        sliderAction.setCallBack(cbk.valueChanged)
                        sliderAction.setMaxVal(item.childCount() - 1)
                    except:
                        import traceback
                        traceback.print_exc()
                        return
                dataArray,info = dataClass.data()
                dataDisplay = QubDataDisplay(self.__mdi)
                if self.__mdi is not None:
                    self.__mdi.addNewChildOfMainWindow(dataDisplay,None)
                    dataDisplay.resize(0.5*self.__mdi.width(),0.5 * self.__mdi.height())
                    dataDisplay.move(self.__mdi.width() * .25,self.__mdi.height() * 0.25)

                dataDisplay.setData(dataArray)
                item.dataDisplay = weakref.ref(dataDisplay)
                dataDisplay.setCaption(dataClass.name())

                for pluginsClass in self.__dataActionClass :
                    c = pluginsClass()
                    try:
                        c.initPlugin(dataDisplay)
                    except NotImplementedError:
                        import traceback
                        traceback.print_exc()
                actions = []
                for action,cbk in actionsNcallback:
                    actions.append(action)
                    cbk.setDataDisplay(dataDisplay)
                    
                if actions:
                    dataDisplay.addAction(actions)
                dataDisplay.show()
            except:
                import traceback
                traceback.print_exc()
       
    def __removeSource(self,i,parent = None) :
        for item in self.__getIterator(parent) :
            if item.isSelected() :
                if parent is None :
                    self.takeItem(item)
                else:
                    parent.takeItem(item)
            else:
                self.__removeSource(i,item)
                        
    def __dbclickedCBK(self,item,point,column) :
        if item :
            try:
                item.dbClickedCBK()
            except:
                import traceback
                traceback.print_exc()
                
    def __refresh_recurs(self,parentItem = None) :
        for item in self.__getIterator(parentItem) :
            self.__refresh_recurs(item)
            try:
                item.refresh()
            except:
                import traceback
                traceback.print_exc()
            
    def __getIterator(self,parentItem = None) :
        if parentItem is not None :
            Item = parentItem.firstChild()
        else :
            Item = self.firstChild()
        while Item :
            NextItem = Item.nextSibling()
            yield Item
            Item = NextItem

class QubDataSourceTreeItem(qt.QListViewItem):
    def __init__(self,parent,key = None,dataSource = None,**keys) :
        qt.QListViewItem.__init__(self,parent)
        self.__dataSource = dataSource
        self.__key = key or id(self)
        self.dataDisplay = None

    def __del__(self) :
        if self.dataDisplay :
            dataDisplay = self.dataDisplay()
            if dataDisplay:
                dataDisplay.close()

    ##@brief get a key for this item
    #
    #this methode should be redefine in subclass
    def getKey(self) :
        return self.__key
    ##@brief get the handler data of this item
    #
    #@return a QubDataClass
    def getDataClass(self) :
        return self.__dataSource
    ##@brief a refresh function if needed
    #
    #this methode will be called by a timer to refresh this item
    #you can refresh text column and or icon pixmap
    def refresh(self) :
        pass
    ##@brief this methode will be called on double click
    def dbClickedCBK(self) :
        pass
