from Qub.Data.Plug.QubPlug import QubPlug

class QubPlugManager :
    """
    The Object manage each plug connected to it, it call plug callback (update & destroy).
    the pollplug can be a QTimer or a QubPollPlug
    """
    def __init__(self,source,pollplug,calleachtimeflag = False,timeout = 1000) :
        self.__plugs = []
        self.__pollplug = pollplug
        self.__source = source
        pollplug.setNextPlugMgr(self)
        self.__timeout = timeout
        self.__calleachtime = calleachtimeflag
        
    def nbPlug(self) :
        return len(self.__plugs)
    
    def source(self) :
        return self.__source
    
    def plug(self,aQubPlug) :
        """
        Plug object connection
        """
        if(isinstance(aQubPlug,QubPlug)) :
            self.__plugs.append(aQubPlug)
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
            self.__plugs.remove(aQubPlug)
            aQubPlug.rmPlugMgr(self)
            if not len(self.__plugs) :
                self.__pollplug.stop()
                
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
        for i,plug in enumerate(self.__plugs) :
            if not plug.isEnd() :
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
            else:
                self.__plugs[i:i] = []

        nbPlug = len(self.__plugs)
        if not nbPlug or not nbActivePlug:
            self.__pollplug.stop()
        elif(timerInterval != self.__timeout) :
            self.__timeout = timerInterval
            self.__pollplug.changeInterval(self.__timeout)
        return not nbPlug or not nbActivePlug
  
    def destroy(self,*args) :
        """
        Methode called when container is destroy
        """
        for i,plug in enumerate(self.__plugs) :
            if not plug.isEnd() :
                if plug.destroy(*args) :
                    plug.rmPlugMgr(self)
                    self.__plugs[i:i] = []
        aEndFlag = not len(self.__plugs)
        if(aEndFlag) :
            self.__pollplug.stop()
        return aEndFlag

    def newObject(self,*args) :
        """
        Methode called when new container object may be available
        """
        nbActivePlug = 0
        for i,plug in enumerate(self.__plugs) :
            if not plug.isEnd() :
                if plug.isActive() :
                    nbActivePlug += 1
                    plug.newObject(*args)
            else :
                self.__plugs[i:i] = []

        nbPlug = len(self.__plugs)
        if not nbPlug or not nbActivePlug:
            self.__pollplug.stop()
        elif(timerInterval != self.__timeout) :
            self.__timeout = timerInterval
            self.__pollplug.changeInterval(self.__timeout)
        return not nbPlug or not nbActivePlug
             
