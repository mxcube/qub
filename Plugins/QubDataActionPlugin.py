##@brief this class is the base class for data action plugins
#
class QubDataActionPlugin :
    def __init__(self,**keys) :
        pass
    ##@brief methode to init the plugin
    #
    #@param dataDisplay is an object link Qub::Widget::QubDataDisplay
    def initPlugin(self,dataDisplay) :
        raise NotImplementedError('you have to redefine initPlugin in class %s' % self.__class__.__name__)

    ##@brief get information about the plugin
    #
    def getPluginInfo(self) :
        pass
 
