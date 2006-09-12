
class QubDrawingEvent :
    def __init__(self) :
        self.__isDisconnect = False
        self.__name = ''
        self.__exceptList = []
        
    def mousePressed(self,x,y) :
        pass
    def mouseReleased(self,x,y) :
        pass
    def mouseMove(self,x,y) :
        pass
    def endDraw(self) :
        pass
    
    def setName(self,name) :
        self.__name = name
    def name(self) :
        return self.__name

    def setExclusiveExcept(self,aExceptList) :
        self.__exceptList = aExceptList
    def exclusiveExceptList(self) :
        return self.__exceptList
    
    def disconnected(self) :
        self.__isDisconnect = True
    def isDisconnected(self) :
        return self.__isDisconnect

class QubPressedNDrag1Point(QubDrawingEvent) :
    def __init__(self,aDrawingMgr,oneShot = True) :
        QubDrawingEvent.__init__(self)
        self.__onShot = oneShot
        self.__drawingMgr = aDrawingMgr
        self.__buttonPressed = False
        
    def mousePressed(self,x,y) :
        self.__buttonPressed = True
        self.__drawingMgr.move(x,y)
        self.__drawingMgr.show()
        return False                    # not END
    
    def mouseReleased(self,x,y) :
        self.__buttonPressed = False
        self.__drawingMgr.move(x,y)
        return self.__onShot
    
    def mouseMove(self,x,y) :
        if self.__buttonPressed :
            self.__drawingMgr.move(x,y)
        return False                    # NOT END

    def endDraw(self) :
        self.__drawingMgr.endDraw()

class QubPressedNDrag2Point(QubDrawingEvent) :
    def __init__(self,aDrawingMgr,oneShot = True) :
        QubDrawingEvent.__init__(self)
        self.__onShot = oneShot
        self.__drawingMgr = aDrawingMgr
        self.__buttonPressed = False

    def mousePressed(self,x,y) :
        self.__buttonPressed = True
        self.__drawingMgr.moveFirstPoint(x,y)
        self.__drawingMgr.moveSecondPoint(x,y)
        self.__drawingMgr.show()
        return False                    # not END

    def mouseReleased(self,x,y) :
        self.__buttonPressed = False
        self.__drawingMgr.moveSecondPoint(x,y)
        return self.__onShot

    def mouseMove(self,x,y) :
        if self.__buttonPressed :
            self.__drawingMgr.moveSecondPoint(x,y)
        return False                    # not END

    def endDraw(self) :
        self.__drawingMgr.endDraw()
