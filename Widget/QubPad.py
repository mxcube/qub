import sys
import qt

from Qub.Icons import QubIcons

class QubPad(qt.QWidget):
    """
    This class inherits QWidget and manage a 2 or 1 axis Pad.

    To Use this class make a plug which inherits from QubPadPlug, and plug it to this widget
    """
    def __init__(self,parent = None,name = None,fl = 0):
        qt.QWidget.__init__(self,parent,name,fl)

        self.__multiplyInUse = 1
        self.__multiplyfactor = 10
        
        padLayout = qt.QVBoxLayout(self,11,6,"padLayout")

        layout2 = qt.QHBoxLayout(None,0,6,"layout2")

        self.__hAxis = qt.QLabel(self,"__hAxis")
        layout2.addWidget(self.__hAxis)
        spacer1 = qt.QSpacerItem(40,20,qt.QSizePolicy.Expanding,qt.QSizePolicy.Minimum)
        layout2.addItem(spacer1)
        self.__hStepCombo = _combo_box(True,self,"__hStepCombobox")
        self.__hStepCombo.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.MinimumExpanding,qt.QSizePolicy.Fixed,0,0,
                                                    self.__hStepCombo.sizePolicy().hasHeightForWidth()))
        self.__hStepCombo.setAutoCompletion(1)
        self.__hStepCombo.setDuplicatesEnabled(0)
        layout2.addWidget(self.__hStepCombo)
        
        self.__hMultiplyText = qt.QLabel(self,"__hMultiplyText")
        layout2.addWidget(self.__hMultiplyText)
        padLayout.addLayout(layout2)
        
        self.__vAxis = qt.QLabel(self,"__vAxis")
 
        self.__padButton = _pad_button(self.__hAxis,self.__vAxis,self,"__padButton")
        self.__padButton.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.MinimumExpanding,qt.QSizePolicy.MinimumExpanding,
                                                      0,0,self.__padButton.sizePolicy().hasHeightForWidth()))
        self.__padButton.setFlat(1)
        padLayout.addWidget(self.__padButton)

        layout1 = qt.QHBoxLayout(None,0,6,"layout1")

        layout1.addWidget(self.__vAxis)
        spacer2 = qt.QSpacerItem(40,20,qt.QSizePolicy.Expanding,qt.QSizePolicy.Minimum)
        layout1.addItem(spacer2)
        self.__vStepCombo = _combo_box(True,self,"__vStepCombo")
        self.__vStepCombo.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.MinimumExpanding,qt.QSizePolicy.Fixed,0,0,
                                                    self.__vStepCombo.sizePolicy().hasHeightForWidth()))
        self.__vStepCombo.setAutoCompletion(1)
        self.__vStepCombo.setDuplicatesEnabled(0)
        layout1.addWidget(self.__vStepCombo)

        self.__vMultiplyText = qt.QLabel(self,"__vMultiplyText")
        layout1.addWidget(self.__vMultiplyText)
        padLayout.addLayout(layout1)

        self.languageChange()

        self.clearWState(qt.Qt.WState_Polished)


        self.__hName,self.__hFormat,self.__hPos = ('H','%f',0.)
        self.__vName,self.__vFormat,self.__vPos = ('V','%f',0.)
        self.__refreshVLabel()
        self.__refreshHLabel()
        
    def languageChange(self):
        self.setCaption(self.__tr("Pad"))
        self.__padButton.setText(qt.QString.null)

    def setMultiplyStep(self,aFlag) :
        if(aFlag) :
            self.__multiplyInUse = self.__multiplyfactor
            self.__hMultiplyText.setText(' x %d' % self.__multiplyInUse)
            self.__vMultiplyText.setText(' x %d' % self.__multiplyInUse)
        else :
            self.__multiplyInUse = 1
            self.__hMultiplyText.setText('')
            self.__vMultiplyText.setText('')


    def __tr(self,s,c = None):
        return qt.qApp.translate("pad",s,c)

    def setHAxisName(self,name) :
        """
        Horizontal Motor's name
        """
        self.__hName = name
        self.__refreshHLabel()
    def setHFormat(self,format) :
        """
        Horizontal Motor's position format
        """
        self.__hFormat = format
    def setHPos(self,pos) :
        """
        Horizontal Motor's position
        """
        self.__hPos = pos
    def __refreshHLabel(self) :
        format = '%s : ' + self.__hFormat
        self.__hAxis.setText(format % (self.__hName,self.__hPos))

    def setVAxisName(self,name) :
        """
        Vertical Motor's name
        """
        self.__vName = name
        self.__refreshVLabel()
    def setVFormat(self,format) :
        """
        Vertical Motor's position format
        """
        self.__vFormat = format
        self.__refreshVLabel()
    def setVPos(self,pos) :
        """
        Vertical Motor's position
        """
        self.__vPos = pos
        self.__refreshVLabel()
    def __refreshVLabel(self) :
        format = '%s : ' + self.__vFormat
        self.__vAxis.setText(format % (self.__vName,self.__vPos))


    def setPlug(self,aPadPlug) :
        """
        Connect the plug callback
        """
        self.__padButton.setPlug(aPadPlug)

    def setMultiplyFactor(self,factor) :
        """
        Change the fast move factor
        """
        self.__multiplyfactor = int(factor)
    
    def getHStep(self) :
        hStep,hValid = self.__hStepCombo.currentText().toFloat()
        return self.__multiplyInUse * hStep

    def getVStep(self) :
        vStep,hValid = self.__vStepCombo.currentText().toFloat()
        return self.__multiplyInUse * vStep

    
