import qt
import weakref
import itertools

class QubEventMgr:
    def __init__(self) :
	self.__pendingEvents = []
        self.__excludedEvent = []
	self.__drawingMgr = []
        self.__eventLinkMgrs = []
        self.__mouseX,self.__mouseY = 0,0
        self.__curentModifierMgr = None
        self.__scrollView = None
  
    def addDrawingMgr(self,aDrawingMgr) :
        try:
            self.__drawingMgr.append(weakref.ref(aDrawingMgr,self.__weakRefDrawingMgrRemove))
            aDrawingMgr.setEventMgr(self)
            for link in self.__eventLinkMgrs :
                aDrawingMgr.addLinkEventMgr(link)
        except:
            import traceback
            traceback.print_exc()
            
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
            
    def addEventMgrLink(self,anEventMgr,
                        srcCanvas,desCanvas,
                        srcMatrix,destMatrix) :
        """ this methode link several event manager together,
        thanks to that, each draw may be seen on every view
        """
        linkEventMgr = _linkEventMgr(self,anEventMgr,
                                     srcCanvas,desCanvas,
                                     srcMatrix,destMatrix)
        self.addLinkEventMgr(linkEventMgr)
        anEventMgr.addLinkEventMgr(linkEventMgr)
        for drawingMgr in self.__drawingMgr :
            drawingMgr().addLinkEventMgr(linkEventMgr)
            
    def rmEventMgrLink(self,anEventMgr) :
        """ this methode unlink event manager
        """
        linkfind = None
        for link in self.__eventLinkMgrs :
            mgr1,mgr2 = link.getMgrs()
            if mgr1 == self or mgr2 == self :
                mgr1.rmLinkEventMgr(link)
                mgr2.rmLinkEventMgr(link)
                break
    def scrollView(self) :
        return self.__scrollView
    
    def _setScrollView(self,aScrollView) :
        self.__scrollView = aScrollView
        
    def _mousePressed(self,event,evtMgr = None) :
        try:
            if event.button() == qt.Qt.LeftButton and event.state() == qt.Qt.ShiftButton :
                if self.__curentModifierMgr is not None :
                    self.__curentModifierMgr.mousePressed(event.x(),event.y())
            elif event.button() == qt.Qt.LeftButton :
                for drawingEventRef in self.__pendingEvents[:] :
                    if(drawingEventRef().mousePressed(event.x(),event.y())) :
                        self._rmDrawingEventRef(drawingEventRef)

            if evtMgr is None:          # event propagate
                for link in self.__eventLinkMgrs :
                    link.mousePressed(event,self)

        except:
            import traceback
            traceback.print_exc()
            
    def _mouseMove(self,event,evtMgr = None) :
        try:
            self.__mouseX,self.__mouseY = event.x(),event.y()
            for drawingEventRef in self.__pendingEvents[:] :
                if(drawingEventRef().mouseMove(event.x(),event.y())) :
                    self._rmDrawingEventRef(drawingEventRef)

            if(self.__curentModifierMgr is not None and
               event.state() == (qt.Qt.LeftButton + qt.Qt.ShiftButton)) :
                self.__curentModifierMgr.mouseMovePressed(event.x(),event.y())
            elif event.state() == qt.Qt.ShiftButton : # FIND MOVE CLASS
                self.__checkObjectModify(event.x(),event.y(),evtMgr)
            else :
                if self.__curentModifierMgr is not None :
                    if evtMgr is not None :
                        evtMgr.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                    else:
                        self.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                    self.__curentModifierMgr = None

            if evtMgr is None:          # event propagate
                for link in self.__eventLinkMgrs :
                    link.mouseMove(event,self)
        except:
            import traceback
            traceback.print_exc()
            
    def _mouseRelease(self,event,evtMgr = None) :
        try:
            if event.state() & qt.Qt.LeftButton :
                if self.__curentModifierMgr is not None :
                    self.__curentModifierMgr.mouseReleased(event.x(),event.y())
                else :
                    for drawingEventRef in self.__pendingEvents[:] :
                        if(drawingEventRef().mouseReleased(event.x(),event.y())) :
                            self._rmDrawingEventRef(drawingEventRef)
            if evtMgr is None:          # event propagate
                for link in self.__eventLinkMgrs :
                    link.mouseReleased(event,self)
        except:
            import traceback
            traceback.print_exc()

    def _update(self,evtMgr = None) :
        for drawingMgr in self.__drawingMgr :
            try:
                drawingMgr().update()
            except:
                import traceback
                traceback.print_exc()
        if evtMgr is None :             # event propagate
            for link in self.__eventLinkMgrs :
                link.update(self)
                
    def _keyPressed(self,keyevent,evtMgr = None) :
        if keyevent.key() == qt.Qt.Key_Shift :
            self.__checkObjectModify(self.__mouseX,self.__mouseY,evtMgr)
        if evtMgr is None:          # event propagate
            for link in self.__eventLinkMgrs :
                link.keyPressed(keyevent,self)
                
    def _keyReleased(self,keyevent,evtMgr = None) :
        if keyevent.key() == qt.Qt.Key_Shift :
            if self.__curentModifierMgr is not None :
                if evtMgr is not None :
                    evtMgr.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                else:
                    self.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                self.__curentModifierMgr = None
        if evtMgr is None:          # event propagate
            for link in self.__eventLinkMgrs :
                link.keyReleased(keyevent,self)
                

    def _leaveEvent(self,event,evtMgr = None) :
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

    def __checkObjectModify(self,x,y,anEventMgr) :
        BBoxNmodifyClass = []
        for drawingMgr in self.__drawingMgr :
            modifyClass = drawingMgr().getModifyClass(x,y)
            if modifyClass is not None :
                boundingRect = drawingMgr().boundingRect()
                BBoxNmodifyClass.append((boundingRect,modifyClass))

        BBoxNmodifyClass.sort(lambda v1,v2 : v1[0].width() * v1[0].height() - v2[0].width() * v2[0].height())
        if not BBoxNmodifyClass :
            if anEventMgr is None : anEventMgr = self
            if self.__curentModifierMgr is not None :
                anEventMgr.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
                self.__curentModifierMgr = None
        else:
            self.__curentModifierMgr = BBoxNmodifyClass[0][1]
            if anEventMgr is None : anEventMgr = self
            self.__curentModifierMgr.setCursor(anEventMgr)
            
            

    def addLinkEventMgr(self,linkEventMgr) :
        """ Do not call this methode directly
        """
        self.__eventLinkMgrs.append(linkEventMgr)

    def getEventMethodes(self) :
        return [self._mousePressed,self._mouseMove,self._mouseRelease,
                self._update,self._keyPressed,self._keyReleased,self._leaveEvent]
                   ####### Link event class #######

