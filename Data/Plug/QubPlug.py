#from Qub.Data.Plug.QubPlugManager import QubPlugManager

class QubPlug :
    """
    QubPlug is a base class to plug data source to every think.
    You have to derivate update and destroy methode for your use.
    """
    def __init__(self,timeout = 1000,anActiveFlag = True) :
        """
        each timeout the update methode will be called
        anActiveFlag if True : activate the polling as soon as it's pluged somewhere
        if not you have to call startPolling when you want
        """
        self.timeLeft = timeout
        self.__timeout = timeout
        self.__endFlag = False
        self.__isActive = anActiveFlag
        self._plugmgrs = []
        self._sources = []
        
    def changeInterval(self,time) :
        self.__timeout = time
        if(self.timeLeft > self.__timeout) :
            self.timeLeft = self.__timeout
        
    def timeout(self) :
        return self.__timeout

    def startPolling(self) :
        if not self.__isActive :
            if len(self._plugmgrs) :
                self.__isActive = True
                for plug_mgr in self._plugmgrs :
                    plug_mgr.startPolling(self.__timeout)
            else :
                raise StandardError('This Plug is not connect')

    def stopPolling(self) :
        self.__isActive = False
        
    def setEnd(self) :
        """
        This is the end... of the plug.
        Call this methode for a clean remove.
        This methode must be call instead of del
        """
        self.__endFlag = True

    def newobject(self,*args) :
        """
        This methode is call when the container detect a new source
        """
    def update(self,*args) :
        """
        This methode is call on timer be the polling until it
        return True (End) or the stopPolling methode
        if it return True, the plug will be set unActive
        """
        return True

    def destroy(self,*args) :
        """
        This methode is call when the container is destroy
        sould return True if the plug manage that event
        if it return True, the plug will be remove from the poll
        """
        return False

    def setPlugMgr(self,aPlugMgr) :
        """
        Methode call be the Plug Manager (user shoul'd use)
        """
##        if isinstance(QubPlugManager,aPlugMgr) :
        self._plugmgrs.append(aPlugMgr)
##        else :
##            raise StandardError('Must be a QubPlugManager')

    def rmPlugMgr(self,aPlugMgr) :
        """
        Methode call be the Plug Manager (user shoul'd use)
        """
        self._plugmgrs.remove(aPlugMgr)
      
    def isActive(self) :
        return self.__isActive

    def isEnd(self) :
        return self.__endFlag
            
class QubPollingPlug(QubPlug) :
    def __init__(self,timeout = 1000,anActiveFlag = False) :
        QubPlug.__init__(self,timeout,anActiveFlag)
        self._nextplugmgr = None

    def setNextPlugMgr(self,nextplugmgr) :
        self._nextplugmgr = nextplugmgr
        
    def start(self,timeout) :
        self.changeInterval(timeout)
        self.startPolling()

    def stop(self) :
        self.stopPolling()
    