class QubPadPlug :
    def __init__(self) :
        self._padButton = None

    def stopVertical(self) :
        print "Should redefine Vertical Stop"
    def stopHorizontal(self) :
        print "Should redefine Horizontal Stop"
    def up(self,step) :
        print "Should move %f step up" % step
    def down(self,step) :
        print "Should move %f step down" % step
    def left(self,step) :
        print "Should move %f step left" % step
    def right(self,step) :
        print "Should move %f step right" % step

    def setPad(self,aPad) :
        self._padButton = aPad


                   ####### Motor Move State #######
class _MoveMotorState :
    def __init__(self,manager) :
        self._mgr = manager
        manager.moveState = self
    def move(self) :
        pass
    def endMove(self) :
        pass
    def setYourStateOnImage(self,image) :
        pass
    
class _Stop(_MoveMotorState) :
     def __init__(self,manager) :
         _MoveMotorState.__init__(self,manager)
     def move(self) :
         self._mgr.needRebuildImage = True
         _OneMove(self._mgr)
     def setYourStateOnImage(self,image) :
         self._mgr.setGrayOn(image,self._mgr.STOP)
     
class _OneMove(_MoveMotorState) :
     def __init__(self,manager) :
         _MoveMotorState.__init__(self,manager)
     def move(self) :
         _BothMove(self._mgr)
     def endMove(self) :
         self._mgr.needRebuildImage = True
         _Stop(self._mgr)

class _BothMove(_MoveMotorState) :
     def __init__(self,manager) :
         _MoveMotorState.__init__(self,manager)
     def endMove(self) :
         _OneMove(self._mgr)


                ####### State Horizontal Motor #######

class _hMotorState :
    def __init__(self,manager,plug) :
        self._mgr = manager
        manager.hstate = self
        self._plug = plug

    def setPlug(self,aPadPlug) :
        if(isinstance(aPadPlug,QubPadPlug)) :
            self._plug = aPadPlug
            aPadPlug.setPad(self._mgr)
        else :
            raise StandardError('Must be a PadPlug')

    def connect(self) :
        self._mgr.needRebuildImage = True
        _hConnected(self._mgr,self._plug)

    def disconnect(self) :
        self._mgr.needRebuildImage = True
        _hNConnected(self._mgr,self._plug)

    def error(self) :
        self._mgr.needRebuildImage = True
        _hError(self._mgr,self._plug)
    
    def move_left(self) :
        pass
    def move_right(self) :
        pass
    def end_move(self,aCbkFlag = False) :
        pass
    
    def setYourStateOnImage(self,image) :
        pass

    def setBackgroundLabel(self,label) :
        bck_color = self._mgr.paletteBackgroundColor() 
        label.setPaletteBackgroundColor(bck_color)
   
