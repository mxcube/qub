import sys
import qt

from Qub.Icons import QubIcons

class QubPad(qt.QWidget):
    HORIZONTAL_AXIS,VERTICAL_AXIS,ROTATION_AXIS = (1 << 0,1 << 1,1 << 2)
    """
    This class inherits QWidget and manage a 3,2 or 1 axis Pad.

    To Use this class make a plug which inherits from QubPadPlug, and plug it to this widget
    """
    def __init__(self,parent = None,name = None,fl = 0):
        qt.QWidget.__init__(self,parent,name,fl)

        self.__multiplyInUse = 1
        self.__multiplyfactor = 10
        
        padLayout = qt.QVBoxLayout(self,5,0,"padLayout")

                      ####### HORIZONTAL #######
        self.__hFrame = qt.QFrame(self,"__hFrame")
        self.__hFrame.setFrameShape(qt.QFrame.GroupBoxPanel)
        self.__hFrame.setFrameShadow(qt.QFrame.Raised)
        hlayout = qt.QHBoxLayout(self.__hFrame,2,0,"hlayout")
        
        self.__hIcon = qt.QLabel(self.__hFrame,"__hIcon")
        self.__hIcon.setPixmap(qt.QPixmap(QubIcons.getIconPath('horizontal.png')))
        hlayout.addWidget(self.__hIcon)

        self.__hAxisName = qt.QLabel(self.__hFrame,"__hAxisName")
        hlayout.addWidget(self.__hAxisName)
        self.__hAxisPos = qt.QLabel(self.__hFrame,"__hAxisPos")
        hlayout.addWidget(self.__hAxisPos)
        self.__hSpacer = qt.QSpacerItem(40,20,qt.QSizePolicy.Expanding,qt.QSizePolicy.Minimum)
        hlayout.addItem(self.__hSpacer)
        self.__hUndo = qt.QPushButton(self.__hFrame)
        self.__hUndo.setPixmap(qt.QPixmap(QubIcons.getIconPath('undo.png')))
        hlayout.addWidget(self.__hUndo)
        self.__hRedo = qt.QPushButton(self.__hFrame)
        self.__hRedo.setPixmap(qt.QPixmap(QubIcons.getIconPath('redo.png')))
        hlayout.addWidget(self.__hRedo)
        self.__hStepCombo = _combo_box(True,self.__hFrame,"__hStepCombobox")
        self.__hStepCombo.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.MinimumExpanding,qt.QSizePolicy.Fixed,0,0,
                                                    self.__hStepCombo.sizePolicy().hasHeightForWidth()))
        self.__hStepCombo.setAutoCompletion(1)
        self.__hStepCombo.setDuplicatesEnabled(0)
        hlayout.addWidget(self.__hStepCombo)
        
        self.__hMultiplyText = qt.QLabel(self.__hFrame,"__hMultiplyText")
        hlayout.addWidget(self.__hMultiplyText)

        padLayout.addWidget(self.__hFrame)
        
                       ####### VERTICAL #######
        self.__vFrame = qt.QFrame(self,"__vFrame")
        self.__vFrame.setFrameShape(qt.QFrame.GroupBoxPanel)
        self.__vFrame.setFrameShadow(qt.QFrame.Raised)
        vlayout = qt.QHBoxLayout(self.__vFrame,2,0,"vlayout")

        self.__vIcon = qt.QLabel(self.__vFrame,"__vIcon")
        self.__vIcon.setPixmap(qt.QPixmap(QubIcons.getIconPath('vertical.png')))
        vlayout.addWidget(self.__vIcon)

        self.__vAxisName = qt.QLabel(self.__vFrame,"__vAxisName")
        vlayout.addWidget(self.__vAxisName)
        self.__vAxisPos = qt.QLabel(self.__vFrame,"__vAxisPos")
        vlayout.addWidget(self.__vAxisPos)
        self.__vSpacer = qt.QSpacerItem(40,20,qt.QSizePolicy.Expanding,qt.QSizePolicy.Minimum)
        vlayout.addItem(self.__vSpacer)
        self.__vUndo = qt.QPushButton(self.__vFrame)
        self.__vUndo.setPixmap(qt.QPixmap(QubIcons.getIconPath('undo.png')))
        vlayout.addWidget(self.__vUndo)
        self.__vRedo = qt.QPushButton(self.__vFrame)
        self.__vRedo.setPixmap(qt.QPixmap(QubIcons.getIconPath('redo.png')))
        vlayout.addWidget(self.__vRedo)
        self.__vStepCombo = _combo_box(True,self.__vFrame,"__vStepCombo")
        self.__vStepCombo.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.MinimumExpanding,qt.QSizePolicy.Fixed,0,0,
                                                    self.__vStepCombo.sizePolicy().hasHeightForWidth()))
        self.__vStepCombo.setAutoCompletion(1)
        self.__vStepCombo.setDuplicatesEnabled(0)
        vlayout.addWidget(self.__vStepCombo)

        self.__vMultiplyText = qt.QLabel(self.__vFrame,"__vMultiplyText")
        vlayout.addWidget(self.__vMultiplyText)

        padLayout.addWidget(self.__vFrame)
                       ####### ROTATION #######
        self.__rFrame = qt.QFrame(self,"__rFrame")
        self.__rFrame.setFrameShape(qt.QFrame.GroupBoxPanel)
        self.__rFrame.setFrameShadow(qt.QFrame.Raised)
        rlayout = qt.QHBoxLayout(self.__rFrame,2,0,"rlayout")

        self.__rIcon = qt.QLabel(self.__rFrame,"__rIcon")
        self.__rIcon.setPixmap(qt.QPixmap(QubIcons.getIconPath('rotation.png')))
        rlayout.addWidget(self.__rIcon)
        
        self.__rAxisName = qt.QLabel(self.__rFrame,"__rAxisName")
        rlayout.addWidget(self.__rAxisName)
        self.__rAxisPos = qt.QLabel(self.__rFrame,"__rAxisPos")
        rlayout.addWidget(self.__rAxisPos)
        self.__rSpacer = qt.QSpacerItem(40,20,qt.QSizePolicy.Expanding,qt.QSizePolicy.Minimum)
        rlayout.addItem(self.__rSpacer)
        self.__rUndo = qt.QPushButton(self.__rFrame)
        self.__rUndo.setPixmap(qt.QPixmap(QubIcons.getIconPath('undo.png')))
        rlayout.addWidget(self.__rUndo)
        self.__rRedo = qt.QPushButton(self.__rFrame)
        self.__rRedo.setPixmap(qt.QPixmap(QubIcons.getIconPath('redo.png')))
        rlayout.addWidget(self.__rRedo)
        self.__rStepCombo = _combo_box(True,self.__rFrame,"__rStepCombo")
        self.__rStepCombo.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.MinimumExpanding,qt.QSizePolicy.Fixed,0,0,
                                                    self.__rStepCombo.sizePolicy().hasHeightForWidth()))
        self.__rStepCombo.setAutoCompletion(1)
        self.__rStepCombo.setDuplicatesEnabled(0)
        rlayout.addWidget(self.__rStepCombo)

        self.__rMultiplyText = qt.QLabel(self.__rFrame,"__rMultiplyText")
        rlayout.addWidget(self.__rMultiplyText)
        
        padLayout.addWidget(self.__rFrame)

                         ####### PAD #######
        self.__padButton = _pad_button(self.__hAxisPos,self.__vAxisPos,self.__rAxisPos,
                                       self.__hUndo,self.__hRedo,self.__vUndo,self.__vRedo,self.__rUndo,self.__rRedo,
                                       self,"__padButton")
        self.__padButton.setSizePolicy(qt.QSizePolicy(qt.QSizePolicy.MinimumExpanding,qt.QSizePolicy.MinimumExpanding,
                                                      0,0,self.__padButton.sizePolicy().hasHeightForWidth()))
        self.__padButton.setFlat(1)
        padLayout.addWidget(self.__padButton)

        self.languageChange()

        self.clearWState(qt.Qt.WState_Polished)


        self.__hName,self.__hFormat,self.__hPos = ('H','%f',0.)
        self.__vName,self.__vFormat,self.__vPos = ('V','%f',0.)
        self.__rName,self.__rFormat,self.__rPos = ('R','%f',0.)
        self.__refreshHLabel()
        self.__refreshVLabel()
        self.__refreshRLabel()
        #Pixmap Step
        self.__stepPixmap = qt.QPixmap(QubIcons.getIconPath('step.png'))
    def languageChange(self):
        self.setCaption(self.__tr("Pad"))
        self.__padButton.setText(qt.QString.null)

    def setMultiplyStep(self,aFlag) :
        if(aFlag) :
            self.__multiplyInUse = self.__multiplyfactor
            self.__hMultiplyText.setText(' x %d' % self.__multiplyInUse)
            self.__vMultiplyText.setText(' x %d' % self.__multiplyInUse)
            self.__rMultiplyText.setText(' x %d' % self.__multiplyInUse)
        else :
            self.__multiplyInUse = 1
            self.__hMultiplyText.setText('')
            self.__vMultiplyText.setText('')
            self.__rMultiplyText.setText('')


    def setAxis(self,axisOring) :
        widgetDic = {QubPad.HORIZONTAL_AXIS : [self.__hFrame],
                     QubPad.VERTICAL_AXIS : [self.__vFrame],
                     QubPad.ROTATION_AXIS : [self.__rFrame]}
        for axis_type,widget_list in widgetDic.iteritems() :
            if not (axisOring & axis_type) :
                for widget in widget_list :
                    widget.hide()
            else :
                for widget in widget_list :
                    widget.show()
        self.__padButton.setAxis(axisOring)

             
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
        self.__refreshHLabel()
        
    def setHPos(self,pos) :
        """
        Horizontal Motor's position
        """
        self.__hPos = pos
        self.__refreshHLabel()
    def getHPos(self) :
        return self.__hPos
    
    def __refreshHLabel(self) :
        self.__hAxisName.setText('%s : ' % self.__hName)
        self.__hAxisPos.setText(self.__hFormat % self.__hPos)

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

    def getVPos(self) :
        return self.__vPos
    
    def __refreshVLabel(self) :
        self.__vAxisName.setText('%s : ' % self.__vName)
        self.__vAxisPos.setText(self.__vFormat % self.__vPos)

    def setRAxisName(self,name) :
        """
        Rotation Motor's name
        """
        self.__rName = name
        self.__refreshRLabel()
    def setRFormat(self,format) :
        """
        Rotation Motor's position format
        """
        self.__rFormat = format
        self.__refreshRLabel()
    def setRPos(self,pos) :
        """
        Rotation Motor's position
        """
        self.__rPos = pos
        self.__refreshRLabel()
    def getRPos(self) :
        return self.__rPos
    
    def __refreshRLabel(self) :
        self.__rAxisName.setText('%s : ' % self.__rName)
        self.__rAxisPos.setText(self.__rFormat % self.__rPos)


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

    def getRStep(self) :
        rStep,rValid = self.__rStepCombo.currentText().toFloat()
        return self.__multiplyInUse * rStep
    
    def setHSteps(self,step_list) :
        self.__hStepCombo.clear()
        for step in step_list :
            self.__hStepCombo.insertItem(self.__stepPixmap,str(step))

    def setVSteps(self,step_list) :
        self.__vStepCombo.clear()
        for step in step_list :
            self.__vStepCombo.insertItem(self.__stepPixmap,str(step))

    def setRSteps(self,step_list) :
        self.__rStepCombo.clear()
        for step in step_list :
            self.__rStepCombo.insertItem(self.__stepPixmap,str(step))
        
