import qt
import traceback
from Qub.Tools.QubThread import QubLock
from Qub.Tools.QubThread import QubThreadProcess

class QubStdData2Image(QubThreadProcess,qt.QObject) :
    class _data_struct :
        PATH_TYPE,DATA_TYPE = range(2)
        def __init__(self) :
            self.type = QubStdData2Image._data_struct.DATA_TYPE
            self.path = None
            self.data = None
            self.inProcess = False
            self.end = False
            self.image = qt.QImage()
            
        def setPath(self,path) :
            self.type = QubStdData2Image._data_struct.PATH_TYPE
            self.path = path
            return self
        def setData(self,data) :
            self.type = QubStdData2Image._data_struct.DATA_TYPE
            self.data = data
            return self
    """
    This class is use to decompress standard data -> image.
    data cant be (jpeg,tiff 8 bits...)
    WARNING the setImage plug methode will be called in an other thread than the main
    """
    def __init__(self) :
        QubThreadProcess.__init__(self)
        qt.QObject.__init__(self)
        self.__plug = None
        self.__mutex = qt.QMutex()
        self.__cond = qt.QWaitCondition()
        self.__dataPending = []
        self.__actif = False
        self.__postSetImage = []
        
    def plug(self,plug):
        if isinstance(plug,QubStdData2ImagePlug) :
            aLock = QubLock(self.__mutex)
            self.__plug = plug
        else :
            raise StandardError('Must be a QubStdData2ImagePlug')

    def putData(self,data) :
        """
        insert a data array in the decompress queues
        """
        self.__append(data,None)
        
    def putImagePath(self,path) :
        """
        Insert a image path file in the decompress queues
        """
        self.__append(None,path)
        
    
    def __append(self,arrayData,path) :
        aLock = QubLock(self.__mutex)
        if self.__plug is not None and not self.__plug.isEnd() :
            while len(self.__dataPending) > 16 : # SIZE QUEUE LIMIT
                self.__cond.wait(self.__mutex)
            dataStruct = QubStdData2Image._data_struct()
            if path is not None :
                dataStruct.setPath(path)
            else :
                dataStruct.setData(arrayData)
            self.__dataPending.append(dataStruct)
            if not self.__actif :
                self.__actif = True
                aLock.unLock()
                self._threadMgr.push(self)

    def getFunc2Process(self) :
        aLock = QubLock(self.__mutex)
        aPendingDataNb = 0
        for dataStruct in self.__dataPending :
            if not dataStruct.inProcess :
                aPendingDataNb += 1
        if aPendingDataNb <= 1 :
            self.__actif = False
            aLock.unLock()
            self._threadMgr.pop(self,False)
        return self.__decompress
    
    def __decompress(self) :
        aLock = QubLock(self.__mutex)
        aWorkingStruct = None
        for dataStruct in self.__dataPending :
            if not dataStruct.inProcess :
                aWorkingStruct = dataStruct
                dataStruct.inProcess = True
                break
        aLock.unLock()
        if aWorkingStruct is not None :
            try :
                if aWorkingStruct.type is QubStdData2Image._data_struct.DATA_TYPE :
                    aWorkingStruct.image.loadFromData(aWorkingStruct.data)
                else :
                    aWorkingStruct.image.load(aWorkingStruct.path)
                aLock.lock()
                aWorkingStruct.end = True
                if self.__plug is not None and not self.__plug.isEnd() :
                    for i,dataStruct in enumerate(self.__dataPending) :
                        if dataStruct.end :
                            self.__postSetImage.append(dataStruct.image)
                        else :
                            break
                    self.__dataPending[0:i + 1] = []
                else :
                    self.__dataPending = []
            except :
                traceback.print_exc()
                self.__dataPending.remove(aWorkingStruct)
            self.__cond.wakeOne()
            aLock.unLock()
            #send event
            event = qt.QCustomEvent(qt.QEvent.User)
            event.event_name = "_postSetImage"
            qt.qApp.postEvent(self,event)
            
    def customEvent(self,event) :
        if event.event_name == "_postSetImage" :
            aLock = QubLock(self.__mutex)
            if self.__plug is not None and not self.__plug.isEnd() :
                for image in self.__postSetImage :
                    if self.__plug.setImage(image) :
                        self.__plug = None
                        break
            else :
                self.__plug = None
            self.__postSetImage = []
class QubStdData2ImagePlug :
    def __init__(self) :
        self.__endFlag = False
    def setEnd(self) :
        self.__endFlag = True
    def isEnd(self) :
        return self.__endFlag

    def setImage(self,image) :
        """
        This methode is call when an image is decompressed
        """
        return True                     # (END)
