import weakref
from Qub.Data.Plug.QubPlug import QubPlug

class QubPlugManager :
    """
    The Object manage each plug connected to it, it call plug callback (update & destroy).
    the pollplug can be a QTimer or a QubPollPlug
    """
    def __init__(self,source,pollplug,calleachtimeflag = False,timeout = 1000) :
        self.__plugs = []
        self.__pollplug = pollplug
        self.__sourceRef = weakref.ref(source)
        pollplug.setNextPlugMgr(self)
        self.__timeout = timeout
        self.__calleachtime = calleachtimeflag

    def timeout(self) :
        return self.__timeout
    
    def nbPlug(self) :
        return len(self.__plugs)
    
    def source(self) :
        return self.__sourceRef
    
    def plug(self,aQubPlug) :
        """
        Plug object connection
        """
        if(isinstance(aQubPlug,QubPlug)) :
            self.__plugs.append(weakref.ref(aQubPlug))
            aQubPlug.setPlugMgr(self)
            if(aQubPlug.isActive()) :
                self.__pollplug.start(aQubPlug.timeout())
        else :
            raise StandardError('Must be a QubPlug')

    def unplug(self,aQubPlug) :
        """
        Unplug object
        """
        if(isinstance(aQubPlug,QubPlug)) :
            try:
                self.__plugs.remove(weakref.ref(aQubPlug))
            except ValueError:
                return
            aQubPlug.rmPlugMgr(self)
            if not len(self.__plugs) :
                self.__pollplug.stop()
            else:
                timerInterval = 1000000
                for plug in self.__plugs:
                    if(timerInterval > plug.timeout()) :
                        timerInterval = plug.timeout()
                self.__timeout = timerInterval
                self.__pollplug.changeInterval(self.__timeout)
                
    def startPolling(self,timeout) :
        if(self.__pollplug.isActive()) :
            if(self.__timeout > timeout) :
                self.__timeout = timeout
                self.__pollplug.changeInterval(timeout)
        else :
            self.__pollplug.start(timeout)

    def update(self,*args) :
        """
        Called when you may need update
        """
        timerInterval = 1000000
        nbActivePlug = 0
        timeout = self.__timeout
        if not timeout :
            timeout = 1
        for plugRef in self.__plugs :
            plug = plugRef()
            if plug and not plug.isEnd() :
                if plug.isActive() :
                    nbActivePlug += 1
                    plug.timeLeft -= timeout
                    if(self.__calleachtime or plug.timeLeft <= 0) :
                        if plug.update(*args) :
                            plug.stopPolling()
                            continue
                    
                        plug.timeLeft = plug.timeout()

                    if(timerInterval > plug.timeLeft) :
                        timerInterval = plug.timeLeft
        self.__plugs = [plug for plug in self.__plugs if (plug and plug()) and not plug().isEnd()]
        
        nbPlug = len(self.__plugs)
        if not nbPlug or not nbActivePlug:
            self.__pollplug.stop()
        elif(timerInterval != self.__timeout) :
            self.__timeout = timerInterval
            self.__pollplug.changeInterval(self.__timeout)
        return not nbPlug or not nbActivePlug
  
    def containerDestroy(self,*args) :
        """
        Methode called when container is destroy
        """
        for plugRef in self.__plugs :
            plug = plugRef()
            if plug and not plug.isEnd() :
                if plug.containerDestroy(*args) :
                    plug.rmPlugMgr(self)
                    self.__plugs.remove(plugRef)
        aEndFlag = not len(self.__plugs)
        if aEndFlag :
            self.__pollplug.stop()
        return aEndFlag
    
    def destroy(self,*args) :
        """
        Methode called when container is object of a container is destroy
        """
        for plugRef in self.__plugs :
            plug = plugRef()
            if plug and not plug.isEnd() :
                if plug.destroy(*args) :
                    plug.rmPlugMgr(self)
                    self.__plugs.remove(plugRef)
        aEndFlag = not len(self.__plugs)
        if(aEndFlag) :
            self.__pollplug.stop()
        return aEndFlag

    def newContainerObject(self,*args) :
        """
        Methode called when new container object may be available
        """
        nbActivePlug = 0
        for plugRef in self.__plugs :
            plug = plugRef()
            if plug and not plug.isEnd() :
                if plug.isActive() :
                    nbActivePlug += 1
                    plug.newContainerObject(*args)
            else :
                self.__plugs.remove(plugRef)

        nbPlug = len(self.__plugs)
        if not nbPlug or not nbActivePlug:
            self.__pollplug.stop()
        return not nbPlug or not nbActivePlug
             
