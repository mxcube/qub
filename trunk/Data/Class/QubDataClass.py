import weakref

from Qub.Tools.QubWeakref import createWeakrefMethod

class QubDataContainerClass:
    ##@brief constructor
    #
    #@param name the object's name
    #@param key the id of the object, it's should be unique
    #
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
    ##@brief constructor
    #
    #@param data object's data (usualy a numpy array)
    #@param info object's information (usualy a dictionnary)
    #@param caching if True keep data in cache
    #
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
    ##@brief get data and info
    #
    #usualy a numpy array and dictionnary as info
    #
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
    ##@see scaleClass
    def setScaleClass(self,scaleClass) :
        self._scaleClass = scaleClass
    ##@brief set an update callback
    #
    #the callback methode will be called each time the data changed.
    #Callback signature is <b>cbk(self,Qub::Data::Class::QubDataClass::QubDataClass)</b>
    #
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
            
##@brief image class
#
#This class is a image source description. It's link with a plugin
#
class QubDataImage(QubDataClass) :
    ##@brief constructor
    #
    #@param read_plugin a class which retrived the info and data by <b>get</b> function
    #
    def __init__(self,read_plugin = None,**keys) :
        QubDataClass.__init__(self,**keys)
        self.__read_plugin = read_plugin
        try:
            read_plugin.plug(QubDataClass.Plug(self))
        except AttributeError:
            pass

    def _data(self,**keys):
        return self.__read_plugin.get(**keys)
