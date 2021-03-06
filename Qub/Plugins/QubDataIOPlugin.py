##@brief this class is the base class for IO data plugins
#
#
#
class QubDataIOPlugin:
    READ,WRITE,RW = [0x1,0x2,0x3]       ##< plugin mode
    def __init__(self,**keys) :
        pass

    ##@brief this methode define the mode of the plugin
    #
    #There is 3 possible modes
    # - <b>READ </b> can only be use in Read mode
    # - <b>WRITE</b> only only be use in Write mode
    # - <b>RW</b> can be use in Both mode Read or write
    #
    def getMode(self) :
        raise NotImplementedError('you have to redefine getMode in class %s' % self.__class__.__name__)

    ##@brief get the extension that are normaly manager by this plugin
    #
    #Use be the gui to do some file filter
    #@return a list of ext ie: ['.jpeg','.jpg']
    def extensionFilter(self) :
        pass

    ##@brief get a read handler
    #
    #@param fd an opened file
    #@return QubDataIOPlugin::ReadHandler or None if is not the format
    def readHandler(self,fd) :
        pass

    ##@brief get write parameters for the plugin
    #
    #@return QWidget
    def getWriteParam(self) :
        pass

    ##@brief get a write handler
    #
    #@param fd an opened file
    #@return QubDataIOPlugin::WriteHandler
    def writeHandler(self,fd) :
        pass

    ##@brief get information about the plugin
    #
    def getPluginInfo(self) :
        pass

    class ReadHandler:
        def __init__(self,**keys) :
            pass
        ##@brief return the number of data block in file
        #
        def getNumData(self) :
            return 1
        ##@brief get the size of the data
        #
        #@param index of data in file
        #@return the size of data in bytes
        def getDataSize(self,index = 0) :
            pass
        ##@brief get data
        #
        #@param index of the data in file
        #@param roi of data a tuple (x,y,width,height)
        #@return a numpy array
        def get(self,index = 0,roi = None,**keys) :
            raise NotImplementedError('you have to redefine get in class %s' % self.__class__.__name__)

        ##@brief get data source
        #
        #@return a dictionnary of a hierarchic data source tree
        #(Qub::Data::Class::QubDataClass)
        #
        def getDataSource(self) :
            raise NotImplementedError('you have to redefine getDataSource in class %s' % self.__class__.__name__)

        ##@brief get info handler of data
        #
        #@param index of the data in file
        #@return a dictionnary info
        def info(self,index = 0) :
            pass

    class WriteHandler:
        ##@brief write data
        #
        #@param data a numpy array
        #@param writeParam the param class of the plugin
        #@param index of data in file
        #@see QubDataIOPlugin::getWriteParam
        def write(self,data,writeParam = None,index = 0) :
            raise NotImplementedError('you have to redefine write in class %s' % self.__class__.__name__)

        ##@brief test if the plugin is able to store several data in one file
        #
        def isMultiDataFormat(self) :
            return False
        
