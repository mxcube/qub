import sps

from Qub.Data.Source.QubSource import QubSpecMotherSource
        

################################################################################
###########                  QubSpecShm                              ###########
################################################################################

class QubSpecShm(QubSpecMotherSource) :
    def __init__(self,specVersion,name,aPollPlug) :
        QubSpecMotherSource.__init__(self,specVersion,name,aPollPlug,True)
        self.__data = None
                
    def __del__(self):
        self._plugmgr.destroy(self)
        self._pollplug.setEnd()
        
    def hasChange(self) :
        return sps.isupdated(self._cnt.name(),self._name)

    def getSpecArray(self,forceupdate = False) :
        if not self._isDead :
            if not forceupdate :
                forceupdate = sps.isupdated(self._cnt.name(),self._name)
            if(forceupdate) :    
                self.__data = sps.getdata(self._cnt.name(),self._name)
            return self.__data
        else :
            raise StandardError("Array is been deleted")

    def checkUpdate(self) :
        if(self.hasChange()) :
            data = self.getSpecArray(True)
            self._plugmgr.update(self._cnt,self,data)
