import qt

class QubLock :
    """ Simple way to lock a API """
    def __init__(self,mutex,lockFlag = True) :
        self.__mutex = mutex
        self.__lockFlag = False
        if lockFlag :
            self.lock()
            
    def __del__(self) :
        self.unLock()
            
    def lock(self) :
        if not self.__lockFlag :
            self.__mutex.lock()
            self.__lockFlag = True
                
    def unLock(self) :
        if self.__lockFlag :
            self.__lockFlag = False
            self.__mutex.unlock()

class QubThreadProcess :
    """
    Your process have to inherits of this class.
    This class drive the process steps by calling QubThreadProcess.push and QubThreadProcess.pop
    """
    def __init__(self) :
        self._threadMgr = _theThreadPoll
        
    def getFunc2Process(self) :
        """
        This methode is call under a mutex lock; it should give a quike return of the next methode to process
        After calling this methode, the process class is still in the queue in order to multi-thread
        the same step of the process, YOU HAVE TO POP IT YOURSELF FROM THE QUEUE!!! 
        """
        raise StandardError('getFunc2Process must be redefine')

class _ThreadMgr :
    class _thread(qt.QThread) :
        def __init__(self,queues,mutex,cond) :
            qt.QThread.__init__(self)
            self.__cond = cond
            self.__mutex = mutex
            self.__queues = queues
            self.__stop = False

        def __del__(self) :
            self.stop()
            self.wait()
            
        def stop(self) :
            aLock = QubLock(self.__mutex)
            self.__stop = True
            self.__cond.wakeOne()

        def run(self) :
            aLock = QubLock(self.__mutex)
            while not self.__stop :
                while not self.__stop and self.__waitCondTest() :
                    self.__cond.wait(self.__mutex)
                if not self.__stop :
                    queue = self.__getMaxLengthQueue()
                    process = queue[0]
                    try :
                        func = process.getFunc2Process()
                        aLock.unLock()
                        func()
                        aLock.lock()
                    except :
                        aLock.lock()
                        if len(queue) and process == queue[0] :
                            queue.pop(0)

        def __waitCondTest(self) :
            aFlag = True
            for l in self.__queues :
                if len(l) :
                    aFlag = False
                    break
            return aFlag
        
        def __getMaxLengthQueue(self) :
            maxLenght = 0
            returnQueue = None
            for l in self.__queues :
                lenght = len(l)
                if lenght > maxLenght :
                    maxLenght = lenght
                    returnQueue = l
            return returnQueue
        
    def __init__(self) :
        self.__mutex = qt.QMutex()
        self.__cond = qt.QWaitCondition()
        self.__queues = []
        self.__threads = []
        for x in xrange(2) :
            threadProcess = _ThreadMgr._thread(self.__queues,self.__mutex,self.__cond)
            self.__threads.append(threadProcess)
            threadProcess.start()
            


    def push(self,process,lockFlag = True,queueId = 0) :
        aLock = QubLock(self.__mutex,lockFlag)
        nbQueue = len(self.__queues)
        if nbQueue > queueId :
            queue = self.__queues[queueId]
            while len(queue) > 127 :    # QUEUE LIMIT
                self.__cond.wait()
            queue.append(process)
        else :
            for i in xrange(nbQueue,queueId) :
                self.__queues.append([])
            self.__queues.append([process])
        self.__cond.wakeAll()

    def pop(self,process,lockFlag = True,queueId = 0) :
        aLock = QubLock(self.__mutex,lockFlag)
        nbQueue = len(self.__queues)
        if nbQueue < queueId :
            raise StandardError('nb Queue == %d, try pop on %d' %
                                (nbQueue,queueId))
        elif self.__queues[queueId][0] != process :
            raise StandardError('try to pop an other process than your')
        else :
            self.__queues[queueId].pop(0)
            self.__cond.wakeAll()

#INIT
_theThreadPoll = _ThreadMgr()

