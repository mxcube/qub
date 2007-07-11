class QubDataFileStreamIO:
    def __init__(self,filepath = None,index = 0,plugInClass = None) :
        self._filePath = filepath
        self._index = index
        self._pluginClass = plugInClass

    def get(self,**keys) :
        fd = file(self._filePath)
        try:
            plugIn = self._pluginClass()
            readHandler = plugIn.readHandler(fd)
            dataArray = readHandler.get(index = self._index,**keys)
            info = readHandler.info(index = self._index)
            return dataArray,info
        except:
            import traceback
            traceback.print_exc()
            fd.close()
            
    def plug(self,aPlug) :
        pass