class QubPadPlug :
    def __init__(self) :
        self._padButton = None

    def stopVertical(self) :
        print "Should redefine Vertical Stop"
    def stopHorizontal(self) :
        print "Should redefine Horizontal Stop"
    def stopRotation(self) :
        print "Should redefine Rotation Stop"
    def up(self,step) :
        print "Should move %f step up" % step
    def down(self,step) :
        print "Should move %f step down" % step
    def left(self,step) :
        print "Should move %f step left" % step
    def right(self,step) :
        print "Should move %f step right" % step
    def clockwise(self,step) :
        print "Should move %f step clockwise" % step
    def unclockwise(self,step) :
        print "Should move %f step unclockwise" % step
    def setPad(self,aPad) :
        self._padButton = aPad

                      ####### Undo/Rdeo #######
class _undo_redo :
    def __init__(self,parent) :
        self.__undos = []
        self.__redos = []
        
    def undo(self,currentPos) :
        self.__redos.append(currentPos)
        return self.__undos.pop()
    def redo(self,currentPos) :
        self.__undos.append(currentPos)
        return self.__redos.pop()
    def addPos(self,pos) :
        self.__redos = []
        self.__undos.append(pos)
        if len(self.__undos) > 50 :
            self.__undos.pop(0)
    def setButtonState(self,undo,redo) :
        if len(self.__undos) :
            undo.setEnabled(True)
            qt.QToolTip.add(undo,'pos : %f' % float(self.__undos[-1]))
        else :
            undo.setEnabled(False)
            qt.QToolTip.remove(undo)
        if len(self.__redos) :
            redo.setEnabled(True)
            qt.QToolTip.add(redo,'pos : %f' % float(self.__redos[-1]))
        else :
            redo.setEnabled(False)
            qt.QToolTip.remove(redo)
   
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
     def move(self) :
         _AllMove(self._mgr)
     def endMove(self) :
         _OneMove(self._mgr)

