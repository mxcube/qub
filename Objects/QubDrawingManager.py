import weakref
import qt
from Qub.Objects.QubDrawingEvent import QubPressedNDrag1Point,QubPressedNDrag2Point
from Qub.Objects.QubDrawingEvent import QubModifyAbsoluteAction
from Qub.Objects.QubDrawingEvent import QubModifyRelativeAction
from Qub.Tools import QubWeakref

class QubDrawingMgr :
    """ Base class of Drawing manager
    """
    def __init__(self,aCanvas,aMatrix) :
        self._matrix = aMatrix
        self._canvas = aCanvas
        self._drawingObjects = []
        self._foreignObjects = []       # Object from other Views
        self._eventMgr = None
        self._lastEvent = None
        self._oneShot = False
        self._drawingEvent = None
        self.__exclusive = True
        self.__exceptList = []          # event Name with is not exclusive
        self.__eventName = ''
        self.__cantBeModify = True
        
    def __del__(self) :
        for drawingObject in self._drawingObjects :
            drawingObject.setCanvas(None)
        for link,canvas,matrix,objectlist in self._foreignObjects :
            for drawingObject in objectlist :
                drawingObject.setCanvas(None)
                
                    ####### PUBLIC METHODE #######
    def addDrawingObject(self,aDrawingObject) :
        try :
            self._drawingObjects.append(aDrawingObject)
            if hasattr(aDrawingObject,'setScrollView') and self._eventMgr is not None :
                aDrawingObject.setScrollView(self._eventMgr.scrollView())
            if hasattr(aDrawingObject,'setMatrix') :
                aDrawingObject.setMatrix(self._matrix)
            for link,canvas,matrix,objectlist in self._foreignObjects :
                newObject = aDrawingObject.__class__(None)
                newObject.setCanvas(canvas)
                if hasattr(newObject,'setScrollView') :
                    otherMgr = link().getOtherMgr(self._eventMgr)
                    newObject.setScrollView(otherMgr.scrollView())
                if hasattr(newObject,'setMatrix') :
                    otherMgr = link().getOtherMgr(self._eventMgr)
                    newObject.setMatrix(matrix)
                objectlist.append(newObject)
        except:
            import traceback
            traceback.print_exc()
            
    def removeDrawingObject(self,aDrawingObject) :
        aFindFlag = False
        for i,drawingObject in enumerate(self._drawingObjects):
            if aDrawingObject == drawingObject :
                aFindFlag = True
                break
        if aFindFlag :
            self._drawingObjects.pop(i)
            for link,canvas,matrix,objectlist in self._foreignObjects :
                objectlist.pop(i)
                
    def hide(self) :
        for drawingObject in self._drawingObjects :
            drawingObject.hide()
        for link,canvas,matrix,objectlist in self._foreignObjects :
            for drawingObject in objectlist :
                drawingObject.hide()
                
    def show(self) :
        try :
            for drawingObject in self._drawingObjects :
                drawingObject.show()
            for link,canvas,matrix,objectlist in self._foreignObjects :
                for drawingObject in objectlist :
                    drawingObject.show()
        except:
            import traceback
            traceback.print_exc()
            

    def setCanBeModify(self,aFlag) :
        """
        authorize the user to modify the drawing manager ie :
                  -> resized,moved....
        """
        self.__cantBeModify = aFlag
        
    def setAutoDisconnectEvent(self,aFlag) :
        """
        disconnect the event at the end of procedure otherwise
        the event is keep in the event loop as soon as the startDrawing is called
        default = False
        """
        self._oneShot = aFlag
        
    def setExclusive(self,aFlag) :
        """
        set the exclusivity of the event :
            if True (default) the event loop will exclude every other
               event which is not in the ExceptExclusiveList when
               startDrawing is called
            if False not exclusive
        see setExceptExclusiveListName
        see setEventName
        """
        self.__exclusive = bool(aFlag)
        
    def setExceptExclusiveListName(self,names) :
        """
        list of event names that is not exclusive with this drawing
        see setEventName
        see setExclusive
        """
        self.__exceptList = names

    def setEventName(self,name) :
        """
        the name of the event, its use to make the exclusion
        see setExclusive
        see setExceptExclusiveListName
        """
        self.__eventName = name
        
    def setColor(self,color) :
        for drawingObject in self._drawingObjects :
            pen = drawingObject.pen()
            pen.setColor(color)
            drawingObject.setPen(pen)
        for link,canvas,matrix,objectlist in self._foreignObjects :
            for drawingObject in objectlist :
                pen = drawingObject.pen()
                pen.setColor(color)
                drawingObject.setPen(pen)
                
    def startDrawing(self) :
        """
        start the drawing procedure, now this object will listen the event loop :
               -> mouse move,click...
        """
        if self._eventMgr is not None :
            self._lastEvent = self._getDrawingEvent()
            if self._lastEvent is not None :
                self._lastEvent.setExceptExclusiveListName(self.__exceptList)
                self._lastEvent.setExclusive(self.__exclusive)
                self._lastEvent.setName(self.__eventName)
                self._eventMgr.addDrawingEvent(self._lastEvent)

    def stopDrawing(self) :
        """
        this methode ends the listening of the event loop
        """
        self._lastEvent = None
                    
    def setEndDrawCallBack(self,cbk) :
        """
        set the end callback procedure
        """
        self._endDrawCbk = cbk

    def setDrawingEvent(self,event) :
        """
        change the drawing procedure beavior
        see QubDrawingEvent
        """
        self._drawingEvent = event
        
                ####### END OF PUBLIC METHODES #######
    def boundingRect(self) :
        returnRect = None
        for drawingObject in self._drawingObjects :
            objectRect = drawingObject.boundingRect()
            if returnRect is not None :
                returnRect = objectRect.unit(returnRect)
            else :
                returnRect = objectRect
        return returnRect
        
    def endDraw(self) :
        """
        This methode is call at the end of the drawing procedure
        """
        if self._endDrawCbk is not None :
            self._endDrawCbk(self)
            
    def addSetHandleMethodToEachDrawingObject(self,call_back,methode_name = '') :
        """
        add a methode named : methode_name if is define or the name of the call_back
        when call this methode will apply the call_back on each drawingObject
        """
        newCallable = _foreach_callable(self.__foreach_set,call_back)
        if methode_name :
            self.__dict__[methode_name] = newCallable
        else :
            try:
                self.__dict__[call_back.im_func.func_name] = newCallable
            except AttributeError:
                self.__dict__[call_back.func_name] = newCallable
    
            ####### HAS TO BE REDEFINE IN SUBCLASS #######
    def update(self) :
        raise StandardError('update has to be redifined')

    def _getDrawingEvent(self) :
        raise StandardError('_getDrawingEvent has to be redifined')

    def _getModifyClass(self,x,y) :
        return None

                ####### CALL BY THE EVENT LOOP #######
    def getModifyClass(self,x,y) :
        if self.__cantBeModify :
            aVisibleFlag = False
            for drawingObject in self._drawingObjects :
                if drawingObject.isVisible() :
                    aVisibleFlag = True
                    break
            if aVisibleFlag :
                return self._getModifyClass(x,y)

    def setEventMgr(self,anEventMgr) :
        self._eventMgr = anEventMgr
        for drawingObject in self._drawingObjects :
            if hasattr(drawingObject,'setScrollView') :
                drawingObject.setScrollView(self._eventMgr.scrollView())

    def addLinkEventMgr(self,aLinkEventMgr) :
        try:
            canvas,matrix = aLinkEventMgr.getCanvasNMatrix(self._eventMgr)
            newObjects = []
            for drawing in self._drawingObjects :
                nObject = drawing.__class__(None)
                nObject.setCanvas(canvas)
                if hasattr(nObject,'setScrollView') :
                    otherMgr = aLinkEventMgr.getOtherMgr(self._eventMgr)
                    nObject.setScrollView(otherMgr.scrollView())
                if hasattr(nObject,'setMatrix') :
                    otherMgr = aLinkEventMgr.getOtherMgr(self._eventMgr)
                    nObject.setMatrix(matrix)
                newObjects.append(nObject)
            self._foreignObjects.append((weakref.ref(aLinkEventMgr,QubWeakref.createWeakrefMethod(self.__linkRm)),
                                         canvas,matrix,newObjects))
        except:
            import traceback
            traceback.print_exc()
        
    def __linkRm(self,linkref) :
        for link,canvas,matrix,objectlist in self._foreignObjects :
            if link == linkref :
                for drawingObject in objectlist :
                    drawingObject.setCanvas(None)
                self._foreignObjects.remove((link,canvas,matrix,objectlist))
                break

    def __foreach_set(self,callback,*args,**keys) :
        try :
            for drawingObject in self._drawingObjects :
                callback(drawingObject,*args,**keys)
            for link,canvas,matrix,objectlist in self._foreignObjects :
                for drawingObject in objectlist :
                    callback(drawingObject,*args,**keys)
        except:
            import traceback
            traceback.print_exc()
            