class _hError(_hMotorState) :
    def __init__(self,manager,plug) :
        _hMotorState.__init__(self,manager,plug)
    def error(self) :
        pass
    def setYourStateOnImage(self,image) :
        self._mgr.setRedOn(image,self._mgr.LEFT)
        self._mgr.setRedOn(image,self._mgr.RIGHT)

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('red'))
        
class _hNConnected(_hMotorState) :
    def __init__(self,manager,plug) :
        _hMotorState.__init__(self,manager,plug)
        
    def setYourStateOnImage(self,image) :
        self._mgr.setGrayOn(image,self._mgr.LEFT)
        self._mgr.setGrayOn(image,self._mgr.RIGHT)


class _hConnected(_hMotorState) :
    def __init__(self,manager,plug) :
        _hMotorState.__init__(self,manager,plug)
    def connect(self) :
        pass
    def move_left(self) :
        self._mgr.needRebuildImage = True
        _hMoveLeft(self._mgr,self._plug)
    def move_right(self) :
        self._mgr.needRebuildImage = True
        _hMoveRight(self._mgr,self._plug)
    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('green'))
        
class _hMoveLeft(_hMotorState) :
    def __init__(self,manager,plug) :
        _hMotorState.__init__(self,manager,plug)
        self.move_left()
        self._mgr.moveState.move()

    def __del__(self) :
        self._mgr.moveState.endMove()

    def move_left(self) :
        if(self._plug) :
            self._plug.left(self._mgr.getHStep())
    def end_move(self,aCbkFlag = False) :
        _hConnected(self._mgr,self._plug)
        if(aCbkFlag and self._plug) :
            self._plug.stopHorizontal()

    def setYourStateOnImage(self,image) :
        self._mgr.setYellowOn(image,self._mgr.LEFT)
        self._mgr.setGrayOn(image,self._mgr.RIGHT)

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('yellow'))

class _hMoveRight(_hMotorState) :
    def __init__(self,manager,plug) :
        _hMotorState.__init__(self,manager,plug)
        self.move_right()
        self._mgr.moveState.move()

    def __del__(self) :
        self._mgr.moveState.endMove()

    def move_right(self) :
        if(self._plug) :
            self._plug.right(self._mgr.getHStep())

    def end_move(self,aCbkFlag = False) :
        _hConnected(self._mgr,self._plug)
        if(aCbkFlag and self._plug) :
            self._plug.stopHorizontal()
        
    def setYourStateOnImage(self,image) :
        self._mgr.setYellowOn(image,self._mgr.RIGHT)
        self._mgr.setGrayOn(image,self._mgr.LEFT)

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('yellow'))

                 ####### State Vertical Motot #######
class _vMotorState :
    def __init__(self,manager,plug) :
        self._mgr = manager
        self._plug = plug
        manager.vstate = self

    def setPlug(self,aPadPlug) :
        if(isinstance(aPadPlug,QubPadPlug)) :
            self._plug = aPadPlug
            aPadPlug.setPad(self._mgr)
        else :
            raise StandardError('Must be a PadPlug')

    def connect(self) :
        self._mgr.needRebuildImage = True
        _vConnected(self._mgr,self._plug)

    def disconnect(self) :
        self._mgr.needRebuildImage = True
        _vNConnected(self._mgr,self._plug)

    def error(self) :
        self._mgr.needRebuildImage = True
        _vError(self._mgr,self._plug)
    
    def move_up(self) :
        pass
    def move_down(self) :
        pass
    def end_move(self,aCbkFlag = False) :
        pass
    
    def setYourStateOnImage(self,image) :
        pass

    def setBackgroundLabel(self,label) :
        bck_color = self._mgr.paletteBackgroundColor() 
        label.setPaletteBackgroundColor(bck_color)