class _AllMove(_MoveMotorState) :
    def __init__(self,manager) :
        _MoveMotorState.__init__(self,manager)
    def endMove(self) :
        _BothMove(self._mgr)

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
    
    def externalMove(self) :
        pass
    def move_left(self) :
        pass
    def move_right(self) :
        pass
    def undo(self) :
        pass
    def redo(self) :
        pass
    def end_move(self,aCbkFlag = False) :
        pass
    
    def setYourStateOnImage(self,image) :
        pass

    def setUndoRedoState(self,undoButton,redoButton) :
        undoButton.setEnabled(False)
        redoButton.setEnabled(False)

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
    def externalMove(self) :
        self._mgr.needRebuildImage = True
        _hExternalMove(self._mgr,self._plug)
    def move_left(self) :
        self._mgr.needRebuildImage = True
        _hMoveLeft(self._mgr,self._plug)
    def move_right(self) :
        self._mgr.needRebuildImage = True
        _hMoveRight(self._mgr,self._plug)
    def undo(self) :
        self._mgr.needRebuildImage = True
        _hUndoRedo(self._mgr,self._plug,True)
    def redo(self) :
        self._mgr.needRebuildImage = True
        _hUndoRedo(self._mgr,self._plug,False)
        
    def setUndoRedoState(self,undoButton,redoButton) :
        self._mgr.hundoredo.setButtonState(undoButton,redoButton)
    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('green'))

class _hExternalMove(_hMotorState) :
    def __init__(self,manager,plug) :
        _hMotorState.__init__(self,manager,plug)
        self._mgr.moveState.move()
    def __del__(self) :
        self._mgr.moveState.endMove()

    def end_move(self,aCbkFlag = False) :
        _hConnected(self._mgr,self._plug)
        if(aCbkFlag and self._plug) :
            self._plug.stopHorizontal()

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('yellow'))
    def setYourStateOnImage(self,image) :
        self._mgr.setGrayOn(image,self._mgr.LEFT)
        self._mgr.setGrayOn(image,self._mgr.RIGHT)
        

