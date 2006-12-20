import weakref
import qt
##@defgroup DrawingEvent
#@brief Manager of the event behaviour
#
#They are the link between Qub::Objects::QubEventMgr::QubEventMgr and
#QubDrawingManager.

##@brief base class of drawing event
#@ingroup DrawingEvent
class QubDrawingEvent :
    def __init__(self,exclusive = True,exceptList = []) :
        self.__name = ''
        # exclusive with the name of other event
        self.__exceptList = exceptList
        # if False self.__exceptList is not considered
        self.__exclusive = exclusive
        
    def mousePressed(self,x,y) :
        pass
    def mouseReleased(self,x,y) :
        pass
    def mouseMove(self,x,y) :
        pass

    #@brief called when the event is removed from the polling loop
    def endPolling(self) :
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
    #@brief methode called when the event is just exclude or active again
    #@param aFlag :
    # - if <b>True</b> event is dub (exclude)
    # - else <b>False</b> event is active
    def setDubMode(self,aFlag) :
        pass                            # TODO

    #@return text information about the current action
    def getActionInfo(self) :
        return ''                       # MUST BE REDEFINE
    
class _DrawingEventNDrawingMgr(QubDrawingEvent):
    def __init__(self,aDrawingMgr,oneShot) :
        QubDrawingEvent.__init__(self)
        self._drawingMgr = weakref.ref(aDrawingMgr)
        self._onShot = oneShot
    def getActionInfo(self) :
        return self._drawingMgr().getActionInfo()
    
##@brief A point event behaviour manager.
#@ingroup DrawingEvent
#
#Behaviour description:
# -# show drawing object on init
# -# move the drawing object on mouse move
# -# call the endDraw callback on mouse released
class QubMoveNPressed1Point(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,oneShot) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,oneShot)
        self._drawingMgr().show()
        
    def mouseReleased(self,x,y) :
        self._drawingMgr().move(x,y)
        self._drawingMgr().endDraw()
        return self._onShot
    
    def mouseMove(self,x,y) :
        self._drawingMgr().move(x,y)
        return False                    # NOT END
##@brief The default point event behaviour manager
#@ingroup DrawingEvent
#
#Behaviour description:
# -# show drawing object on mouse pressed
# -# call drawing object move until mouse released
# -# on mouse released call endDraw callback
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
##@brief Set 2 points with a pressed and drag
#@ingroup DrawingEvent
#
#The default line and rectangle behaviour manager
#Behaviour description:
# -# show drawing object on mouse pressed and set the
#absolute position on the first point
# -# move the second point until mouse button is released
# -# on mouse released call endDraw callback
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

##@brief Set 2 points with 2 click
#@ingroup DrawingEvent
#
#Behaviour description:
# -# show drawing object on first mouse pressed
# -# set the first point on first mouse released
# -# start moving the second point since mouse pressed
# -# set the second point on second mouse released and call endDraw callback
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

##@brief Set N point with N click
#@ingroup DrawingEvent
#
#This event behaviour manager is used with polygone.
#Behaviour description:
# -# the drawing object is shown on first mouse pressed
# -# on first mouse released set the first point absolute position
# -# check if it's the end of the draw by testing the return of
#the drawing manager's moving methode:
#    - if it's return <b>True</b> end of draw and call endDraw callback
#    - else go to next point
class QubNPointClick(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,oneShot) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,oneShot)
        self.__pointNb = 0
        self.__active = False
        
    def mousePressed(self,x,y) :
        if self.__pointNb == 0 :
            self._drawingMgr().show()
        self._drawingMgr().move(x,y,self.__pointNb)
        self.__active = True
        
    def mouseReleased(self,x,y) :
        aEndFlag = self._drawingMgr().move(x,y,self.__pointNb)
        if aEndFlag :
            self.__pointNb = 0; self.__active = False
            self._drawingMgr().endDraw()
        else: self.__pointNb += 1
        return aEndFlag and self._onShot

    def mouseMove(self,x,y) :
        if self.__active :
            self._drawingMgr().move(x,y,self.__pointNb)
            
##@brief Modify a point
#@ingroup DrawingEvent
#
#This is the default event behaviour manger to modify point
class QubModifyAbsoluteAction(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,aEventmgr,modifyCBK,
                 cursor = qt.QCursor(qt.Qt.SizeAllCursor)) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,False)
        self._eventmgr = aEventmgr
        self._cursor = cursor
        self._modify = modifyCBK
        self._dirtyFlag = False
        
    def __del__(self) :
        if self._dirtyFlag :
            self._drawingMgr().endDraw()
        
    def setCursor(self,eventMgr) :
        eventMgr.setCursor(self._cursor)
        
    def mousePressed(self, x, y):
        self._dirtyFlag = True
        self._modify(x,y)
                
    def mouseMove(self, x, y):
        pass
                
    def mouseMovePressed(self, x, y):
        self._modify(x, y)
        
    def mouseReleased(self, x, y):
        self._modify(x, y)
        self._dirtyFlag = False
        self._drawingMgr().endDraw()

##@brief Modify a point by relative moving
#@ingroup DrawingEvent
class QubModifyRelativeAction(_DrawingEventNDrawingMgr) :
    def __init__(self,aDrawingMgr,aEventmgr,modifyCBK,
                 cursor = qt.QCursor(qt.Qt.SizeAllCursor)) :
        _DrawingEventNDrawingMgr.__init__(self,aDrawingMgr,False)
        self._eventmgr = aEventmgr
        self._cursor = cursor
        self._modify = modifyCBK
        self._dirtyFlag = False

    def __del__(self) :
        if self._dirtyFlag :
            self._drawingMgr().endDraw()
            
    def setCursor(self,eventMgr) :
        eventMgr.setCursor(self._cursor)

    def mousePressed(self, x, y):
        self._dirtyFlag = True
        self.__oldX = x
        self.__oldY = y
                
    def mouseMove(self, x, y):
        pass

    def mouseMovePressed(self, x, y):
        self._modify(x - self.__oldX, y - self.__oldY)
        self.__oldX = x
        self.__oldY = y        
        
    def mouseReleased(self, x, y):
        self._modify(x - self.__oldX, y - self.__oldY)
        self._dirtyFlag = False
        self._drawingMgr().endDraw()