class QubContainerDrawingMgr(QubDrawingMgr) :
    """
    this class is a container of stand alone drawing object
    """
    def __init__(self,aCanvas,aMatrix = None) :
        QubDrawingMgr.__init__(self,aCanvas,aMatrix)

    def update(self) :
        try :
            for drawingObject in self._drawingObjects :
                drawingObject.update()
            for link,canvas,matrix,objectlist in self._foreignObjects :
                for drawingObject in objectlist :
                    drawingObject.update()
        except:
            import traceback
            traceback.print_exc()
            
    def _getDrawingEvent(self) :
        return None                     # just in case that someone call startDrawing

class QubPointDrawingMgr(QubDrawingMgr) :
    """
    This class manage all the drawing object
    that can be define with one point
    """
    def __init__(self,aCanvas,aMatrix = None) :
        QubDrawingMgr.__init__(self,aCanvas,aMatrix)
        self._x,self._y = 0,0
        self._drawingEvent = QubPressedNDrag1Point
                
                    ####### PUBLIC METHODE #######
    def setPoint(self,x,y) :
        self._x,self._y = x,y
        self.update()

    def point(self) :
        return (self._x,self._y)

        
               ####### INTERNAL LOOP EVENT CALL #######
    def move(self,x,y) :
        if self._matrix is not None :
            self._x,self._y = self._matrix.invert()[0].map(x,y)
        else:
            self._x,self._y = (x,y)

        for drawingObject in self._drawingObjects :
            drawingObject.move(x,y)

        self._drawForeignObject()

    def update(self) :
        if self._matrix is not None :
            x,y = self._matrix.map(self._x,self._y)
        else :
            x,y = self._x,self._y
            
        for drawingObject in self._drawingObjects :
            drawingObject.move(x,y)

        self._drawForeignObject()
        
    def _getModifyClass(self,x,y) :
        rect = self.boundingRect()
        if rect.contains(x,y) : 
            return QubModifyAbsoluteAction(self,self._eventMgr,self.move)

    def _getDrawingEvent(self) :
        return self._drawingEvent(self,self._oneShot)

    def _drawForeignObject(self) :
        try:
            for link,canvas,matrix,objectlist in self._foreignObjects :
                x,y = self._x,self._y
                if matrix is not None :
                    x,y = matrix.map(x,y)
                for drawingObject in objectlist :
                    drawingObject.move(x,y)
        except:
            import traceback
            traceback.print_exc()
            
