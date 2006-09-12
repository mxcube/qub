import qt
from Qub.Objects.QubDrawingEvent import QubPressedNDrag1Point,QubPressedNDrag2Point

class QubDrawingMgr :
    def __init__(self,aCanvas,aMatrix) :
        self._matrix = aMatrix
        self._canvas = aCanvas
        self._drawingObjects = []
        self._eventMgr = None
        self._lastEvent = None

    def __del__(self) :
        for drawingObject in self._drawingObjects :
            if hasattr(drawingObject,'removeInCanvas') :
                drawingObject.removeInCanvas()
            else:
                drawingObject.setCanvas(None)
            
    def addDrawingObject(self,aDrawingObject) :
        self._drawingObjects.append(aDrawingObject)

    def removeDrawingObject(self,aDrawingObject) :
        try :
            self._drawingObjects.remove(aDrawingObject)
        except:
            pass
        
    def hide(self) :
        for drawingObject in self._drawingObjects :
            drawingObject.hide()
    def show(self) :
        for drawingObject in self._drawingObjects :
            drawingObject.show()


    def boundingRect(self) :
        returnRect = None
        for drawingObject in self._drawingObjects :
            objectRect = drawingObject.boundingRect()
            if returnRect is not None :
                returnRect = objectRect.unit(returnRect)
            else :
                returnRect = objectRect
        return returnRect
        
    def getResizeClass(self,x,y) :
        return None

    def getMoveClass(self,x,y) :
        return None

    def update(self) :
        raise StandardError('update has to be redifined')

    def startDrawing(self) :
        if self._eventMgr is not None :
            self._lastEvent = self._getDrawingEvent()
            self._eventMgr.addDrawingEvent(self._lastEvent)

    def stopDrawing(self) :
        if self._lastEvent is not None :
            self._lastEvent.disconnected()
            
    def setEventMgr(self,anEventMgr) :
        self._eventMgr = anEventMgr

    def setEndDrawCallBack(self,cbk) :
        self._endDrawCbk = cbk
        
    def endDraw(self) :
        """
        This methode is call at the end of the draw event
        """
        if self._endDrawCbk is not None :
            self._endDrawCbk(self)
        self._lastEvent = None
        
    def _getDrawingEvent(self) :
        raise StandardError('_getDrawingEvent has to be redifined')

class QubPointDrawingMgr(QubDrawingMgr) :
    def __init__(self,aCanvas,aMatrix = None) :
        QubDrawingMgr.__init__(self,aCanvas,aMatrix)
        self._x,self._y = 0,0
        
    def move(self,x,y) :
        if self._matrix is not None :
            self._x,self._y = self._matrix.invert()[0].map(x,y)
        else:
            self._x,self._y = (x,y)

        for drawingObject in self._drawingObjects :
            drawingObject.move(x,y)
                
    def setPoint(self,x,y) :
        self._x,self._y = x,y
        self.update()

    def point(self) :
        return (self._x,self._y)


    def update(self) :
        if self._matrix is not None :
            x,y = self._matrix.map(self._x,self._y)
        else :
            x,y = self._x,self._y
            
        for drawingObject in self._drawingObjects :
            drawingObject.move(x,y)

    def _getDrawingEvent(self) :
        return QubPressedNDrag1Point(self)

class QubLineDrawingManager(QubDrawingMgr) :
    def __init__(self,aCanvas,aMatrix = None) :
        QubDrawingMgr.__init__(self,aCanvas,aMatrix)
        self._x1,self._y1 = 0,0
        self._x2,self._y2 = 0,0

    def moveFirstPoint(self,x,y) :
        if self._matrix is not None :
            self._x1,self._y1 = self._matrix.invert()[0].map(x,y)
            x2,y2 = self._matrix.map(self._x2,self._y2)
        else:
            self._x1,self._y1 = x,y
            x2,y2 = self._x2,self._y2
        
        for drawingObject in self._drawingObjects :
            drawingObject.setPoints(x,y,x2,y2)

    def moveSecondPoint(self,x,y) :
        if self._matrix is not None :
            self._x2,self._y2 = self._matrix.invert()[0].map(x,y)
            x1,y1 = self._matrix.map(self._x1,self._y1)
        else:
            self._x2,self._y2 = x,y
            x1,y1 = self._x1,self._y1
        
        for drawingObject in self._drawingObjects :
            drawingObject.setPoints(x1,y1,x,y)

    def setPoints(self,x1,y1,x2,y2) :
        self._x1,self._y1 = x1,y1
        self._x2,self._y2 = x2,y2
        self.update()

    def points(self) :
        return (self._x1,self._y1,self._x2,self._y2)
    
    def update(self) :
        if self._matrix is not None :
            x1,y1 = self._matrix.map(self._x1,self._y1)
            x2,y2 = self._matrix.map(self._x2,self._y2)
        else :
            x1,y1 = self._x1,self._y1
            x2,y2 = self._x2,self._y2
            
        for drawingObject in self._drawingObjects :
            drawingObject.setPoints(x1,y1,x2,y2)

    def _getDrawingEvent(self) :
        return QubPressedNDrag2Point(self)
            
class Qub2PointSurfaceDrawingManager(QubDrawingMgr) :
    def __init__(self,aCanvas,aMatrix = None) :
        QubDrawingMgr.__init__(self,aCanvas,aMatrix)
        self._rect = qt.QRect(0,0,1,1)

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

    def setPoints(self,x1,y1,x2,y2) :
        self._rect.setCoords(x1,y1,x2,y2);
        self.update()

    def rect(self) :
        rect = self._rect.normalize()
        return rect
    
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
        rect = self._matrix.map(self._rect.normalize())
        x,y,width,height = rect.rect()
        for drawingObject in self._drawingObjects :
            drawingObject.move(x,y)
            drawingObject.setSize(width,height)
                
    def _getDrawingEvent(self) :
        return QubPressedNDrag2Point(self)
