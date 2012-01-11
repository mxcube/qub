import numpy

from Qub.CTools import polygone

##@brief create a scan class from a xml element tree
#
#@param elementTree an object from xml.etree.ElementTree
def create_scan_from_xml_ElementTree(elementTree) :
    if elementTree.tag == 'scan':
        scan_type = elementTree.attrib.get('scan_type',None)
        if scan_type == 'lookup':
            return _LookUpScan(elementTree)

class QubScanInfo:
    def __init__(self,elementTree = None,**keys):
        self._elemetTree = elementTree
    ##@brief this methode should be redefined in subclass
    #
    #@return usually a numpy array
    def getMotorPos(self) :
        pass
    ##@brief this methode should be redefine in subclass
    #
    #@return a list of motor in the order as the numpy array
    #@see getMotorPos
    def getMotorName(self) :
        pass

class _LookUpScan(QubScanInfo) :
    def __init__(self,**keys) :
        QubScanInfo.__init__(self,**keys)
        self.__posMot1 = self.__posMot2 = None
        
    def getMotorPos(self) :
        if self.__posMot1 is None:
            gridElement = self._elemetTree.find('grid')
            angle = float(gridElement['angle'])
            nbAxis1 = int(gridElement['nbAxis1'])
            nbAxis2 = int(gridElement['nbAxis2'])
            gridPoint = []
            for point in gridElement.getchildren() :
                if point.tag == 'point':
                    gridPoint.append((float(point.attrib['x']),
                                      float(point.attrib['y'])))
            gridPoint = numpy.array(gridPoint)
            rotation = numpy.matrix([[numpy.cos(angle),-numpy.sin(angle)],
                                     [numpy.sin(angle),numpy.cos(angle)]])
            translation = numpy.matrix([gridPoint[0][0],gridPoint[0][1]])

            gridPoint -= translation
            gridPoint = gridPoint * rotation
            gridPoint = numpy.array([[x,y] for y in numpy.linspace(gridPoint[0,1],gridPoint[2,1],nbAxis2 + 1)\
                                     for x in numpy.linspace(gridPoint[0,0],gridPoint[1,0],nbAxis1 + 1)])

            rotation = numpy.matrix([[numpy.cos(-angle),-numpy.sin(-angle)],
                                     [numpy.sin(-angle),numpy.cos(-angle)]])

            gridPoint = gridPoint * rotation
            gridPoint += translation

            includePolygone,excludePolygone = [],[]

            polygoneElement = self._elemetTree.find('polygones')
            for polyE in polygones.getchildren() :
                if polyE.tag == 'poly':
                    points = []
                    for p in poly.getchildren() :
                        if p.tag = 'point':
                            points.append((float(p['x']),float(p['y'])))
                    if bool(polyE.attrib['includeMode']) :
                        includeMode.append(points)
                    else:
                        excludePolygone.append(points)

            maskPoint = []
            pointGrid = gridPoint.tolist()
            for points in includePolygone:
                pInPoly = polygone.points_inclusion(pointGrid,points,False)
                if not maskPoint:
                    maskPoint = pInPoly
                else:
                    maskPoint = [a > 0 or b > 0 for a,b in zip(pInPoly,maskPoint)]

            if not maskPoint:
                maskPoint = [True] * len(gridPoint)

            for points in excludePolygone:
                pInPoly = polygone.points_inclusion(pointGrid,points,False)
                maskPoint = [a > 0 and not b > 0 for a,b in zip(maskPoint,pInPoly)]


            beamElement = self._elemetTree.find('beampos')
            beamx,beamy = float(beamElement.attrib['x']),float(beamElement.attrib['y'])

            pixel2motorElem = self._elemetTree.find('pixel2motor')
            pixel2Mot1 = float(pixel2motorElem.attrib['mot1'])
            pixel2Mot2 = float(pixel2motorElem.attrib['mot2'])

            motorPosElem = self._elemetTree.find('motorpos')
            mot1Pos = float(motorPosElem['mot1'])
            mot2Pos = float(motorPosElem['mot2'])

            posMot1 = []
            posMot2 = []
            for match,point in zip(maskPoint,gridPoint):
                if match:
                  posMot1.append(point[0,0])
                  posMot2.append(point[0,1])

            if posMot1:
                posMot1 = numpy.array(posMot1)
                posMot1 -= beamx
                posMot1 *= pixel2Mot1
                self.__posMot1 = posMot1 + mot1Pos

                posMot2 = numpy.array(posMot2)
                posMot2 -= beamy
                posMot2 *= pixel2Mot2
                self.__posMot2 = posMot2 + mot2Pos
            
        return self.__posMot1,self.__posMot2

    def getMotorName(self) :
        motorNameElem = self._elemetTree.find('motorname')
        return motorNameElem['mot1'],motorNameElem['mot2']

                    