class _vError(_vMotorState) :
    def __init__(self,manager,plug) :
        _vMotorState.__init__(self,manager,plug)
    def error(self) :
        pass
    def setYourStateOnImage(self,image) :
        self._mgr.setRedOn(image,self._mgr.UP)
        self._mgr.setRedOn(image,self._mgr.DOWN)

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('red'))

class _vNConnected(_vMotorState) :
    def __init__(self,manager,plug) :
        _vMotorState.__init__(self,manager,plug)
    def setYourStateOnImage(self,image) :
        self._mgr.setGrayOn(image,self._mgr.UP)
        self._mgr.setGrayOn(image,self._mgr.DOWN)

class _vConnected(_vMotorState) :
    def __init__(self,manager,plug) :
        _vMotorState.__init__(self,manager,plug)
    def connect(self) :
        pass
    def move_up(self) :
        self._mgr.needRebuildImage = True
        _vMoveUp(self._mgr,self._plug)
    def move_down(self) :
        self._mgr.needRebuildImage = True
        _vMoveDown(self._mgr,self._plug)
    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('green'))

class _vMoveUp(_vMotorState) :
    def __init__(self,manager,plug) :
        _vMotorState.__init__(self,manager,plug)
        self.move_up()
        self._mgr.moveState.move()
    def __del__(self) :
        self._mgr.moveState.endMove()
    
    def move_up(self) :
        if(self._plug) :
            self._plug.up(self._mgr.getVStep())

    def end_move(self,aCbkFlag = False) :
        self._mgr.needRebuildImage = True
        _vConnected(self._mgr,self._plug)
        if(aCbkFlag and self._plug) :
            self._plug.stopVertical()

    def setYourStateOnImage(self,image) :
        self._mgr.setYellowOn(image,self._mgr.UP)
        self._mgr.setGrayOn(image,self._mgr.DOWN)

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('yellow'))

class _vMoveDown(_vMotorState) :
    def __init__(self,manager,plug) :
        _vMotorState.__init__(self,manager,plug)
        self.move_down()
        self._mgr.moveState.move()
    def __del__(self) :
        self._mgr.moveState.endMove()
    def move_down(self) :
        if(self._plug) :
            self._plug.down(self._mgr.getVStep())

    def end_move(self,aCbkFlag = False) :
        self._mgr.needRebuildImage = True
        _vConnected(self._mgr,self._plug)
        if(aCbkFlag and self._plug) :
            self._plug.stopVertical()
        
    def setYourStateOnImage(self,image) :
        self._mgr.setYellowOn(image,self._mgr.DOWN)
        self._mgr.setGrayOn(image,self._mgr.UP)

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('yellow'))
        
class _drawIdle(qt.QTimer) :
    def __init__(self,button) :
        qt.QTimer.__init__(self)
        self.__pos = None
        self.__button = button
        self.__x = 0
        self.__y = 0
        self.connect(self,qt.SIGNAL('timeout()'),self.__idleDraw);
        
    def setPos(self,pos) :
        self.__x = pos.x()
        self.__y = pos.y()

    def __idleDraw(self) :
        self.__button.realDraw(self.__x,self.__y)
        self.stop()
        
