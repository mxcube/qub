import sps

from Qub.Data.Source.QubSource import QubSpecMotherSource
        

################################################################################
###########                  QubSpecShm                              ###########
################################################################################

class QubSpecShm(QubSpecMotherSource) :
    def __init__(self,specVersion,name,aPollPlug) :
        QubSpecMotherSource.__init__(self,specVersion,name,aPollPlug,True)

                
    def __del__(self):
        self._plugmgr.destroy(self)
        self._pollplug.setEnd()

        
    def hasChange(self) :
        cnt = self._cnt()
        return cnt and sps.isupdated(cnt.name(),self._name)

    def getSpecArray(self,forceupdate = False) :
        if not self._isDead :
            cnt = self.container()
            if cnt:
                try:
                    return sps.getdata(cnt.name(),self._name)
                except sps.error: pass
        else :
            raise StandardError("Array is been deleted")

    def checkUpdate(self) :
        if(self.hasChange()) :
            cnt = self._cnt()
            try:
                data = self.getSpecArray(True)
                if cnt:
                    self._plugmgr.update(cnt,self,data)
            except sps.error:
                if cnt:
                    self._plugmgr.destroy(cnt,[self])
