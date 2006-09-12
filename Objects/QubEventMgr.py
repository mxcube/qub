import qt
import weakref

class QubEventMgr:
    def __init__(self) :
	self.__pendingDrawing = []
	self.__drawingMgr = []


    def addDrawingMgr(self,aDrawingMgr) :
        self.__drawingMgr.append(weakref.ref(aDrawingMgr,self.__weakRefDrawingMgrRemove))
        aDrawingMgr.setEventMgr(self)

    def addDrawingEvent(self,aDrawingEvent) :
        self.__pendingDrawing.append(weakref.ref(aDrawingEvent,self.__weakRefEventRemove))

    def _mousePressed(self,event) :
        try:
            if event.button() == qt.Qt.LeftButton :
                for drawingEventRef in self.__pendingDrawing :
                    if(drawingEventRef().isDisconnected() or 
                       drawingEventRef().mousePressed(event.x(),event.y())) :
                        self._rmDrawingEventRef(drawingEventRef)
        except:
            import traceback
            traceback.print_exc()
            
    def _mouseMove(self,event) :
        try:
            if event.state() == qt.Qt.LeftButton :
                for drawingEventRef in self.__pendingDrawing :
                    if(drawingEventRef().isDisconnected() or
                       drawingEventRef().mouseMove(event.x(),event.y())) :
                        self._rmDrawingEventRef(drawingEventRef)
        except:
            import traceback
            traceback.print_exc()
            
    def _mouseRelease(self,event) :
        try:
            if event.state() == qt.Qt.LeftButton :
               for drawingEventRef in self.__pendingDrawing :
                    if(drawingEventRef().isDisconnected() or
                       drawingEventRef().mouseReleased(event.x(),event.y())) :
                        self._rmDrawingEventRef(drawingEventRef)
        except:
            import traceback
            traceback.print_exc()

    def _update(self) :
        for drawingMgr in self.__drawingMgr :
            try:
                drawingMgr().update()
            except:
                import traceback
                traceback.print_exc()
                
    def _rmDrawingEventRef(self,aDrawingEventRef) :
        try:
            self.__pendingDrawing.remove(aDrawingEventRef)
            aDrawingEventRef().endDraw()
        except:
            pass

    def __weakRefEventRemove(self,eventRef) :
        try :
            self.__pendingDrawing.remove(eventRef)
        except:
            pass
    def __weakRefDrawingMgrRemove(self,mgrRef) :
        try:
            self.__drawingMgr.remove(mgrRef)
        except:
            pass