class _hMoveLeft(_hMotorState) :
    def __init__(self,manager,plug) :
        _hMotorState.__init__(self,manager,plug)
        self._mgr.hundoredo.addPos(self._mgr.getHPos())
        if(self._plug) :
            self._plug.left(self._mgr.getHStep())
        self._mgr.moveState.move()

    def __del__(self) :
        self._mgr.moveState.endMove()

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
        self._mgr.hundoredo.addPos(self._mgr.getHPos())
        if(self._plug) :
            self._plug.right(self._mgr.getHStep())
        self._mgr.moveState.move()

    def __del__(self) :
        self._mgr.moveState.endMove()

    def end_move(self,aCbkFlag = False) :
        _hConnected(self._mgr,self._plug)
        if(aCbkFlag and self._plug) :
            self._plug.stopHorizontal()
        
    def setYourStateOnImage(self,image) :
        self._mgr.setYellowOn(image,self._mgr.RIGHT)
        self._mgr.setGrayOn(image,self._mgr.LEFT)

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('yellow'))

class _hUndoRedo(_hMotorState) :
    def __init__(self,manager,plug,aUndoFlag) :
        _hMotorState.__init__(self,manager,plug)
        self.__step = 0
        currentPos = self._mgr.getHPos()
        if aUndoFlag :
            self.__step = self._mgr.hundoredo.undo(currentPos) - currentPos
        else :
            self.__step = self._mgr.hundoredo.redo(currentPos) - currentPos
        if(self._plug) :
            if self.__step > 0 :
                self._plug.right(self.__step)
            else :
                self._plug.left(-self.__step)
        self._mgr.moveState.move()

    def __del__(self) :
        self._mgr.moveState.endMove()

    def end_move(self,aCbkFlag = False) :
        _hConnected(self._mgr,self._plug)
        if(aCbkFlag and self._plug) :
            self._plug.stopHorizontal()
        
    def setYourStateOnImage(self,image) :
        if self.__step > 0 :
            self._mgr.setYellowOn(image,self._mgr.RIGHT)
            self._mgr.setGrayOn(image,self._mgr.LEFT)
        else :
            self._mgr.setYellowOn(image,self._mgr.LEFT)
            self._mgr.setGrayOn(image,self._mgr.RIGHT)

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
    
    def externalMove(self) :
        pass

    def move_up(self) :
        pass
    def move_down(self) :
        pass
    def undo(self) :
        pass
    def redo(self) :
        pass
    def end_move(self,aCbkFlag = False) :
        pass
    
    def setYourStateOnImage(self,image) :
        pass

    def setUndoRedoState(self,undoButton,redoButton) :
        undoButton.setEnabled(False)
        redoButton.setEnabled(False)

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
    def externalMove(self) :
        self._mgr.needRebuildImage = True
        _vExternalMove(self._mgr,self._plug)
    def move_up(self) :
        self._mgr.needRebuildImage = True
        _vMoveUp(self._mgr,self._plug)
    def move_down(self) :
        self._mgr.needRebuildImage = True
        _vMoveDown(self._mgr,self._plug)
    def undo(self) :
        self._mgr.needRebuildImage = True
        _vUndoRedo(self._mgr,self._plug,True)
    def redo(self) :
        self._mgr.needRebuildImage = True
        _vUndoRedo(self._mgr,self._plug,False)

    def setUndoRedoState(self,undoButton,redoButton) :
        self._mgr.vundoredo.setButtonState(undoButton,redoButton)
    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('green'))

class _vExternalMove(_vMotorState) :
    def __init__(self,manager,plug) :
        _vMotorState.__init__(self,manager,plug)
        self._mgr.moveState.move()
    def __del__(self) :
        self._mgr.moveState.endMove()

    def end_move(self,aCbkFlag = False) :
        _vConnected(self._mgr,self._plug)
        if(aCbkFlag and self._plug) :
            self._plug.stopVertical()

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('yellow'))
    def setYourStateOnImage(self,image) :
        self._mgr.setGrayOn(image,self._mgr.UP)
        self._mgr.setGrayOn(image,self._mgr.DOWN)

class _vMoveUp(_vMotorState) :
    def __init__(self,manager,plug) :
        _vMotorState.__init__(self,manager,plug)
        self._mgr.vundoredo.addPos(self._mgr.getVPos())
        if(self._plug) :
            self._plug.up(self._mgr.getVStep())
        self._mgr.moveState.move()
    def __del__(self) :
        self._mgr.moveState.endMove()
    
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
        self._mgr.vundoredo.addPos(self._mgr.getVPos())
        if(self._plug) :
            self._plug.down(self._mgr.getVStep())
        self._mgr.moveState.move()
    def __del__(self) :
        self._mgr.moveState.endMove()

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