class _pad_button(qt.QPushButton) :
    def __init__(self,hLabel,vLabel,parent,name) :
        qt.QPushButton.__init__(self,parent,name)
        self.__hLabel,self.__vLabel = hLabel,vLabel
        self.__pad = parent
        self.setMouseTracking(True)
        self.__multiplymode = False

        pad_path = QubIcons.getIconPath('pad.png')
        self.__image = qt.QImage(pad_path)
        self.__unhighlightImage(self.__image,0,0,self.__image.width(),self.__image.height())
        
        self.__idle = _drawIdle(self)

        
        self.UNDEF,self.UP,self.DOWN,self.LEFT,self.RIGHT,self.STOP = range(6)
        self.__under = self.UNDEF
        
        self.__tuple2ArrowType = {(0,1) : self.RIGHT,(2,1) : self.LEFT,
                                  (1,1) : self.STOP,
                                   (1,0) : self.UP, (1,2) : self.DOWN}
        self.__arrowType2tuple = {}
        for t,e in self.__tuple2ArrowType.iteritems() :
            self.__arrowType2tuple[e] = t
            
        self.__column_size = self.__image.width() / 3
        self.__line_size = self.__image.height() / 3

         
        self.__currentimg = None
        self.moveState = _Stop(self)
        self.hstate = _hNConnected(self,None)
        self.vstate = _vNConnected(self,None)
        self.needRebuildImage = True
        self.__rebuildImageIfNeeded()
        self.setPixmap(qt.QPixmap(self.__currentimg))
        self.connect(self,qt.SIGNAL("clicked()"),self.__moveMotor)

    def keyPressEvent(self,aKeyEvent) :
        if(aKeyEvent.key() == qt.Qt.Key_Shift) :
            aKeyEvent.accept()
            self.__multiplyStep(True)
        else :
            aKeyEvent.ignore()
                
    def keyReleaseEvent(self,aKeyEvent) :
         if(aKeyEvent.key() == qt.Qt.Key_Shift) :
            aKeyEvent.accept()
            self.__multiplyStep(False)
         else :
             aKeyEvent.ignore()
        
    def mouseMoveEvent(self,MouseEvent) :
        MouseEvent.accept()
        self.__idle.setPos(MouseEvent.pos())
        if not self.__idle.isActive() :
            self.__idle.start(0)
            
    def enterEvent(self,anEvent) :
        self.setFocus()
        
    def leaveEvent(self,anEvent) :
        self.__idle.setPos(qt.QPoint(-1,-1))
        if not self.__idle.isActive() :
            self.__idle.start(0)
        self.__multiplyStep(False)
        
    def __moveMotor(self):
        if(self.__under == self.STOP) :
            self.hstate.end_move(True)
            self.vstate.end_move(True)
        elif(self.__under == self.UP) :
            self.vstate.move_up()
        elif(self.__under == self.DOWN) :
            self.vstate.move_down()
        elif(self.__under == self.LEFT) :
            self.hstate.move_left()
        elif(self.__under == self.RIGHT) :
            self.hstate.move_right()

        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)

    def __rebuildImageIfNeeded(self) :
        if(self.needRebuildImage) :
            self.needRebuildImage = False
            tmpimg = self.__image.copy()
            self.moveState.setYourStateOnImage(tmpimg)
            self.hstate.setYourStateOnImage(tmpimg)
            self.vstate.setYourStateOnImage(tmpimg)
            self.__currentimg = tmpimg

            self.hstate.setBackgroundLabel(self.__hLabel)
            self.vstate.setBackgroundLabel(self.__vLabel)
    
    def realDraw(self,x,y) :
        self.__rebuildImageIfNeeded()
        image = self.__currentimg.copy()
        im_ox = (self.width() - image.width()) / 2
        im_oy = (self.height() - image.height()) / 2
        im_ex = im_ox + image.width()
        im_ey = im_oy + image.height()

        under = self.UNDEF
        if im_ox <= x <= im_ex and im_oy <= y <= im_ey :
            columid = (x - im_ox) / self.__column_size
            lineid = (y - im_oy) / self.__line_size
            under,onArrow = self.__getArrowAtColumNLine(columid,lineid)
            if onArrow :
                self.__highlightImage(image,*self.__getBBoxFromColumnNLine(columid,lineid))
        self.__under = under
        self.setPixmap(qt.QPixmap(image))

            
    def __getArrowAtColumNLine(self,columid,lineid) :
        onArraw = False
        state = self.UNDEF
        if(self.__tuple2ArrowType.has_key((columid,lineid))) :
            onArraw = True
            state = self.__tuple2ArrowType[(columid,lineid)]
        return (state,onArraw)

    def __getColumNLineFromTypeArrow(self,type_arrow) :
        columid = -1
        lineid = -1
        if(self.__arrowType2tuple.has_key(type_arrow)) :
            columid,lineid = self.__arrowType2tuple[type_arrow]
        return (columid,lineid)
    
    def __getBBoxFromColumnNLine(self,columid,lineid) :
        ox = columid * self.__column_size
        oy = lineid * self.__line_size
        ex = ox + self.__column_size
        ey = oy + self.__line_size
        return (ox,oy,ex,ey)

    def __setGray(self,image,ox,oy,ex,ey) :
        for y in xrange(oy,ey) :
            for x in xrange(ox,ex) :
                rgb = image.pixel(x,y)
                alpha = qt.qAlpha(rgb)
                if(alpha) :
                    gray = qt.qGreen(rgb)
                    red = qt.qRed(rgb)
                    if(red > gray) :
                        gray = red
                    image.setPixel(x,y,qt.qRgba(gray,gray,gray,alpha))
                        
    def __setRed(self,image,ox,oy,ex,ey) :
        for y in xrange(oy,ey) :
            for x in xrange(ox,ex) :
                rgb = image.pixel(x,y)
                alpha = qt.qAlpha(rgb)
                if(alpha) :
                    image.setPixel(x,y,qt.qRgba(qt.qGreen(rgb),qt.qRed(rgb),qt.qBlue(rgb),alpha))

    def __setYellow(self,image,ox,oy,ex,ey) :
        for y in xrange(oy,ey) :
            for x in xrange(ox,ex) :
                rgb = image.pixel(x,y)
                alpha = qt.qAlpha(rgb)
                if(alpha) :
                    green = qt.qGreen(rgb)
                    image.setPixel(x,y,qt.qRgba(green,green,qt.qBlue(rgb),alpha))

    def __highlightImage(self,image,ox,oy,ex,ey) :
        for y in xrange(oy,ey) :
            for x in xrange(ox,ex) :
                rgb = image.pixel(x,y)
                alpha = qt.qAlpha(rgb)
                if(alpha) :
                    red,green,blue = qt.qRed(rgb) * 1.25,qt.qGreen(rgb) * 1.25,qt.qBlue(rgb) * 1.25
                    image.setPixel(x,y,qt.qRgba(red,green,blue,alpha))
                    
    def __unhighlightImage(self,image,ox,oy,ex,ey) :
        for y in xrange(oy,ey) :
            for x in xrange(ox,ex) :
                rgb = image.pixel(x,y)
                alpha = qt.qAlpha(rgb)
                if(alpha) :
                    red,green,blue = qt.qRed(rgb) * 0.8,qt.qGreen(rgb) * 0.8,qt.qBlue(rgb) * 0.8
                    image.setPixel(x,y,qt.qRgba(red,green,blue,alpha))
                    
    def __multiplyStep(self,aFlag) :
        if(self.__multiplymode != aFlag) :
            self.__multiplymode = aFlag
            self.__pad.setMultiplyStep(self.__multiplymode)

    def getHStep(self) :
        return self.__pad.getHStep()

    def getVStep(self) :
        return self.__pad.getVStep()
    
    def setGrayOn(self,image,type_arrow) :
        columid,lineid = self.__getColumNLineFromTypeArrow(type_arrow)
        self.__setGray(image,*self.__getBBoxFromColumnNLine(columid,lineid))

    def setRedOn(self,image,type_arrow) :
        columid,lineid = self.__getColumNLineFromTypeArrow(type_arrow)
        self.__setRed(image,*self.__getBBoxFromColumnNLine(columid,lineid))

    def setYellowOn(self,image,type_arrow) :
        columid,lineid = self.__getColumNLineFromTypeArrow(type_arrow)
        self.__setYellow(image,*self.__getBBoxFromColumnNLine(columid,lineid))

    def setPlug(self,aPadPlug) :
        self.hstate.setPlug(aPadPlug)
        self.vstate.setPlug(aPadPlug)
        
    def endHMotorMoving(self) :
        self.hstate.end_move()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)

    def endVMotorMoving(self) :
        self.vstate.end_move()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)

    def hMotorConnected(self) :
        self.hstate.connect()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)

    def vMotorConnected(self) :
        self.vstate.connect()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)

    def hMotorError(self) :
        self.hstate.error()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)

    def vMotorError(self) :
        self.vstate.error()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)
        
