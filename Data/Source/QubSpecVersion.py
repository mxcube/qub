import sps
from Qub.Data.Source.QubSpecShm import QubSpecShm
from Qub.Data.Source.QubSource import QubSpecMotherSource
from Qub.Data.Plug.QubPlug import QubPollingPlug


                    ####### QubSpecVersion #######

class QubSpecVersion(QubSpecMotherSource) :
    def __init__(self,cnt,name,pollplug) :
        QubSpecMotherSource.__init__(self,cnt,name,pollplug)
         
    def createObject(self,key,*args):
        if key in sps.getarraylist(self._name) :
            pollplug = QubSpecVersion2Shm(self)
            return QubSpecShm(self,key,pollplug)
        return None  
           ####### QubSpecVersionQubSpecVersion2Shm #######

class QubSpecVersion2Shm(QubPollingPlug) :
    def __init__(self,aQubSpecVersion) :
        QubPollingPlug.__init__(self)
        self.__specversion = aQubSpecVersion
        
    def update(self,specsource) :
        available_arrays = sps.getarraylist(self.__specversion.name())
        (darrays,narray) = self.__specversion.getDeletednNewFromDataName(available_arrays)

        if(len(darrays)) :
            self._nextplugmgr.destroy(self.__specversion,darrays)

        for shm in self.__specversion.objects() :
            shm.checkUpdate()

        if(len(narray)) :
            self._nextplugmgr.newObject(self.__specversion,narray)
        return not self._nextplugmgr.nbPlug()
    
    def destroy(self,specsource,specversions) :
        aEndFlag = False
        if self.__specversion in specversions :
            self._nextplugmgr.destroy(self.__specversion)
            self.__specversion.setDestroy()
            aEndFlag = True
        return aEndFlag