class _vUndoRedo(_vMotorState) :
    def __init__(self,manager,plug,aUndoFlag) :
        _vMotorState.__init__(self,manager,plug)
        self.__step = 0
        currentPos = self._mgr.getVPos()
        if aUndoFlag :
            self.__step = self._mgr.vundoredo.undo(currentPos) - currentPos
        else :
            self.__step = self._mgr.vundoredo.redo(currentPos) - currentPos
        if(self._plug) :
            if self.__step > 0 :
                self._plug.up(self.__step)
            else :
                self._plug.down(-self.__step)
        self._mgr.moveState.move()
    def __del__(self) :
        self._mgr.moveState.endMove()
    
    def end_move(self,aCbkFlag = False) :
        self._mgr.needRebuildImage = True
        _vConnected(self._mgr,self._plug)
        if(aCbkFlag and self._plug) :
            self._plug.stopVertical()

    def setYourStateOnImage(self,image) :
        if self.__step > 0 :
            self._mgr.setYellowOn(image,self._mgr.UP)
            self._mgr.setGrayOn(image,self._mgr.DOWN)
        else :
            self._mgr.setYellowOn(image,self._mgr.DOWN)
            self._mgr.setGrayOn(image,self._mgr.UP)

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('yellow'))

                         ####### State Rotation Motor #######
class _rMotorState :
    def __init__(self,manager,plug) :
        self._mgr = manager
        self._plug = plug
        manager.rstate = self

    def setPlug(self,aPadPlug) :
        if(isinstance(aPadPlug,QubPadPlug)) :
            self._plug = aPadPlug
            aPadPlug.setPad(self._mgr)
        else :
            raise StandardError('Must be a PadPlug')

    def connect(self) :
        self._mgr.needRebuildImage = True
        _rConnected(self._mgr,self._plug)

    def disconnect(self) :
        self._mgr.needRebuildImage = True
        _rNConnected(self._mgr,self._plug)

    def error(self) :
        self._mgr.needRebuildImage = True
        _rError(self._mgr,self._plug)
    
    def externalMove(self) :
        pass

    def move_clockwise(self) :
        pass
    def move_unclockwise(self) :
        pass
    def undo(self) :
        pass
    def redo(self) :
        pass
    def end_move(self,aCbkFlag = False) :
        pass
    
    def setYourStateOnImage(self,image) :
        pass

    def setUndoRedoState(self,undoButton,redoButton) :
        undoButton.setEnabled(False)
        redoButton.setEnabled(False)

    def setBackgroundLabel(self,label) :
        bck_color = self._mgr.paletteBackgroundColor() 
        label.setPaletteBackgroundColor(bck_color)

class _rError(_rMotorState) :
    def __init__(self,manager,plug) :
        _rMotorState.__init__(self,manager,plug)
    def error(self) :
        pass
    def setYourStateOnImage(self,image) :
        self._mgr.setRedOn(image,self._mgr.CLOCKWISE)
        self._mgr.setRedOn(image,self._mgr.UNCLOCKWISE)

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('red'))

class _rNConnected(_rMotorState) :
    def __init__(self,manager,plug) :
        _rMotorState.__init__(self,manager,plug)
    def setYourStateOnImage(self,image) :
        self._mgr.setGrayOn(image,self._mgr.CLOCKWISE)
        self._mgr.setGrayOn(image,self._mgr.UNCLOCKWISE)

class _rConnected(_rMotorState) :
    def __init__(self,manager,plug) :
        _rMotorState.__init__(self,manager,plug)
    def connect(self) :
        pass
    def externalMove(self) :
        self._mgr.needRebuildImage = True
        _rExternalMove(self._mgr,self._plug)
    def move_clockwise(self) :
        self._mgr.needRebuildImage = True
        _rMoveClockwise(self._mgr,self._plug)
    def move_unclockwise(self) :
        self._mgr.needRebuildImage = True
        _rMoveUnclockwise(self._mgr,self._plug)

    def undo(self) :
        self._mgr.needRebuildImage = True
        _rUndoRedo(self._mgr,self._plug,True)
    def redo(self) :
        self._mgr.needRebuildImage = True
        _rUndoRedo(self._mgr,self._plug,False)

    def setUndoRedoState(self,undoButton,redoButton) :
        self._mgr.rundoredo.setButtonState(undoButton,redoButton)

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('green'))

class _rExternalMove(_rMotorState) :
    def __init__(self,manager,plug) :
        _rMotorState.__init__(self,manager,plug)
        self._mgr.moveState.move()
    def __del__(self) :
        self._mgr.moveState.endMove()

    def end_move(self,aCbkFlag = False) :
        _rConnected(self._mgr,self._plug)
        if(aCbkFlag and self._plug) :
            self._plug.stopRotation()

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('yellow'))
    def setYourStateOnImage(self,image) :
        self._mgr.setGrayOn(image,self._mgr.CLOCKWISE)
        self._mgr.setGrayOn(image,self._mgr.UNCLOCKWISE)

