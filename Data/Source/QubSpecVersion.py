import weakref
from Qub.CTools import sps
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
    def __init__(self,aQubSpecVersion,timeout = 1000,anActiveFlag = False) :
        QubPollingPlug.__init__(self,timeout = timeout,anActiveFlag = anActiveFlag)
        self.__specversion = weakref.ref(aQubSpecVersion)

    def update(self,specsource) :
        cnt = self.__specversion()
        if cnt :
            available_arrays = sps.getarraylist(cnt.name())
            (darrays,narray) = cnt.getDeletednNewFromDataName(available_arrays)

            if(len(darrays)) :
                self.__destroy(darrays)
                
            for shm in cnt.objects() :
                shm.checkUpdate()
                
            if(len(narray)) :
                if self._nextplugmgr:
                    self._nextplugmgr.newContainerObject(cnt,narray)
                self.newObject(cnt,narray)
            if self._nextplugmgr:
                return not self._nextplugmgr.nbPlug()
            else:
                return False
        else:
            return True

    def containerDestroy(self,specsource,specversions) :
        cnt = self.__specversion()
        aEndFlag = not cnt
        if cnt and cnt in specversions :
            self.__destroy(cnt.objects())
            cnt.setDestroy()
            aEndFlag = True
        return aEndFlag

    def __destroy(self,darrays) :
        cnt = self.__specversion()
        if cnt:
            self.destroy(cnt,darrays)
            if self._nextplugmgr:
                self._nextplugmgr.destroy(cnt,darrays)