class _combo_box(qt.QComboBox) :
    def __init__(self,rw,parent,name) :
        qt.QComboBox.__init__(self,rw,parent,name)
        self.connect(self,qt.SIGNAL("activated(int)"),self.__changeValue)
        self.__errorDisplay = False
    def leaveEvent(self,anEvent) :
        text = self.currentText()
        if not text.isEmpty() :
            if not self.__checkFloatValue(text) :
                self.setCurrentText('')

    def __checkFloatValue(self,text) :
        float,valid = text.toFloat()
        if not valid and not self.__errorDisplay :
            self.__errorDisplay = True
            errorMessage = qt.QErrorMessage(self,'float invalide')
            errorMessage.message('Values must be float')
            errorMessage.exec_loop()
            
            self.__errorDisplay = False
        return valid
    
    def __changeValue(self,index) :
        text = self.text(index)
        if not self.__checkFloatValue(text) :
            self.removeItem(index)


                      ####### MAIN TEST #######
      
class _myTestPlug(QubPadPlug) :
    def __init__(self) :
        QubPadPlug.__init__(self)

        self.timer1 =  qt.QTimer()
        qt.QObject.connect(self.timer1,qt.SIGNAL('timeout()'),self.hMotorConnected)
        self.timer1.start(10000,True)

        self.timer2 =  qt.QTimer()
        qt.QObject.connect(self.timer2,qt.SIGNAL('timeout()'),self.vMotorConnected)
        self.timer2.start(5000,True)

        self.timer3 = qt.QTimer()
        qt.QObject.connect(self.timer3,qt.SIGNAL('timeout()'),self.hMotorError)
        self.timer3.start(30000,True)

        self.timer4 = qt.QTimer()
        qt.QObject.connect(self.timer4,qt.SIGNAL('timeout()'),self.vMotorError)
        self.timer4.start(100000,True)

    def hMotorConnected(self) :
        print "Horizontal Motor Connected"
        self._padButton.hMotorConnected()
    def vMotorConnected(self) :
        print "Vertical Motor Connected"
        self._padButton.vMotorConnected()

    def hMotorError(self) :
        print "Horizontal Motor Error"
        self._padButton.hMotorError()

    def vMotorError(self) :
        print "Vertical Motor Error"
        self._padButton.vMotorError()


    def stopVertical(self) :
        print "Vertical Stop"
    def stopHorizontal(self) :
        print "Horizontal Stop"

    def up(self,step) :
        print "Move %f step up" % step
        self.vtimer = qt.QTimer()
        qt.QObject.connect(self.vtimer,qt.SIGNAL('timeout()'),self._padButton.endVMotorMoving)
        self.vtimer.start(2000,True)
        
    def down(self,step) :
        print "Move %f step down" % step
        self.vtimer = qt.QTimer()
        qt.QObject.connect(self.vtimer,qt.SIGNAL('timeout()'),self._padButton.endVMotorMoving)
        self.vtimer.start(2000,True)

    def left(self,step) :
        print "Move %f step left" % step
        self.ltimer = qt.QTimer()
        qt.QObject.connect(self.ltimer,qt.SIGNAL('timeout()'),self._padButton.endHMotorMoving)
        self.ltimer.start(3000,True)

    def right(self,step) :
        print "Move %f step right" % step
        self.ltimer = qt.QTimer()
        qt.QObject.connect(self.ltimer,qt.SIGNAL('timeout()'),self._padButton.endHMotorMoving)
        self.ltimer.start(3000,True)

if __name__ == "__main__":
    a = qt.QApplication(sys.argv)
    qt.QObject.connect(a,qt.SIGNAL("lastWindowClosed()"),a,qt.SLOT("quit()"))
    w = QubPad()
    plug = _myTestPlug()
    w.setPlug(plug)
    
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