class QubLineDrawingManager(QubDrawingMgr) :
    def __init__(self,aCanvas,aMatrix = None) :
        QubDrawingMgr.__init__(self,aCanvas,aMatrix)
        self._x1,self._y1 = 0,0
        self._x2,self._y2 = 0,0
        self._drawingEvent = QubPressedNDrag2Point

                    ####### PUBLIC METHODE #######
    def setPoints(self,x1,y1,x2,y2) :
        self._x1,self._y1 = x1,y1
        self._x2,self._y2 = x2,y2
        self.update()

    def points(self) :
        return (self._x1,self._y1,self._x2,self._y2)
    
        
               ####### INTERNAL LOOP EVENT CALL #######
    def moveFirstPoint(self,x,y) :
        if self._matrix is not None :
            self._x1,self._y1 = self._matrix.invert()[0].map(x,y)
            x2,y2 = self._matrix.map(self._x2,self._y2)
        else:
            self._x1,self._y1 = x,y
            x2,y2 = self._x2,self._y2
        
        for drawingObject in self._drawingObjects :
            drawingObject.setPoints(x,y,x2,y2)

        self._drawForeignObject()

    def moveSecondPoint(self,x,y) :
        if self._matrix is not None :
            self._x2,self._y2 = self._matrix.invert()[0].map(x,y)
            x1,y1 = self._matrix.map(self._x1,self._y1)
        else:
            self._x2,self._y2 = x,y
            x1,y1 = self._x1,self._y1
        
        for drawingObject in self._drawingObjects :
            drawingObject.setPoints(x1,y1,x,y)

        self._drawForeignObject()

    def update(self) :
        if self._matrix is not None :
            x1,y1 = self._matrix.map(self._x1,self._y1)
            x2,y2 = self._matrix.map(self._x2,self._y2)
        else :
            x1,y1 = self._x1,self._y1
            x2,y2 = self._x2,self._y2
            
        for drawingObject in self._drawingObjects :
            drawingObject.setPoints(x1,y1,x2,y2)

        self._drawForeignObject()
        
    def _getDrawingEvent(self) :
        return self._drawingEvent(self,self._oneShot)
            
    def _getModifyClass(self,x,y) :
        (x1,y1,x2,y2) = self._x1,self._y1,self._x2,self._y2
        if self._matrix is not None :
            x1,y1 = self._matrix.map(x1,y1)
            x2,y2 = self._matrix.map(x2,y2)
            
        if(abs(x - x1) < 5 and abs(y - y1) < 5) :
            return QubModifyAbsoluteAction(self,self._eventMgr,self.moveFirstPoint)
        elif(abs(x - x2) < 5 and abs(y - y2) < 5) :
            return QubModifyAbsoluteAction(self,self._eventMgr,self.moveSecondPoint)

    def _drawForeignObject(self) :
        for link,canvas,matrix,objectlist in self._foreignObjects :
            x1,y1 = self._x1,self._y1
            x2,y2 = self._x2,self._y2
            if matrix is not None :
                x1,y1 = matrix.map(x1,y1)
                x2,y2 = matrix.map(x2,y2)
                
            for drawingObject in objectlist :
                drawingObject.setPoints(x1,y1,x2,y2)

        