class _rMoveClockwise(_rMotorState) :
    def __init__(self,manager,plug) :
        _rMotorState.__init__(self,manager,plug)
        self._mgr.rundoredo.addPos(self._mgr.getRPos())
        if(self._plug) :
            self._plug.clockwise(self._mgr.getRStep())
        self._mgr.moveState.move()
    def __del__(self) :
        self._mgr.moveState.endMove()
    
    def end_move(self,aCbkFlag = False) :
        self._mgr.needRebuildImage = True
        _rConnected(self._mgr,self._plug)
        if(aCbkFlag and self._plug) :
            self._plug.stopRotation()

    def setYourStateOnImage(self,image) :
        self._mgr.setYellowOn(image,self._mgr.CLOCKWISE)
        self._mgr.setGrayOn(image,self._mgr.UNCLOCKWISE)

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('yellow'))

class _rMoveUnclockwise(_rMotorState) :
    def __init__(self,manager,plug) :
        _rMotorState.__init__(self,manager,plug)
        self._mgr.rundoredo.addPos(self._mgr.getRPos())
        if(self._plug) :
            self._plug.unclockwise(self._mgr.getRStep())
        self._mgr.moveState.move()
    def __del__(self) :
        self._mgr.moveState.endMove()

    def end_move(self,aCbkFlag = False) :
        self._mgr.needRebuildImage = True
        _rConnected(self._mgr,self._plug)
        if(aCbkFlag and self._plug) :
            self._plug.stopRotation()
        
    def setYourStateOnImage(self,image) :
        self._mgr.setYellowOn(image,self._mgr.UNCLOCKWISE)
        self._mgr.setGrayOn(image,self._mgr.CLOCKWISE)

    def setBackgroundLabel(self,label) :
        label.setPaletteBackgroundColor(qt.QColor('yellow'))

