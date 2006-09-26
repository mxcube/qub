import weakref
import qt

class QubDrawingEvent :
    def __init__(self,exclusive = True,exceptList = []) :
        self.__name = ''
        self.__exceptList = exceptList  # exclusive with the name of other event
        self.__exclusive = exclusive      # if False self.__exceptList is not considered
        
    def mousePressed(self,x,y) :
        pass
    def mouseReleased(self,x,y) :
        pass
    def mouseMove(self,x,y) :
        pass

    def endPolling(self) :
        """
        called when the event is removed from the polling loop
        """
        pass
    
    def setName(self,name) :
        self.__name = name
    def name(self) :
        return self.__name

    def setExclusive(self,aFlag) :
        self.__exclusive = bool(aFlag)
        
    def setExceptExclusiveListName(self,names) :
        self.__exceptList = names
        
    def exclusive(self) :
        if self.__exclusive :
            return self.__exceptList
        else :
            return False
    def setDubMode(self,aFlag) :
        pass                            # TODO
    
class _DrawingEventNDrawingMgr(QubDrawingEvent):
    def __init__(self,aDrawingMgr,oneShot) :
        QubDrawingEvent.__init__(self)
        self._drawingMgr = weakref.ref(aDrawingMgr)
        self._onShot = oneShot
        
class QubPressedNDrag1Point(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,oneShot) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,oneShot)
        self.__buttonPressed = False
        
    def mousePressed(self,x,y) :
        self.__buttonPressed = True
        self._drawingMgr().show()
        self._drawingMgr().move(x,y)
        return False                    # not END
        
    def mouseReleased(self,x,y) :
        self.__buttonPressed = False
        self._drawingMgr().move(x,y)
        self._drawingMgr().endDraw()
        return self._onShot
    
    def mouseMove(self,x,y) :
        if self.__buttonPressed :
            self._drawingMgr().move(x,y)
        return False                    # NOT END

class QubPressedNDrag2Point(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,oneShot) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,oneShot)
        self.__buttonPressed = False

    def mousePressed(self,x,y) :
        self.__buttonPressed = True
        self._drawingMgr().moveFirstPoint(x,y)
        self._drawingMgr().moveSecondPoint(x,y)
        self._drawingMgr().show()
        return False                    # not END

    def mouseReleased(self,x,y) :
        self.__buttonPressed = False
        self._drawingMgr().moveSecondPoint(x,y)
        self._drawingMgr().endDraw()
        return self._onShot

    def mouseMove(self,x,y) :
        if self.__buttonPressed :
            self._drawingMgr().moveSecondPoint(x,y)
        return False                    # not END

class Qub2PointClick(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,oneShot) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,oneShot)
        self.__active = False
        self.__pointNb = 0

    def mousePressed(self,x,y) :
        self.__active = True
        if not self.__pointNb :         # first press
            self._drawingMgr().moveFirstPoint(x,y)
            self._drawingMgr().moveSecondPoint(x,y)
            self._drawingMgr().show()
        else :                          # second press
            self._drawingMgr().moveSecondPoint(x,y)
        return False
    
    def mouseReleased(self,x,y) :
        returnFlag = False
        if not self.__pointNb :
            self._drawingMgr().moveFirstPoint(x,y)
            self._drawingMgr().moveSecondPoint(x,y)
            self.__pointNb += 1
        else :
            self._drawingMgr().moveSecondPoint(x,y)
            self._drawingMgr().endDraw()
            self.__active = False
            self.__pointNb = 0
            returnFlag = self._onShot
        return returnFlag
    
    def mouseMove(self,x,y) :
        if self.__active :
            if not self.__pointNb :
                self._drawingMgr().moveFirstPoint(x,y)
                self._drawingMgr().moveSecondPoint(x,y)
            else :
                self._drawingMgr().moveSecondPoint(x,y)
        return False
                     ####### MODIFY EVENT #######
class QubModifyAction(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,aEventmgr,modifyCBK,
                 cursor = qt.QCursor(qt.Qt.SizeAllCursor)) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,False)
        self._eventmgr = aEventmgr
        aEventmgr.setCursor(cursor)
        self._modify = modifyCBK
        
    def modify(self,x,y) :
        self._modify(x,y)
        self._drawingMgr().endDraw()
