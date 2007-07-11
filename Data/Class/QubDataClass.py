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
    
##@brief mother class of data class Object
#
class QubDataClass(QubDataContainerClass):
    class Plug:
        def __init__(self,source,caching = False) :
            self.__source = source and weakref.ref(source,self.__end) or None
            self.__cnt = None
            self.__cache = caching

        ##@brief update sources
        #
        #@return True if update OK
        def update(self) :
            source = self.__source()
            if source: source.setDirty()
            return source and True or False
        
        def setContainer(self,cnt) :
            self.__cnt = cnt

        def isCaching(self) :
            return self.__cache
        
        def __end(self,ref) :
            if self.__cnt:
                self.__cnt.removePlug(self)
            
    def __init__(self,data = None,info = None,scaleClass = None,caching = False,**keys) :
        QubDataContainerClass.__init__(self,**keys)
        self._isDirty = True            # Need a refresh
        self._dataCache = data
        self._info = info
        self._scaleClass = scaleClass
        self.__childrenDataClass = []
        self.__cachingCounter = 0
        self.__forceCaching = caching
        self._updateCallback = None
    ##@brief get data
    #
    #usualy a numpy array and dictionnary as info
    def data(self,**keys) :
        if self._isDirty or self._dataCache is None :
            data,info = self._data(**keys)
            self._isDirty = False
        else:
            data = self._dataCache
            info = self._info

        if self.__childrenDataClass:
            self._dataCache = data
            self._info = info
        return (data,info)      
    ##@brief get scale data class
    #
    #usualy return a Qub::Data::Scale::QubDataScale::QubDataScale
    def scaleClass(self):
        return self._scaleClass

    def setScaleClass(self,scaleClass) :
        self._scaleClass = scaleClass
        
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
    def __init__(self,read_plugin = None,**keys) :
        QubDataClass.__init__(self,**keys)
        self.__read_plugin = read_plugin
        try:
            read_plugin.plug(QubDataClass.Plug(self))
        except AttributeError:
            pass

    def _data(self,**keys):
        return self.__read_plugin.get(**keys)