class _rUndoRedo(_rMotorState) :
    def __init__(self,manager,plug,aUndoFlag) :
        _rMotorState.__init__(self,manager,plug)
        self.__step = 0
        currentPos = self._mgr.getRPos()
        if aUndoFlag :
            self.__step = self._mgr.rundoredo.undo(currentPos) - currentPos
        else :
            self.__step = self._mgr.rundoredo.redo(currentPos) - currentPos
        if(self._plug) :
            if self.__step > 0 :
                self._plug.clockwise(self.__step)
            else :
                self._plug.unclockwise(-self.__step)
        self._mgr.moveState.move()
    def __del__(self) :
        self._mgr.moveState.endMove()
    
    def end_move(self,aCbkFlag = False) :
        self._mgr.needRebuildImage = True
        _rConnected(self._mgr,self._plug)
        if(aCbkFlag and self._plug) :
            self._plug.stopRotation()

    def setYourStateOnImage(self,image) :
        if self.__step > 0 :
            self._mgr.setYellowOn(image,self._mgr.CLOCKWISE)
            self._mgr.setGrayOn(image,self._mgr.UNCLOCKWISE)
        else:
            self._mgr.setYellowOn(image,self._mgr.UNCLOCKWISE)
            self._mgr.setGrayOn(image,self._mgr.CLOCKWISE)

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
    def __init__(self,hLabel,vLabel,rLabel,hUndo,hRedo,vUndo,vRedo,rUndo,rRedo,parent,name) :
        qt.QPushButton.__init__(self,parent,name)
        self.hLabel,self.vLabel,self.rLabel = hLabel,vLabel,rLabel
        self.__hUndo,self.__hRedo,self.__vUndo,self.__vRedo,self.__rUndo,self.__rRedo = hUndo,hRedo,vUndo,vRedo,rUndo,rRedo
        self.__pad = parent
        self.setMouseTracking(True)
        self.__multiplymode = False

        pad_path = QubIcons.getIconPath('pad.png')
        self.__image = qt.QImage(pad_path)
        self.__unhighlightImage(self.__image,0,0,self.__image.width(),self.__image.height())
        
        self.__idle = _drawIdle(self)

        
        self.UNDEF,self.UP,self.DOWN,self.LEFT,self.RIGHT,self.STOP,self.CLOCKWISE,self.UNCLOCKWISE = range(8)
        self.__under = self.UNDEF
        
        self.__currentimg = None
        self.moveState = _Stop(self)

        self.hundoredo = _undo_redo(self)
        self.vundoredo = _undo_redo(self)
        self.rundoredo = _undo_redo(self)

        self.hstate = _hNConnected(self,None)
        self.vstate = _vNConnected(self,None)
        self.rstate = _rNConnected(self,None)
        self.connect(self,qt.SIGNAL("clicked()"),self.__moveMotor)
        qt.QObject.connect(hUndo,qt.SIGNAL("clicked()"),self.__hstate_undo)
        qt.QObject.connect(hRedo,qt.SIGNAL("clicked()"),self.__hstate_redo)
        qt.QObject.connect(vUndo,qt.SIGNAL("clicked()"),self.__vstate_undo)
        qt.QObject.connect(vRedo,qt.SIGNAL("clicked()"),self.__vstate_redo)
        qt.QObject.connect(rUndo,qt.SIGNAL("clicked()"),self.__rstate_undo)
        qt.QObject.connect(rRedo,qt.SIGNAL("clicked()"),self.__rstate_redo)
        
        self.__axisType = 0
        self.setAxis(QubPad.HORIZONTAL_AXIS|QubPad.VERTICAL_AXIS|QubPad.ROTATION_AXIS)
        self.setMinimumSize(self.__currentimg.size())
        
    def setAxis(self,axisOring) :
        if self.__axisType != axisOring :
            self.__axisType = axisOring
            aNbAxis = 0
            for axis_type in [QubPad.HORIZONTAL_AXIS,QubPad.VERTICAL_AXIS,QubPad.ROTATION_AXIS] :
                if axisOring & axis_type :
                    aNbAxis += 1

            pad_path = QubIcons.getIconPath('pad.png')
            tmpimage = qt.QImage(pad_path)
            self.__unhighlightImage(tmpimage,0,0,tmpimage.width(),tmpimage.height())

            self.__column_size = tmpimage.width() / 3
            self.__line_size = tmpimage.height() / 3

            self.__tuple2ArrowType = {(2,1) : self.RIGHT,(0,1) : self.LEFT,
                                      (1,1) : self.STOP,
                                      (1,0) : self.UP, (1,2) : self.DOWN,
                                      (2,0) : self.CLOCKWISE, (0,2) : self.UNCLOCKWISE}
        
            if aNbAxis == 1 :
                if axisOring & QubPad.HORIZONTAL_AXIS :
                    ox,oy,z,k = self.__getBBoxFromColumnNLine(0,1)
                    z,k,ex,ey = self.__getBBoxFromColumnNLine(2,1)
                    tmpimage = self.__crop(tmpimage,ox,oy,ex,ey)
                    self.__column_size = tmpimage.width() / 3
                    self.__line_size = tmpimage.height()
                    self.__tuple2ArrowType = {(0,0) : self.LEFT,(1,0) : self.STOP,(2,0) : self.RIGHT}
                elif axisOring & QubPad.VERTICAL_AXIS :
                    ox,oy,z,k = self.__getBBoxFromColumnNLine(1,0)
                    z,k,ex,ey = self.__getBBoxFromColumnNLine(1,2)
                    tmpimage = self.__crop(tmpimage,ox,oy,ex,ey)
                    self.__line_size = tmpimage.height() / 3
                    self.__column_size = tmpimage.width()
                    self.__tuple2ArrowType = {(0,0) : self.UP,(0,1) : self.STOP,(0,2) : self.DOWN}
                else :                      # ROTATION ON HORIZONTAL
                    self.__movePixel(tmpimage,self.__getBBoxFromColumnNLine(0,2),self.__getBBoxFromColumnNLine(0,1))
                    self.__movePixel(tmpimage,self.__getBBoxFromColumnNLine(2,0),self.__getBBoxFromColumnNLine(2,1))
                    ox,oy,z,k = self.__getBBoxFromColumnNLine(0,1)
                    z,k,ex,ey = self.__getBBoxFromColumnNLine(2,1)
                    tmpimage = self.__crop(tmpimage,ox,oy,ex,ey)
                    self.__column_size = tmpimage.width() / 3
                    self.__line_size = tmpimage.height()
                    self.__tuple2ArrowType = {(0,0) : self.UNCLOCKWISE,(1,0) : self.STOP,(2,0) : self.CLOCKWISE}
            elif aNbAxis == 2 :
                if axisOring & QubPad.ROTATION_AXIS :
                    if axisOring & QubPad.HORIZONTAL_AXIS :
                        self.__movePixel(tmpimage,self.__getBBoxFromColumnNLine(0,2),self.__getBBoxFromColumnNLine(1,2))
                        self.__movePixel(tmpimage,self.__getBBoxFromColumnNLine(2,0),self.__getBBoxFromColumnNLine(1,0))
                        self.__erase(tmpimage,*self.__getBBoxFromColumnNLine(0,2))
                        self.__erase(tmpimage,*self.__getBBoxFromColumnNLine(2,0))
                        self.__tuple2ArrowType = {(2,1) : self.RIGHT,(0,1) : self.LEFT,
                                                  (1,1) : self.STOP,
                                                  (1,0) : self.CLOCKWISE, (1,2) : self.UNCLOCKWISE}
                    else :
                        self.__movePixel(tmpimage,self.__getBBoxFromColumnNLine(0,2),self.__getBBoxFromColumnNLine(0,1))
                        self.__movePixel(tmpimage,self.__getBBoxFromColumnNLine(2,0),self.__getBBoxFromColumnNLine(2,1))
                        self.__erase(tmpimage,*self.__getBBoxFromColumnNLine(0,2))
                        self.__erase(tmpimage,*self.__getBBoxFromColumnNLine(2,0))
                        self.__tuple2ArrowType = {(2,1) : self.CLOCKWISE,(0,1) : self.UNCLOCKWISE,
                                                  (1,1) : self.STOP,
                                                  (1,0) : self.UP, (1,2) : self.DOWN}
                else :
                    self.__erase(tmpimage,*self.__getBBoxFromColumnNLine(0,2))
                    self.__erase(tmpimage,*self.__getBBoxFromColumnNLine(2,0))
                    self.__tuple2ArrowType = {(2,1) : self.RIGHT,(0,1) : self.LEFT,
                                              (1,1) : self.STOP,
                                              (1,0) : self.UP, (1,2) : self.DOWN}
        
            self.__image = tmpimage
 
            self.__arrowType2tuple = {}
            for t,e in self.__tuple2ArrowType.iteritems() :
                self.__arrowType2tuple[e] = t

            self.needRebuildImage = True
            self.__rebuildImageIfNeeded()
                
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

    def paintEvent(self,event) :
        if not self.__idle.isActive() :
            self.__idle.start(0)

    def __moveMotor(self):
        if(self.__under == self.STOP) :
            self.hstate.end_move(True)
            self.vstate.end_move(True)
            self.rstate.end_move(True)
        elif(self.__under == self.UP) :
            self.vstate.move_up()
        elif(self.__under == self.DOWN) :
            self.vstate.move_down()
        elif(self.__under == self.LEFT) :
            self.hstate.move_left()
        elif(self.__under == self.RIGHT) :
            self.hstate.move_right()
        elif(self.__under == self.CLOCKWISE) :
            self.rstate.move_clockwise()
        elif(self.__under == self.UNCLOCKWISE) :
            self.rstate.move_unclockwise()
            
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)

    def __hstate_undo(self) : self.hstate.undo()
    def __hstate_redo(self) : self.hstate.redo()
    def __vstate_undo(self) : self.vstate.undo()
    def __vstate_redo(self) : self.vstate.redo()
    def __rstate_undo(self) : self.rstate.undo()
    def __rstate_redo(self) : self.rstate.redo()

    def __rebuildImageIfNeeded(self) :
        if(self.needRebuildImage) :
            self.needRebuildImage = False
            tmpimg = self.__image.copy()
            self.moveState.setYourStateOnImage(tmpimg)
            if self.__axisType & QubPad.HORIZONTAL_AXIS :
                self.hstate.setYourStateOnImage(tmpimg)
                self.hstate.setBackgroundLabel(self.hLabel)
                self.hstate.setUndoRedoState(self.__hUndo,self.__hRedo)
            if self.__axisType & QubPad.VERTICAL_AXIS :
                self.vstate.setYourStateOnImage(tmpimg)
                self.vstate.setBackgroundLabel(self.vLabel)
                self.vstate.setUndoRedoState(self.__vUndo,self.__vRedo)
            if self.__axisType & QubPad.ROTATION_AXIS :
                self.rstate.setYourStateOnImage(tmpimg)
                self.rstate.setBackgroundLabel(self.rLabel)
                self.rstate.setUndoRedoState(self.__rUndo,self.__rRedo)
            self.__currentimg = tmpimg


            
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
        paint = qt.QPainter(self)
        paint.drawPixmap(im_ox,im_oy,qt.QPixmap(image))
        paint.end()
        

        
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
                    
    def __crop(self,image,ox,oy,ex,ey) :
        returnImage = qt.QImage(ex - ox,ey - oy,32)
        returnImage.setAlphaBuffer(True)
        for ys,yd in zip(xrange(oy,ey),xrange(0,ey - oy)) :
            for xs,xd in zip(xrange(ox,ex),xrange(0,ex - ox)) :
                rgb = image.pixel(xs,ys)
                returnImage.setPixel(xd,yd,rgb)
        return returnImage
    def __movePixel(self,image,source,dest) :
        osx,osy,esx,esy = source
        odx,ody,edx,edy = dest
        for ys,yd in zip(xrange(osy,esy),xrange(ody,edy)) :
            for xs,xd in zip(xrange(osx,esx),xrange(odx,edx)) :
                rgb = image.pixel(xs,ys)
                image.setPixel(xd,yd,rgb)
    def __erase(self,image,ox,oy,ex,ey) :
        for y in xrange(oy,ey) :
            for x in xrange(ox,ex) :
                image.setPixel(x,y,qt.qRgba(0,0,0,0))
    def __multiplyStep(self,aFlag) :
        if(self.__multiplymode != aFlag) :
            self.__multiplymode = aFlag
            self.__pad.setMultiplyStep(self.__multiplymode)

    def getPad(self) :
        return self.__pad
    
    def getHStep(self) :
        return self.__pad.getHStep()

    def getVStep(self) :
        return self.__pad.getVStep()

    def getRStep(self) :
        return self.__pad.getRStep()
   
    def getHPos(self) :
        return self.__pad.getHPos()

    def getVPos(self) :
        return self.__pad.getVPos()

    def getRPos(self) :
        return self.__pad.getRPos()


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
        self.rstate.setPlug(aPadPlug)
        
    def endHMotorMoving(self) :
        self.hstate.end_move()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)

    def endVMotorMoving(self) :
        self.vstate.end_move()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)

    def endRMotorMoving(self) :
        self.rstate.end_move()
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

    def rMotorConnected(self) :
        self.rstate.connect()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)

    def hMotorDisconnected(self) :
        self.hstate.disconnect()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)
            
    def vMotorDisconnected(self) :
        self.vstate.disconnect()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)

    def rMotorDisconnected(self) :
        self.rstate.disconnect()
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

    def rMotorError(self) :
        self.rstate.error()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)
    
    def hMotorExternalMove(self) :
        self.hstate.externalMove()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)

    def vMotorExternalMove(self) :
        self.vstate.externalMove()
        if self.needRebuildImage and not self.__idle.isActive() :
            self.__idle.start(0)

    def rMotorExternalMove(self) :
        self.rstate.externalMove()
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
