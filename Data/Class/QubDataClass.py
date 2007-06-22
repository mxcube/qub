import weakref

from Qub.Tools.QubWeakref import createWeakrefMethod

class QubDataContainerClass:
    def __init__(self,name = '',key = None,**keys) :
        self._name = name
        self._key = key or id(self)
        
    def name(self) :
        return self._name

    def key(self) :
        return self._key

class QubDataGroup(QubDataContainerClass) :
    def __init__(self,**keys) :
        QubDataContainerClass.__init__(self,**keys)
    def key(self) :
        return self._name
    
class QubDataFileContainerClass(QubDataContainerClass) :
    def __init__(self,filename = '',**keys) :
        QubDataContainerClass.__init__(self,**keys)
        self._fileName = filename

    def filename(self) :
        return self._fileName
    
##@brief mother class of data class Object
#
class QubDataClass(QubDataContainerClass):
    class Plug:
        def __init__(self,source,caching = False) :
            self.__source = source and weakref.ref(source,self.__end) or None
            self.__cnt = None
            self.__cache = caching
            
        def update(self) :
            source = self.__source()
            if source: source.setDirty()

        def setContainer(self,cnt) :
            self.__cnt = cnt

        def isCaching(self) :
            return self.__cache
        
        def __end(self,ref) :
            if self.__cnt:
                self.__cnt.removePlug(self)
            
    def __init__(self,data = None,info = None,caching = False,**keys) :
        QubDataContainerClass.__init__(self,**keys)
        self._isDirty = True            # Need a refresh
        self._dataCache = data
        self._info = info
        self.__childrenDataClass = []
        self.__cachingCounter = 0
        self.__forceCaching = caching
        self._updateCallback = None
    ##@brief get data
    #
    #usualy a numpy array and dictionnary as info
    def data(self) :
        if self._isDirty or self._dataCache is None :
            data,info = self._data()
            self._isDirty = False
        else:
            data = self._dataCache
            info = self._info

        if self.__childrenDataClass:
            self._dataCache = data
            self._info = info
        return (data,info)      

    def setUpdateCallback(self,cbk) :
        self._updateCallback = createWeakrefMethod(cbk)
        
    def setDirty(self) :
        if not self._isDirty :
            self._isDirty = True
            if self._updateCallback : self._updateCallback(self)
            for children in self.__childrenDataClass:
                children.update()
            
    def plug(self,aPlug) :
        self.__childrenDataClass.append(aPlug)
        if aPlug.isCaching() : self.__cachingCounter += 1
        aPlug.setContainer(self)

    def removePlug(self,aPlug) :
        try:
            self.__childrenDataClass.remove(aPlug)
            if aPlug.isCaching() : self.__cachingCounter -= 1
        except ValueError:
            pass
        if not self.__forceCaching and not self.__cachingCounter :
            self._data = None           # No source are interest of this data
            
class QubDataImage(QubDataClass) :
    def __init__(self,stream_io = None,**keys) :
        QubDataClass.__init__(self,**keys)
        self.__stream_io = stream_io
        stream_io.plug(QubDataClass.Plug(self))

    def _data(self):
        return self.__stream_io.get()
            

class QubDataFiltered(QubDataClass):
    def __init__(self,data_source_key = {},filter_class = None,**keys) :
        QubDataClass.__init__(self,**keys)
        self._data_source_key = data_source_key
        self._filter_class = filter_class
        for source in data_source_key.values():
            source.plug(QubDataClass.Plug(self))
            
    def _data(self) :
        return self._filter_class.doFilter(self._data_source_key)    

class QubDataOperation(QubDataClass):
    def __init__(self,data_source_list = [],operation_class = None,caching = True,**keys) :
        QubDataClass.__init__(self,**keys)
        self._data_source_list = data_source_list
        self._operation_class = operation_class
        for source in data_source_list:
            source.plug(QubDataClass.Plug(self))

    def _data(self) :
        return self._operation_class.doOperation(self._data_source_list)
