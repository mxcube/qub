##@brief this class is the base class for data action plugins
#
#This is a way to add action (Qub::Widget::QubAction::QubImageAction) on a data display object.
#Action are tools which are display in the tool bar,status bar or context menu of the data display object
#There is two kind of action :
# - Those who need data (Qub::Widget::QubDataDisplay::QubDataDisplay::addDataAction)
# - Those who don't need data (Qub::Widget::QubDataDisplay::QubDataDisplay::addAction)
#
#So in the initPlugin function, you just have to insert your action in the data display object by calling addAction or
#addDataAction
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
 