class _linkEventMgr :
    MOUSE_PRESSED,MOUSE_MOVE,MOUSE_RELEASE,UPDATE,KEY_PRESSED,KEY_RELEASED,LEAVE_EVENT = range(7)

    def __init__(self,evMgr1,evMgr2,
                 canvas1,canvas2,
                 matrix1,matrix2) :
        self.__evtMgrs = [(evMgr1,evMgr1.getEventMethodes()),
                          (evMgr2,evMgr2.getEventMethodes())]
        self.__canvas = [canvas1,canvas2]
        self.__matrix = [matrix1,matrix2]
        
    def mousePressed(self,event,evtMgr) :
        self._mouseEvent(event,evtMgr,_linkEventMgr.MOUSE_PRESSED)
        
    def mouseMove(self,event,evtMgr) :
        self._mouseEvent(event,evtMgr,_linkEventMgr.MOUSE_MOVE)
        
    def mouseReleased(self,event,evtMgr) :
        self._mouseEvent(event,evtMgr,_linkEventMgr.MOUSE_RELEASE)

    def update(self,evtMgr) :
        mgrNMeth = self.__evtMgrs[0]
        if mgrNMeth[0] == evtMgr :
            mgrNMeth = self.__evtMgrs[1]
        mgrNMeth[1][_linkEventMgr.UPDATE](evtMgr)
        
    def keyPressed(self,event,evtMgr) :
        self._simpleEvent(event,evtMgr,_linkEventMgr.KEY_PRESSED)
        
    def keyReleased(self,event,evtMgr) :
        self._simpleEvent(event,evtMgr,_linkEventMgr.KEY_RELEASED)
        
    def leaveEvent(self,event,evtMgr) :
        self._simpleEvent(event,evtMgr,_linkEventMgr.LEAVE_EVENT)
    
    def _simpleEvent(self,event,evtMgr,aType) :
        mgrNMeth = self.__evtMgrs[0]
        if mgrNMeth[0] == evtMgr :
            mgrNMeth = self.__evtMgrs[1]
        mgrNMeth[1][aType](event,evtMgr)
        
    def _mouseEvent(self,event,evtMgr,aType) :
        matrix2,matrix1 = self.__matrix
        mgrNMeth = self.__evtMgrs[0]
        if mgrNMeth[0] == evtMgr :
            matrix1,matrix2 = matrix2,matrix1
            mgrNMeth = self.__evtMgrs[1]

        x,y = event.pos().x(),event.pos().y()
        if matrix1 is not None :
            x,y = matrix1.invert()[0].map(x,y)
        if matrix2 is not None :
            x,y = matrix2.map(x,y)
        newEvent = qt.QMouseEvent(event.type(),qt.QPoint(x,y),event.button(),event.state())
        mgrNMeth[1][aType](newEvent,evtMgr)

    def getMgrs(self) :
        return self.__evtMgrs[0][0],self.__evtMgrs[1][0]

    def getOtherMgr(self,eventMgr) :
        if eventMgr == self.__evtMgrs[0][0] :
            return self.__evtMgrs[1][0]
        else :
            return self.__evtMgrs[0][0]
        
    def getCanvasNMatrix(self,evtMgr) :
        matrix1,matrix2 = self.__matrix
        canvas1,canvas2 = self.__canvas
        if evtMgr == self.__evtMgrs[0][0] :
            matrix1,matrix2 = matrix2,matrix1
            canvas1,canvas2 = canvas2,canvas1
        return (canvas1,matrix1)
