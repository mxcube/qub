##@brief this class is used to
#transform x,y image coordonnees into other coordonnees
#and manage the curves draw
class QubDataScale:
    def __init__(self,**keys) :
        pass
    ##@brief this methode is use to change coordonnees' labels
    #
    #@return a labels in sequence (tuple or list)
    def getLabels(self) :
        pass

    ##@brief this methode transform image coordonnees into other
    #
    #@return coordonnees values in the same order than the labels (tuple or list)
    #@param x the column id in image
    #@param y the row id in image 
    #@see getLabels
    def transform(self,x,y) :
        pass

    ##@brief this methode draw curves in a graph
    #
    #@param x a numpy table column ids
    #@param y a numpy table row ids
    #@param graph a QubGraph
    def drawCurves(self,x,y,graph) :
        pass
