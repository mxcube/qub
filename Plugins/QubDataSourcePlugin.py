##@brief this class is an interface for data source plugins
#
class QubDataSourcePlugin:
    def __init__(self,name = 'undefined Name',**keys) :
        self._name  = name
        
    ##@brief get the name of the plugin
    #
    #The name is use in the data source popupmenu
    def name(self) :
        return self._name

    ##@brief get information about the plugin
    #
    def getPluginInfo(self) :
        pass
    ##@brief this methode should return
    #data and info as a tuple
    def get(self) :
        pass
    ##@brief this methode is called
    #just before run methode
    #in this methode, you can create or modify some widgets because you are in the main loop
    #@param sourceInterface the interface to the source QubDataSourcePlugin.interface
    #@return should return True if you want to continue
    def initPlugin(self,sourceInterface) :
        pass
    ##@brief this methode is called
    #just after init, this is the real run of the plugin
    #<p style="color:red">You are not allowed to modify any widget during
    #this methode (this methode is called in an other thread)</p>
    def run(self,sourceInterface) :
        pass

    class interface:
        def __init__(self,sourceTree) :
            self.__sourceTree = sourceTree
        ##@brief return the selected items as a dictionnary
        #
        #all param are internal recursive param, just call it without any
        #@return a dictionnary of sources
        def getSelectedSources(self,parent = None,forcedSelected = False) :
            dico = {}
            for item in self.__sourceTree._QubDataSourceTree__getIterator(parent) :
                childDico = self.getSelectedSources(item,item.isSelected())
                if childDico or forcedSelected or item.isSelected():
                    dico[item.getDataClass()] = childDico
            return dico
        ##@brief get all current sources
        #@return a dictionnary of sources
        def getSources(self) :
            return self.getSelectedSources(None,True)
        ##@brief insert data source in the data source tree
        #
        #@param dico a sources dictionnary
        def insertDataSource(self,dico) :
            self.__sourceTree.insertDataSourceInTree(dico)
            

