################################################################################
###########                  QubSpecVersionPolling                    ###########
################################################################################

import sps
from Qub.Data.Source.QubSource import QubSpecMotherSource
from Qub.Data.Source.QubSpecVersion import QubSpecVersion
from Qub.Data.Plug.QubPlug import QubPollingPlug

__theSpecVersions = None

def init() :
    global __theSpecVersions
    __theSpecVersions = QubSpecSource(QubSpecTimer())
        
def getSpecVersions() :
    if __theSpecVersions is None :
        init()
    
    return __theSpecVersions
    

try :
    import qt
    
    class QubSpecTimer(qt.QTimer) :
        def __init__(self) :
            qt.QTimer.__init__(self)
            self.connect(self,qt.SIGNAL('timeout()'),self.update);
        
        def update(self) :
            self.__plugmgr.update()

        def setNextPlugMgr(self,aPlugMgr) :
            self.__plugmgr = aPlugMgr

        def setEnd(self) :
            self.stop()
        
    class QubSpecSource(QubSpecMotherSource) :
        def __init__(self,pollplug) :
            QubSpecMotherSource.__init__(self,None,"MainContainer",pollplug)
                        
        def createObject(self, key,*args):
            if key in sps.getspeclist() :
                pollplug = QubSpecSource2Version(self)
                return QubSpecVersion(self,key,pollplug)
            return None
    
except :
            print "No polling possible"


class QubSpecSource2Version(QubPollingPlug) :
    def __init__(self,aQubSpecSource)  :
        QubPollingPlug.__init__(self)
        self.__specsource = aQubSpecSource

    def update(self) :
        specversions = sps.getspeclist()
        (dversions,nversions) = self.__specsource.getDeletednNewFromDataName(specversions)
        if(len(dversions)) :
            self._nextplugmgr.destroy(self.__specsource,dversions)
            
        self._nextplugmgr.update(self.__specsource)

        if(len(nversions)) :
            self._nextplugmgr.newObject(self.__specsource,nversions)
        return not self._nextplugmgr.nbPlug()
            
