from Qub.Data.Plug.QubPlugManager import QubPlugManager

class QubSource :
    def __init__(self) :
        self._dataObjects = {}

    def getObjects(self, key, *args) :
        if not self._dataObjects.has_key(key) :
            newObject = self.createObject(key,*args)

            if newObject is not None:
                self._dataObjects[key] = newObject

            return newObject

        return self._dataObjects[key]
    
    def objects(self) :
        return self._dataObjects.values()
    
    def createObject(self, key, *args):
        return None

    def removeObject(self,key) :
        self._dataObjects.pop(key)

class QubSpecMotherSource(QubSource) :
    def __init__(self,container,name,aPollplug,aCallEachTimeFlag = False) :
        QubSource.__init__(self)
        self._cnt = container
        self._name = name
        self._pollplug = aPollplug
        self._plugmgr = QubPlugManager(self,aPollplug,aCallEachTimeFlag)
        self._isDead = False
        if(container) :
            container.plug(aPollplug)
            
    def __del__(self) :
        self.__cnt.removeObject(self._name)

    def name(self) :
        return self._name
            
    def plug(self,aQubPlug) :
        self._plugmgr.plug(aQubPlug)

    def unplug(self,aQubPlug) :
        self._plugmgr.unplug(aQubPlug)
 
    def removeObjectInContainer(self) :
        self.__cnt.removeObject(self._name)
 
    def setDestroy(self) :
        self._isDead = True
        self._pollplug.setEnd()
        self.removeObjectInContainer()

    def getDeletednNewFromDataName(self,dataNameArray) :
        arrayNameSet = set(dataNameArray)
        createdName = set([x.name() for x in self._dataObjects.values()])
        return (createdName - arrayNameSet,arrayNameSet - createdName)
