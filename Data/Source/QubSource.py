import weakref
from Qub.Data.Plug.QubPlugManager import QubPlugManager

class QubSource :
    def __init__(self) :
        self._dataObjects = {}

    def getObjects(self, key, *args) :
        if not self._dataObjects.has_key(key) :
            newObject = self.createObject(key,*args)

            if newObject is not None:
                self._dataObjects[key] = weakref.ref(newObject,self._objectDeleteCBK)

            return newObject

        return self._dataObjects[key]()
    
    def objects(self) :
        values = []
        for value in self._dataObjects.values() :
            values.append(value())
        return values
    
    def createObject(self, key, *args):
        return None

    def _objectDeleteCBK(self,objectref) :
        for key,obj in self._dataObjects.iteritems():
            if obj == objectref:
                self._dataObjects.pop(key)
                break
        
class QubSpecMotherSource(QubSource) :
    def __init__(self,container,name,aPollplug,aCallEachTimeFlag = False) :
        QubSource.__init__(self)
        self._cnt = container and weakref.ref(container)
        self._name = name
        self._pollplug = aPollplug
        self._plugmgr = QubPlugManager(self,aPollplug,aCallEachTimeFlag)
        self._isDead = False
        if(container) :
            container.plug(aPollplug)
            
    def __del__(self) :
        self.setDestroy()
        
    def container(self) :
        return self._cnt()
    
    def name(self) :
        return self._name
            
    def plug(self,aQubPlug) :
        self._plugmgr.plug(aQubPlug)

    def unplug(self,aQubPlug) :
        self._plugmgr.unplug(aQubPlug)
 
    def setDestroy(self) :
        self._isDead = True
        self._pollplug.setEnd()

    def getDeletednNewFromDataName(self,dataNameArray) :
        arrayNameSet = set(dataNameArray)
        createdName = set([x().name() for x in self._dataObjects.values()])
        return (createdName - arrayNameSet,arrayNameSet - createdName)
