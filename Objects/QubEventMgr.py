import qt
import weakref
import itertools

class QubEventMgr:
    def __init__(self) :
	self.__pendingEvents = []
        self.__excludedEvent = []
	self.__drawingMgr = []
        self.__mouseX,self.__mouseY = 0,0
        self.__curentModifierMgr = None
        
    def addDrawingMgr(self,aDrawingMgr) :
        self.__drawingMgr.append(weakref.ref(aDrawingMgr,self.__weakRefDrawingMgrRemove))
        aDrawingMgr.setEventMgr(self)

    def addDrawingEvent(self,aDrawingEvent) :
        try:
            exclusive = aDrawingEvent.exclusive()
            if exclusive is not False :
                excludeEvents = []
                for pendingEvent in self.__pendingEvents[:] :
                    if pendingEvent() is None : continue
                    excludePendingEvent = pendingEvent().exclusive()
                    if excludePendingEvent is not False and pendingEvent().name() not in exclusive :
                        pendingEvent().setDubMode(True)
                        self.__pendingEvents.remove(pendingEvent)
                        excludeEvents.append(pendingEvent)
                if len(excludeEvents) :
                    self.__excludedEvent.append((weakref.ref(aDrawingEvent,self.__weakRefEventRemove),excludeEvents))
            self.__pendingEvents.append(weakref.ref(aDrawingEvent,self.__weakRefEventRemove))
        except:
            import traceback
            traceback.print_exc()
            
    def _mousePressed(self,event) :
        try:
            if event.button() == (qt.Qt.LeftButton + qt.Qt.ShiftButton) :
                self.__checkObjectModify(event.x(),event.y())
            elif event.button() == qt.Qt.LeftButton :
                for drawingEventRef in self.__pendingEvents[:] :
                    if(drawingEventRef().mousePressed(event.x(),event.y())) :
                        self._rmDrawingEventRef(drawingEventRef)

        except:
            import traceback
            traceback.print_exc()
            
    def _mouseMove(self,event) :
        try:
            self.__mouseX,self.__mouseY = event.x(),event.y()
            for drawingEventRef in self.__pendingEvents[:] :
                if(drawingEventRef().mouseMove(event.x(),event.y())) :
                    self._rmDrawingEventRef(drawingEventRef)

            if(self.__curentModifierMgr is not None and
               event.state() == (qt.Qt.LeftButton + qt.Qt.ShiftButton)) :
                self.__curentModifierMgr.modify(event.x(),event.y())
            elif event.state() == qt.Qt.ShiftButton : # FIND MOVE CLASS
                self.__checkObjectModify(event.x(),event.y())
            else :
                if self.__curentModifierMgr is not None :
                    self.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                    self.__curentModifierMgr = None

        except:
            import traceback
            traceback.print_exc()
            
    def _mouseRelease(self,event) :
        try:
            if event.state() & qt.Qt.LeftButton :
                if self.__curentModifierMgr is not None :
                    self.__curentModifierMgr.modify(event.x(),event.y())
                else :
                    for drawingEventRef in self.__pendingEvents[:] :
                        if(drawingEventRef().mouseReleased(event.x(),event.y())) :
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
                
    def _keyPressed(self,keyevent) :
        if keyevent.key() == qt.Qt.Key_Shift :
            self.__checkObjectModify(self.__mouseX,self.__mouseY)

    def _keyReleased(self,keyevent) :
        if keyevent.key() == qt.Qt.Key_Shift :
            if self.__curentModifierMgr is not None :
                self.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                self.__curentModifierMgr = None
                

    def _leaveEvent(self,event) :
         if self.__curentModifierMgr is not None :
                self.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                self.__curentModifierMgr = None
        
    def _rmDrawingEventRef(self,aDrawingEventRef) :
        try:
            self.__pendingEvents.remove(aDrawingEventRef)
        except:
            for eRef,excludList in self.__excludedEvent :
                if aDrawingEventRef in excludList :
                    excludList.remove(aDrawingEventRef)
        try:
            self.__checkExcludedEventsBeforeRemove(aDrawingEventRef)
            aDrawingEventRef().endPolling()
        except:
            pass
        
    def __weakRefEventRemove(self,eventRef) :
        try :
            self.__pendingEvents.remove(eventRef)
            self.__checkExcludedEventsBeforeRemove(eventRef)
        except:
            pass

    def __weakRefDrawingMgrRemove(self,mgrRef) :
        try:
            self.__drawingMgr.remove(mgrRef)
        except:
           pass

    def __checkExcludedEventsBeforeRemove(self,eventRef) :
        for eRef,excludedList in self.__excludedEvent[:] :
            if eRef() == eventRef() :
                tmpPendingList = self.__pendingEvents[:]
                self.__pendingEvents = excludedList
                for e in tmpPendingList :
                    self.addDrawingEvent(e())
                self.__pendingEvents = [x for x in itertools.ifilter(lambda x : x() is not None,self.__pendingEvents)]
                for i in range(len(tmpPendingList),len(self.__pendingEvents)) :
                    self.__pendingEvents[i]().setDubMode(False)
                self.__excludedEvent.remove((eRef,excludedList))
                break

    def __checkObjectModify(self,x,y) :
        findFlag = False
        for drawingMgr in self.__drawingMgr :
            modifyClass = drawingMgr().getModifyClass(x,y)
            if modifyClass is not None :
                self.__curentModifierMgr = modifyClass
                findFlag = True
                break
        if not findFlag :
            self.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
            self.__curentModifierMgr = None
            