class Qub2PointSurfaceDrawingManager(QubDrawingMgr) :
    def __init__(self,aCanvas,aMatrix = None) :
        QubDrawingMgr.__init__(self,aCanvas,aMatrix)
        self._rect = qt.QRect(0,0,1,1)
        self._drawingEvent = QubPressedNDrag2Point
        
                    ####### PUBLIC METHODE #######
    def setPoints(self,x1,y1,x2,y2) :
        self._rect.setCoords(x1,y1,x2,y2);
        self.update()
        
    def setRect(self,x,y,w,h) :
        self._rect.setRect(x,y,w,h);
        self.update()

    def rect(self) :
        rect = self._rect.normalize()
        return rect
    
               ####### INTERNAL LOOP EVENT CALL #######
    def moveFirstPoint(self,x,y) :
        if self._matrix is not None :
            xNew,yNew = self._matrix.invert()[0].map(x,y)
        else :
            xNew,yNew = x,y
        (x1,y1,x2,y2) = self._rect.coords()
        self._rect.setCoords(xNew,yNew,x2,y2)
        self.update()

    def moveSecondPoint(self,x,y) :
        if self._matrix is not None :
            xNew,yNew = self._matrix.invert()[0].map(x,y)
        else :
            xNew,yNew = x,y
        (x1,y1,x2,y2) = self._rect.coords()
        self._rect.setCoords(x1,y1,xNew,yNew)
        self.update()

    def moveTopRight(self,x,y) :
        if self._matrix is not None :
            xNew,yNew = self._matrix.invert()[0].map(x,y)
        else :
            xNew,yNew = x,y
        (x1,y1,x2,y2) = self._rect.coords()
        self._rect.setCoords(x1,yNew,xNew,y2)
        self.update()

    def moveBottomLeft(self,x,y) :
        if self._matrix is not None :
            xNew,yNew = self._matrix.invert()[0].map(x,y)
        else :
            xNew,yNew = x,y
        (x1,y1,x2,y2) = self._rect.coords()
        self._rect.setCoords(xNew,y1,x2,yNew)
        self.update()

    def moveRelativeRectangle(self, dx, dy):
        if self._matrix is not None :
            dxNew,dyNew = self._matrix.invert()[0].map(dx,dy)
        else:
            dxNew,dyNew = dx, dy
        self._rect.moveBy(dxNew, dyNew)
        self.update()

    def width(self) :
        width = 0
        try:
            for drawingObject in self._drawingObjects :
                tmpWidth = drawingObject.width()
                if tmpWidth > width :
                    width = tmpWidth
        except:
            import traceback
            traceback.print_exc()
        return width

    def height(self) :
        height = 0
        try:
            for drawingObject in self._drawingObjects :
                tmpHeight = drawingObject.height()
                if tmpHeight > height :
                    height = tmpHeight
        except:
            import traceback
            traceback.print_exc()
        return height
    
    def update(self) :
        rect = self._rect.normalize()
        if self._matrix is not None :
            rect = self._matrix.map(rect)
        x,y,width,height = rect.rect()
        for drawingObject in self._drawingObjects :
            drawingObject.move(x,y)
            drawingObject.setSize(width,height)
        self._drawForeignObject()
        
    def _getDrawingEvent(self) :
        return self._drawingEvent(self,self._oneShot)

    def _getModifyClass(self,x,y) :
        rect = self._rect.normalize()
        self._rect = rect
        if self._matrix is not None :
            rect = self._matrix.map(rect)
        (x1,y1,x2,y2) = rect.coords()
        if(abs(x - x1) < 5) :           # TOP LEFT OR BOTTOM LEFT
            if(abs(y - y1) < 5) :       # TOP LEFT
                return QubModifyAbsoluteAction(self,self._eventMgr,
                                       self.moveFirstPoint,
                                       qt.QCursor(qt.Qt.SizeFDiagCursor))
            elif(abs(y - y2) < 5) :     # BOTTOM LEFT
                return QubModifyAbsoluteAction(self,self._eventMgr,
                                       self.moveBottomLeft,
                                       qt.QCursor(qt.Qt.SizeBDiagCursor))
        elif(abs(x - x2) < 5) :         # TOP RIGHT OR BOTTOM RIGHT
            if(abs(y - y1) < 5) :       # TOP RIGHT
                return QubModifyAbsoluteAction(self,self._eventMgr,
                                       self.moveTopRight,
                                       qt.QCursor(qt.Qt.SizeBDiagCursor))
            elif(abs(y - y2) < 5) :
                return QubModifyAbsoluteAction(self,self._eventMgr,
                                       self.moveSecondPoint,
                                       qt.QCursor(qt.Qt.SizeFDiagCursor))
        elif (rect.contains(x, y)):
                return QubModifyRelativeAction(self,self._eventMgr,
                                       self.moveRelativeRectangle)
            
    def _drawForeignObject(self) :
        for link,canvas,matrix,objectlist in self._foreignObjects :
            rect = self._rect.normalize()
            if matrix is not None :
                rect = matrix.map(rect)
            x,y,width,height = rect.rect()
            for drawingObject in objectlist :
                drawingObject.move(x,y)
                drawingObject.setSize(width,height)

############################## Callable ##############################
class _foreach_callable :
    def __init__(self,meth,callback) :
        self.__objRef = weakref.ref(meth.im_self)
        self.__func_meth = weakref.ref(meth.im_func)
        try :
            self.__cbk = weakref.ref(callback.im_func)
        except AttributeError :
            self.__cbk = weakref.ref(callback)
    def __call__(self,*args,**keys) :
        aReturnFlag = False
        try:
            if self.__cbk() is not None :
                self.__func_meth()(self.__objRef(),self.__cbk(),*args,**keys)
                aReturnFlag = True
        except:
            import traceback
            traceback.print_exc()
        return aReturnFlag
