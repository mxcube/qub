import qt
import qtcanvas
import sys
import math

from Qub.Widget.QubAction import QubAction, QubImageAction, QubToggleImageAction
from Qub.Widget.QubWidgetSet import QubColorToolButton, QubColorToolMenu
from Qub.Widget.QubWidgetSet import QubCanvasEllipse
from Qub.Icons.QubIcons import loadIcon


  
###############################################################################
###############################################################################
####################                                       ####################
####################         Miscallenous Actions          ####################
####################                                       ####################
###############################################################################
###############################################################################


###############################################################################
####################           QubToolButtonAction         ####################
###############################################################################
class QubToolButtonAction(QubAction):
    """
    This action send a signal "ButtonPressed" when user hit the button
    It creates a pushbutton in the toolbar/contextmenu or statusbar
    """
    def __init__(self,*args, **keys):
        """
        Constructor method
        label .. :  label is used as tooltip and as string in contextmenu
        name ... :  string name of the action. Will be used to get the
                    QToolButton icon file
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None).
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu.
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it.
        index .. :  Position of the selection widget of the action in its
                    group.
        
        Store in self._label the pushbutton label
        """
        QubAction.__init__(self, *args, **keys)
        
        self._item  = None
        self._label = keys.get('label','')
        
    def addToolWidget(self, parent):
        """
        create default pushbutton (with a label) in the toolbar of the view.
        """
        if self._widget is None:
            self._widget = qt.QToolButton(parent)
            self._widget.setAutoRaise(True)
            icon = qt.QIconSet(loadIcon("%s.png"%self._name))
            self._widget.setIconSet(icon)
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.sendSignal)
            qt.QToolTip.add(self._widget, self._label)
            
        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        self._menu = menu
        icon = qt.QIconSet(loadIcon("%s.png"%self._name))
        self._item = menu.insertItem(icon, qt.QString("%s"%self._label),
                                      self.sendSignal)
        
    def addStatusWidget(self, parent):
        """
        create pushbutton in the statusbar of the view
        """
        if self._widget is None:
            self._widget = qt.QPushButton(self._label, parent, "addtoppbutton")
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.sendSignal)
            qt.QToolTip.add(self._widget, self._label)
            
        return self._widget
         
    def sendSignal(self):
        """
        User have hit toolbar/contextmenu or statusbar pushbutton
        send "ButtonPressed" signal
        """ 
        self.emit(qt.PYSIGNAL("ButtonPressed"), ())

###############################################################################
####################             QubButtonAction           ####################
###############################################################################
class QubButtonAction(QubAction):
    """
    This action send a signal "ButtonPressed" when user hit the button
    It creates a pushbutton in the toolbar/contextmenu or statusbar
    """
    def __init__(self,*args, **keys):
        """
        Constructor method
        name ... :  string name of the action.
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None).
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu.
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it.
        index .. :  Position of the selection widget of the action in its
                    group.
        
        Store in self._label the pushbutton label
        """
        QubAction.__init__(self, *args, **keys)
        
        self._item  = None
        
    def addToolWidget(self, parent):
        """
        create default pushbutton (with a label) in the toolbar of the view.
        """
        if self._widget is None:
            self._widget = qt.QPushButton(self._label, parent, "addtoppbutton")
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.sendSignal)
            qt.QToolTip.add(self._widget, self._label)
            
        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        self._menu = menu
        self._item = menu.insertItem(qt.QString(self._label),
                                      self.sendSignal)
        
    def addStatusWidget(self, parent):
        """
        create pushbutton in the statusbar of the view
        """
        if self._widget is None:
            self._widget = qt.QPushButton(self._label, parent, "addtoppbutton")
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.sendSignal)
            qt.QToolTip.add(self._widget, self._label)
            
        return self._widget
         
    def sendSignal(self):
        """
        User have hit toolbar/contextmenu or statusbar pushbutton
        send "ButtonPressed" signal
        """ 
        self.emit(qt.PYSIGNAL("ButtonPressed"), ())

  
###############################################################################
###############################################################################
####################                                       ####################
####################            Print Actions              ####################
####################                                       ####################
###############################################################################
###############################################################################

###############################################################################
####################          QubPrintPreviewAction        ####################
###############################################################################
class QubPrintPreviewAction(QubAction):
    """
    This action send the pixmap of its associated view to a PrinPreview Widget.
    It creates a pushbutton in the toolbar/contextmenu.
    It uses the "getPPP" method of the "view" to get the pixmap.
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        name ... :  string name of the action.
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None).
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu.
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it.
        index .. :  Position of the selection widget of the action in its
                    group.
        Initialise print preview widget parameter.
        """
        QubAction.__init__(self, *args, **keys)

        self._preview = None
        
        self._item = None
        
    def addToolWidget(self, parent):
        """
        create print preview pushbutton in the toolbar of the view
        """
        if self._widget is None:
            self._widget = qt.QToolButton(parent, "addtoppbutton")
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("addpreview.png")))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.addPixmapToPP)
            qt.QToolTip.add(self._widget, "add this window to print preview")
            
        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        iconSet = qt.QIconSet(loadIcon("addpreview.png"))
        self._menu = menu
        self._item = menu.insertItem(iconSet, qt.QString("Print preview"),
                                      self.addPixmapToPP)
        
    def addStatusWidget(self, parent):
        """
        create print preview pushbutton in the toolbar of the view
        """
        if self._widget is None:
            self._widget = qt.QToolButton(parent, "addtoppbutton")
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("addpreview.png")))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.addPixmapToPP)
            qt.QToolTip.add(self._widget, "add this window to print preview")

        return self._widget
         
    def addPixmapToPP(self):
        """
        if the print preview widget parameter is set, show the print preview
        widget and send it the pixmap of the associated view
        """ 
        if self._preview is not None:
            if self._view is not None:
                if hasattr(self._view, "getPPP"):
                    self._preview.show()
                    self._preview.addPixmap(self._view.getPPP())

    def viewConnect(self, view):
        """
        register the view.
        This action will call the "getPPP" method of the view and send it
        to the print preview widget
        """
        self._view = view

    def previewConnect(self, preview):
        self._preview = preview

  
###############################################################################
###############################################################################
####################                                       ####################
####################      Actions form QubImageView        ####################
####################                                       ####################
###############################################################################
###############################################################################

###############################################################################
####################            QubColormapAction          ####################
###############################################################################

class QubColormapAction(QubAction):
    """
    This action will allow in a display widget to open the QubColormap dialog
    """
    def __init__(self, *args, **keys):
        from Qub.Widget.QubColormap import QubColormapDialog
        """
        Constructor method
        name ... :  string name of the action.
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None).
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu.
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it.
        index .. :  Position of the selection widget of the action in its
                    group.
        """
        QubAction.__init__(self, *args, **keys)
        
        self._item = None
        self._colormapDialog = None
        self.colormap = 0
        self.colorMin = 50
        self.colorMax = 150
        self.dataMin = 0
        self.dataMax = 200
        self.autoscale = 0
        self._name = "Array Colormap"
        
    def addToolWidget(self, parent):
        """
        create colormap pushbutton in the toolbar of the view
        create the colormap dialog if not already done
        """
        from Qub.Widget.QubColormap import QubColormapDialog
      
        """
        create colormap dialog
        """
        if self._colormapDialog is None:
            self._colormapDialog = QubColormapDialog(parent)
            self._colormapDialog.setParam(self.colormap, self.colorMin,
                                          self.colorMax, self.dataMin,
                                          self.dataMax, self.autoscale)
            self.connect(self._colormapDialog, qt.PYSIGNAL("ColormapChanged"),
                         self.sendColormap)
        
        """
        create widget for the view toolbar
        """   
        if self._widget is None:
            self._widget = qt.QToolButton(parent, "colormap")
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("colormap.png")))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                            self.showColormapDialog)
            qt.QToolTip.add(self._widget, "Open colormap selector")

        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        self._menu = menu
        iconSet = qt.QIconSet(loadIcon("colormap.png"))
        self._item = menu.insertItem(iconSet, qt.QString("Colormap"),
                                      self.showColormapDialog)
        
    def addStatusWidget(self, parent):
        """
        create print preview pushbutton in the toolbar of the view
        """
        if self._widget is None:
            self._widget = qt.QToolButton(parent, "colormap")
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("colormap.png")))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                                 self.showColormapDialog)
            qt.QToolTip.add(self._widget, "Open colormap selector")

        return self._widget
        
    def showColormapDialog(self):
        self._colormapDialog.show()
         
    def setParam(self, colormap=None, colorMin=None, colorMax=None,
                 dataMin=None, dataMax=None, autoscale=None):
        """
        send the parameters to the QubDialog
        save them in case QubColormapDialog does not exists in order to
        send them later
        """
        self.colormap = colormap
        self.colorMin = colorMin
        self.colorMax = colorMax
        self.dataMin = dataMin
        self.dataMax = dataMax
        self.autoscale = autoscale
        if self._colormapDialog is not None:
            self._colormapDialog.setParam(colormap, colorMin, colorMax, 
                                          dataMin, dataMax, autoscale)

    def sendColormap(self, colormap, autoscale, colorMin, colorMax):
        self.emit(qt.PYSIGNAL("ColormapChanged"),
                  (colormap, autoscale, colorMin, colorMax))



###############################################################################
####################          QubSeparatorAction           ####################
###############################################################################
class QubSeparatorAction(QubAction):
    """
    """
    def __init__(self,  *args, **keys):
        QubAction.__init__(self, *args, **keys)
        self._name = "sep"

    def addToolWidget(self, parent):
        """
        create widget for the view toolbar
        """
                
        if self._widget is None:
            self._widget = qt.QFrame(parent)
            self._widget.setFrameShape(qt.QFrame.VLine)
            self._widget.setFrameShadow(qt.QFrame.Sunken)
            #rect = self._widget.rect()
            #rect.setY(rect.y()+2)
            #self._widget.setFrameRect(rect)
        
        return self._widget
    

###############################################################################
####################            QubPointSelection          ####################
###############################################################################
class QubPointSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select a point and send its (x, y) parameters using
    PYSIGNAL("PointSelected")
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        name ... :  string name of the action
        qubImage :  action will act on a QubImage object. It can be set in
                    the constructor method or using the "viewConnect" method
                    of the class 
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None)
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group
        Creates action widget to put in "group" dockarea of the "toolbar"
        Return this widget.
        Use name of the action to find icon file
        Initialyse rectangle position variables
        """
        QubToggleImageAction.__init__(self, *args, **keys)

        self.__point = qt.QPoint(0,0)
        self.__mpoint = qt.QPoint(0,0)
        
        if self._name == "default":
            self._name = "point"
    
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        canvas = self._qubImage.canvas()

        self._l1  = qtcanvas.QCanvasLine(canvas)
        self._l2  = qtcanvas.QCanvasLine(canvas)
        self._c   = QubCanvasEllipse(20, 20, 0, 5760, canvas)

        self._cl1 = qtcanvas.QCanvasLine(canvas)
        self._cl2 = qtcanvas.QCanvasLine(canvas)
        self._cc  = QubCanvasEllipse(20, 20, 0, 5760, canvas)

        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """   
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        """
        
        for item in [self._l1,self._l2,self._c,self._cl1,self._cl2,self._cc]:
            item.setPen(qt.QPen(color))
            item.update()
       
    def _setState(self, bool):
        """
        Draw or Hide point canvas item
        """
        self.__state = bool

        if self._l1  is not None and self._l2  is not None and \
           self._c   is not None and self._cl1 is not None and \
           self._cl2 is not None and self._cc  is not None:
            if self.__state:
                self.signalConnect(self._qubImage)
                self.setColor(self._qubImage.foregroundColor())
                for item in [self._l1,self._l2,self._c,self._cl1,self._cl2,self._cc]:
                    item.show()
            else:
                self.signalDisconnect(self._qubImage)
                for item in [self._l1,self._l2,self._c,self._cl1,self._cl2,self._cc]:
                    item.hide()

            for item in [self._l1,self._l2,self._c,self._cl1,self._cl2,self._cc]:
                item.update()
    
    def mouseMove(self, event):
        """
        One of the drawing follows the mouse during the move
        """
        try:
            (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), event.y())
            self.__mpoint.setX(x)
            self.__mpoint.setY(y)

            self.viewportUpdate()
        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])
    
    def mouseRelease(self, event):
        """
        Rectangle selection is finished, send corresponding signal
        with coordinates
        """
        try:
            (x, y)=self._qubImage.matrix().invert()[0].map(event.x(), event.y())

            self.__mpoint.setX(x)
            self.__mpoint.setY(y)

            self.__point.setX(x)
            self.__point.setY(y)

            self.emit(qt.PYSIGNAL("PointSelected"),  (x, y))

            self.viewportUpdate()
        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])
        
    def viewportUpdate(self):
        """
        Draw rectangle either if qubImage pixmap has been updated or
        rectangle coordinates have been changed by the user
        """
        point = self._qubImage.matrix().map(self.__point)
        mpoint = self._qubImage.matrix().map(self.__mpoint)

        self._l1.setPoints(point.x()-10, point.y()-10,
                           point.x()+10, point.y()+10)   
        self._l2.setPoints(point.x()-10, point.y()+10,
                           point.x()+10, point.y()-10)
        self._c.move(point.x(), point.y())  

        self._cl1.setPoints(mpoint.x()-10, mpoint.y()-10,
                            mpoint.x()+10, mpoint.y()+10)   
        self._cl2.setPoints(mpoint.x()-10, mpoint.y()+10,
                            mpoint.x()+10, mpoint.y()-10)   
        self._cc.move(mpoint.x(), mpoint.y())  

        for item in [self._l1,self._l2,self._c,self._cl1,self._cl2,self._cc]:
            if item is not None:
                item.update()


###############################################################################
####################          QubRectangleSelection        ####################
###############################################################################
class QubRectangleSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select a rectangle and send its (x, y, width, height) parameters using
    PYSIGNAL("RectangleSelected")
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        name ... :  string name of the action
        qubImage :  action will act on a QubImage object. It can be set in
                    the constructor method or using the "viewConnect" method
                    of the class 
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None)
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group
        square   :  selction is fixed aspect square selection
        Creates action widget to put in "group" dockarea of the "toolbar"
        Return this widget.
        Use name of the action to find icon file
        Initialyse rectangle position variables
        """
        QubToggleImageAction.__init__(self, *args, **keys)

        self.__rectCoord = qt.QRect(0, 0, 1, 1)

        self.__squareFlag = keys.get("square", False)
        if self._name == "default":
            self._name = "rectangle"
    
    def setRectanglePosition(self, x, y, w, h):
        self.__rectCoord.setRect(x, y, w, h)
        
        self.viewportUpdate()
    
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__rectangle = qtcanvas.QCanvasRectangle(self.__rectCoord,
                                                     self._qubImage.canvas()
                                                     )
        self.setColor(self._qubImage.foregroundColor())


    def setColor(self, color):
        """   
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        """
        self.__rectangle.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__rectangle.setPen(qt.QPen(color))
        self.__rectangle.update()
       
    def initSelection(self,ox,oy,width,height) :
        self.__rectCoord.setRect(ox,oy,width,height)
        self.emit(qt.PYSIGNAL("RectangleSelected"), 
                  (self.__rectCoord.x(), self.__rectCoord.y(), 
                   self.__rectCoord.width(), self.__rectCoord.height()))
        
    def _setState(self, bool):
        """
        Draw or Hide rectangle canvas item
        """
        self.__state = bool

        if self.__rectangle is not None:
            if self.__state:
                self.signalConnect(self._qubImage)
                self.setColor(self._qubImage.foregroundColor())
                self.__rectangle.show()
            else:
                self.signalDisconnect(self._qubImage)
                self.__rectangle.hide()
            
            self.__rectangle.update()

    def mousePress(self, event):
        """
        Update upper-left corner position of the rectangle and sets its
        width and height to 1
        """
        (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), event.y())
        self.__rectCoord.setRect(x, y, 1, 1)
        self.viewportUpdate()
    
    def mouseMove(self, event):
        """
        Upper-left corener of the rectangle has been fixed when mouse press,
        Updates now the width and height to follow the mouse position
        """
        if event.state() == qt.Qt.LeftButton:
            (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), 
                                                           event.y())
            w = x - self.__rectCoord.x()
            h = y - self.__rectCoord.y()
            if self.__squareFlag :
                w = max(w,h)
                h = w
                
            self.__rectCoord.setSize(qt.QSize(w, h))
                
            self.viewportUpdate()
    
    def mouseRelease(self, event):
        """
        Rectangle selection is finished, send corresponding signal
        with coordinates
        """
        (x, y)=self._qubImage.matrix().invert()[0].map(event.x(), event.y())
        w = x - self.__rectCoord.x()
        h = y - self.__rectCoord.y()

        if self.__squareFlag :
            w = max(w,h)
            h = w

        self.__rectCoord.setSize(qt.QSize(w, h))

        self.emit(qt.PYSIGNAL("RectangleSelected"), 
                  (self.__rectCoord.x(), self.__rectCoord.y(), 
                   self.__rectCoord.width(), self.__rectCoord.height()))
        
        self.viewportUpdate()
        
    def viewportUpdate(self):
        """
        Draw rectangle either if qubImage pixmap has been updated or
        rectangle coordinates have been changed by the user
        """
        rect = self._qubImage.matrix().map(self.__rectCoord)

        self.__rectangle.setSize(rect.width(), rect.height())
        self.__rectangle.move(rect.x(), rect.y())

        self.__rectangle.update()            
###############################################################################
#                          QubZoomRectangle                                   #
###############################################################################
class QubZoomRectangle(QubToggleImageAction) :
    UNDEF,DRAG,MOVE = range(3)
    
    def __init__(self,*args,**keys) :
        QubToggleImageAction.__init__(self,*args,**keys)
        self.__rectCoord = qt.QRect(0,0,1,1)

        self.__squareFlag = keys.get('square',False)
        if self._name == 'default' :
            self._name = 'rectangle'

        self.__mode = QubZoomRectangle.UNDEF

    def viewConnect(self,qubImage) :
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__rectangle = qtcanvas.QCanvasRectangle(self.__rectCoord,
                                                     self._qubImage.canvas())
        self.setColor(self._qubImage.foregroundColor())

    def setColor(self,color) :
        """   
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        """
        self.__rectangle.setPen(qt.QPen(color,2))
        self.__rectangle.update()

    def initSelection(self,ox,oy,width,height) :
        self.__rectCoord.setRect(ox,oy,width,height)
        rect = self.__rectCoord.normalize()
        self.emit(qt.PYSIGNAL("RectangleSelected"), 
                  (rect.x(), rect.y(), 
                   rect.width(),rect.height()))
        self.viewportUpdate()
        
    def _setState(self,aFlag) :
        if aFlag :
            self.signalConnect(self._qubImage)
            self.setColor(self._qubImage.foregroundColor())
            self.__rectangle.show()
        else:
            self.signalDisconnect(self._qubImage)
            self.__rectangle.hide()
        self.emit(qt.PYSIGNAL("Actif"),(aFlag,))
        
        self.viewportUpdate()

    def mousePress(self,event) :
        if event.button() == qt.Qt.LeftButton :
            (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), event.y())
            if self.__rectCoord.contains(x,y) :
                self.__mode = QubZoomRectangle.MOVE
            else :
                self.__mode = QubZoomRectangle.DRAG
                self.__rectCoord.setRect(x, y, 1, 1)
                self.viewportUpdate()
            
    def mouseMove(self,event) :
        try :
            if self.__mode == QubZoomRectangle.DRAG :
                (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), 
                                                                 event.y())
                w = x - self.__rectCoord.x()
                h = y - self.__rectCoord.y()
                if self.__squareFlag :
                    w = max(w,h)
                    h = w
                self.__rectCoord.setSize(qt.QSize(w, h))
                self.viewportUpdate()
            elif self.__mode == QubZoomRectangle.MOVE :
                (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), 
                                                                 event.y())
                canvasRect = self._qubImage.matrix().invert()[0].map(self._qubImage.canvas().rect())
                rect = self.__rectCoord.normalize()
                if x > canvasRect.width() - rect.width() / 2 :
                    x = canvasRect.width() - rect.width() / 2
                elif x < rect.width() / 2 :
                    x = rect.width() / 2

                if y > (canvasRect.height() - rect.height() / 2) :
                    y = canvasRect.height() - rect.height() / 2
                elif y < rect.height() / 2 :
                    y = rect.height() / 2

                self.__rectCoord.moveCenter(qt.QPoint(x,y))

                rect = self.__rectCoord.normalize()
                self.emit(qt.PYSIGNAL("RectangleSelected"), 
                          (rect.x(), rect.y(), 
                           rect.width(),rect.height()))
                self.viewportUpdate()
        except:
            import traceback
            traceback.print_exc()
            
    def mouseRelease(self, event):
        if self.__mode == QubZoomRectangle.DRAG :
            rect = self.__rectCoord.normalize()
            self.emit(qt.PYSIGNAL("RectangleSelected"), 
                      (rect.x(), rect.y(), 
                       rect.width(),rect.height()))
        self.__mode = QubZoomRectangle.UNDEF

    def viewportUpdate(self) :

        rect = self._qubImage.matrix().map(self.__rectCoord)

        self.__rectangle.setSize(rect.width(), rect.height())
        self.__rectangle.move(rect.x(), rect.y())
        self.__rectangle.update()

###############################################################################
####################            QubLineSelection           ####################
###############################################################################
class QubLineSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select a line and send the start and end point coordinates using
    PYSIGNAL("LineSelected")
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        name ... :  string name of the action
        qubImage :  action will act on a QubImage object. It can be set in
                    the constructor method or using the "viewConnect" method
                    of the class 
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None)
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group
        Creates action widget to put in "group" dockarea of the "toolbar"
        Return this widget.
        Use name of the action to find icon file
        Initialyse line start and end points variables
        """
        QubToggleImageAction.__init__(self, *args, **keys)

        self.__startPt = qt.QPoint(0,0)
        self.__endPt   = qt.QPoint(1,1)


        if self._name == "default":
            self._name = "line"
        
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__line = qtcanvas.QCanvasLine(self._qubImage.canvas())
        self.__line.setPoints(self.__startPt.x(), self.__startPt.y(),
                              self.__endPt.x(), self.__endPt.y())

        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """
        set foreground color
        """
        self.__line.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__line.setPen(qt.QPen(color))
        self.__line.update()
       
    def _setState(self, bool):
        """
        Draw or Hide line canvas item
        """
        self.__state = bool
        if self.__line is not None:
            if self.__state:
                self.signalConnect(self._qubImage)
                self.setColor(self._qubImage.foregroundColor())
                self.__line.show()
            else:
                self.signalDisconnect(self._qubImage)
                self.__line.hide()
            
            self.__line.update()

    def mousePress(self, event):
        """
        Update start and end point of the line to be the same on the mouse
        position
        """ 
        (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), event.y())
        self.__startPt.setX(x)
        self.__startPt.setY(y)
        self.__endPt.setX(x)
        self.__endPt.setY(y)
            
        self.viewportUpdate()

    def mouseMove(self, event):
        """
        Start point has been fixed by press event, make end point followed
        the mouse
        """
        if event.state() == qt.Qt.LeftButton:
            (x, y) = self._qubImage.matrix().invert()[0].map(event.x(),
                                                           event.y())
            self.__endPt.setX(x)
            self.__endPt.setY(y)
            
            self.viewportUpdate()

    def mouseRelease(self, event):
        """
        Line selection is finished, send start and end point coordinates
        with PYSIGNAL("LineSelected")
        """
        try:
            (x, y) = self._qubImage.matrix().invert()[0].map(event.x(),
                                                           event.y())
            
            self.__endPt.setX(x)
            self.__endPt.setY(y)
            (x1, y1, x2, y2) = (self.__startPt.x(), self.__startPt.y(),
                                self.__endPt.x(), self.__endPt.y())
            
            self.emit(qt.PYSIGNAL("LineSelected"), (x1, y1, x2, y2))
            
            self.viewportUpdate()
        except:
            sys.excepthook(sys.exc_info()[0],
                           sys.exc_info()[1],
                           sys.exc_info()[2])
                
    def viewportUpdate(self):
        """
        Draw line either if qubImage pixmap has been updated or
        line coordinates have been changed by the user
        """
        try:
            startPt = self._qubImage.matrix().map(self.__startPt)
            endPt = self._qubImage.matrix().map(self.__endPt)

            self.__line.setPoints(startPt.x(),startPt.y(), endPt.x(), endPt.y())

            self.__line.update()
        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])


###############################################################################
####################            QubVLineSelection           ###################
###############################################################################

class QubVLineSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select a vertical line and send x position using PYSIGNAL("VLineSelected").
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        name ... :  string name of the action
        qubImage :  action will act on a QubImage object. It can be set in
                    the constructor method or using the "viewConnect" method
                    of the class 
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None)
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group
        Creates action widget to put in "group" dockarea of the "toolbar"
        Return this widget.
        Use name of the action to find icon file.
        Initialise line start and end points variables.
        """
        QubToggleImageAction.__init__(self, *args, **keys)
        
        self.__cursorPos  = 0
        self.__imageHeight = 50

        if self._qubImage != None:
            self.__imageHeight = self._qubImage.visibleHeight()
        else:
            self.__imageHeight = 50

        self.__startPt = qt.QPoint(0, 0)
        self.__endPt   = qt.QPoint(0, self.__imageHeight)

        if self._name == "default":
            self._name = "vline"
        
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__line = qtcanvas.QCanvasLine(self._qubImage.canvas())
        self.__line.setPoints(self.__startPt.x(), self.__startPt.y(),
                              self.__endPt.x(), self.__endPt.y())

        self.__VLineCursor = qtcanvas.QCanvasLine(self._qubImage.canvas())
        self.__VLineCursor.setPoints(self.__cursorPos, 0,
                                     self.__cursorPos,
                                     self._qubImage.visibleHeight())

        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """
        set foreground color
        """
        self.__line.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__line.setPen(qt.QPen(color))
        self.__line.update()

        self.__VLineCursor.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__VLineCursor.setPen(qt.QPen(color))
        self.__VLineCursor.update()

    def _setState(self, bool):
        """
        Draw or Hide line canvas item
        """
        self.__state = bool
        if self.__line is not None:
            if self.__state:
                self.signalConnect(self._qubImage)
                self.setColor(self._qubImage.foregroundColor())
                self.__line.show()
                self.__VLineCursor.show()
            else:
                self.signalDisconnect(self._qubImage)
                self.__line.hide()
                self.__VLineCursor.hide()
            
            self.__line.update()
            self.__VLineCursor.update()
                
    def mousePress(self, event):
        """
        Update start and end point of the line to be the same on the mouse
        position
        """ 
        (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), event.y())
        self.__startPt.setX(x)
        self.__startPt.setY(0)
        self.__endPt.setX(x)
        self.__endPt.setY(self._qubImage.visibleHeight())
        
        try:
            self.emit(qt.PYSIGNAL("VLineSelected"), (x,))
            self.viewportUpdate()
        except:
            sys.excepthook(sys.exc_info()[0],
                           sys.exc_info()[1],
                           sys.exc_info()[2])
            
    def mouseMove(self, event):
        """
        Move the VLine cursor.
        """
        (x, y) = self._qubImage.matrix().invert()[0].map(event.x(),
                                                       event.y())
        self.__cursorPos = x
        self.viewportUpdate()

    def mouseRelease(self, event):
        """
        """
        pass 

    def viewportUpdate(self):
        """
        Draw line either if qubImage pixmap has been updated or
        line coordinates have been changed by the user
        """
        try:
            startPt = self._qubImage.matrix().map(self.__startPt)
            endPt = self._qubImage.matrix().map(self.__endPt)

            self.__line.setPoints(startPt.x(),startPt.y(), endPt.x(), endPt.y())
            self.__VLineCursor.setPoints(self.__cursorPos, 0,
                                         self.__cursorPos,
                                         self._qubImage.visibleHeight())
                
            self.__line.update()
            self.__VLineCursor.update()

        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])





###############################################################################
####################            QubHLineSelection           ###################
###############################################################################
class QubHLineSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select an horizontal line and send position using PYSIGNAL("HLineSelected").
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        name ... :  string name of the action
        qubImage :  action will act on a QubImage object. It can be set in
                    the constructor method or using the "viewConnect" method
                    of the class 
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None)
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group
        Creates action widget to put in "group" dockarea of the "toolbar"
        Return this widget.
        Use name of the action to find icon file.
        Initialise line start and end points variables.
        """
        QubToggleImageAction.__init__(self, *args, **keys)
        
        self.__cursorPos  = 0
        self.__imageWidth = 50

        if self._qubImage != None:
            __imgWidth = self._qubImage.visibleWidth()
        else:
            __imgWidth = 50
            
        self.__startPt = qt.QPoint(0, 0)
        self.__endPt   = qt.QPoint(0, __imgWidth)

        if self._name == "default":
            self._name = "hline"
        
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__line = qtcanvas.QCanvasLine(self._qubImage.canvas())
        self.__line.setPoints(self.__startPt.x(), self.__startPt.y(),
                              self.__endPt.x(), self.__endPt.y())

        self.__HLineCursor = qtcanvas.QCanvasLine(self._qubImage.canvas())
        self.__HLineCursor.setPoints(0, self.__cursorPos,
                                     self._qubImage.visibleWidth(),
                                     self.__cursorPos )

        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """
        set foreground color
        """
        self.__line.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__line.setPen(qt.QPen(color))
        self.__line.update()

        self.__HLineCursor.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__HLineCursor.setPen(qt.QPen(color))
        self.__HLineCursor.update()

    def _setState(self, bool):
        """
        Draw or Hide Hline canvas item
        """
        self.__state = bool
        if self.__line is not None:
            if self.__state:
                self.signalConnect(self._qubImage)
                self.setColor(self._qubImage.foregroundColor())
                self.__line.show()
                self.__HLineCursor.show()
            else:
                self.signalDisconnect(self._qubImage)
                self.__line.hide()
                self.__HLineCursor.hide()
            
            self.__line.update()
            self.__HLineCursor.update()
                
    def mousePress(self, event):
        """
        Update start and end point of the line to be the same on the mouse
        position
        """ 
        (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), event.y())
        self.__startPt.setX(0)
        self.__startPt.setY(y)
        self.__endPt.setX(self._qubImage.visibleWidth())
        self.__endPt.setY(y)
        
        try:
            self.emit(qt.PYSIGNAL("HLineSelected"), (y,))
            self.viewportUpdate()
        except:
            sys.excepthook(sys.exc_info()[0],
                           sys.exc_info()[1],
                           sys.exc_info()[2])
            
    def mouseMove(self, event):
        """
        Move the VLine cursor.
        """
        (x, y) = self._qubImage.matrix().invert()[0].map(event.x(),
                                                       event.y())
        self.__cursorPos = y
        
        self.viewportUpdate()

    def mouseRelease(self, event):
        """
        """
        pass 

    def viewportUpdate(self):
        """
        Draw line either if qubImage pixmap has been updated or
        line coordinates have been changed by the user
        """
        try:
            startPt = self._qubImage.matrix().map(self.__startPt)
            endPt = self._qubImage.matrix().map(self.__endPt)

            self.__line.setPoints(startPt.x(),startPt.y(), endPt.x(), endPt.y())
            self.__HLineCursor.setPoints(0, self.__cursorPos,
                                         self._qubImage.visibleWidth(),
                                         self.__cursorPos )
                
            self.__line.update()
            self.__HLineCursor.update()

        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])


###############################################################################
#####################          QubCircleSelection        ######################
###############################################################################
class QubCircleSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select a circle and send its (center, radius) parameters using
    PYSIGNAL("CircleSelected")
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        name ... :  string name of the action
        qubImage :  action will act on a QubImage object. It can be set in
                    the constructor method or using the "viewConnect" method
                    of the class 
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None)
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group
        Creates action widget to put in "group" dockarea of the "toolbar"
        Return this widget.
        Use name of the action to find icon file
        Initialyse circle position variables
        """
        QubToggleImageAction.__init__(self, *args, **keys)

        self.__rectCoord = qt.QRect(0, 0, 1, 1)
        self.__x0 = 0
        self.__y0 = 0
        self.__radius = 0
        
        if self._name == "default":
            self._name = "circle"
    
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__circle = QubCanvasEllipse( self.__rectCoord.width(),
                                         self.__rectCoord.height(),
                                         self._qubImage.canvas()
                                         )
        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """   
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        """
        self.__circle.setPen(qt.QPen(color))
        self.__circle.update()

    def _setState(self, bool):
        """
        Draw or Hide circle canvas item
        """
        self.__state = bool
        if self.__circle is not None:
            if self.__state:
                self.signalConnect(self._qubImage)
                self.setColor(self._qubImage.foregroundColor())
                self.__circle.show()
            else:
                self.signalDisconnect(self._qubImage)
                self.__circle.hide()
            
            self.__circle.update()

    def mousePress(self, event):
        """
        Update upper-left corner position of the rectangle and sets its
        width and height to 1
        """ 
        (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), event.y())
        self.__x0 = x
        self.__y0 = y
        self.__rectCoord.setRect(x, y, 1, 1)
        self.viewportUpdate()
    
    def mouseMove(self, event):
        """
        Upper-left corner of the rectangle has been fixed when mouse press,
        Updates now the width and height to follow the mouse position
        """
        if event.state() == qt.Qt.LeftButton:
            (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), 
                                                           event.y())
            
            dx = x - self.__x0
            dy = y - self.__y0
            radius = math.sqrt( pow(dx,2) + pow(dy,2) )
            w = radius * 2.0
            h = radius * 2.0
            xc = self.__x0 - radius
            yc = self.__y0 - radius
            self.__rectCoord.setRect(xc, yc, w, h)
            self.__radius = radius
            self.viewportUpdate()
            
    def mouseRelease(self, event):
        """
        Rectangle selection is finished, send corresponding signal
        with coordinates (center and radius)
        """
        self.emit(qt.PYSIGNAL("CircleSelected"), 
                  (self.__x0, self.__y0, self.__radius))
        
        self.viewportUpdate()
        
    def viewportUpdate(self):
        """
        Draw Circle either if qubImage pixmap has been updated or
        rectangle coordinates have been changed by the user
        """
        rect = self._qubImage.matrix().map(self.__rectCoord)
        (x,y) = self._qubImage.matrix().map(self.__x0, self.__y0)

        self.__circle.setSize(rect.width(), rect.height())
        self.__circle.move(x, y)
        
        self.__circle.update()            






###############################################################################
#####################          QubDiscSelection        ######################
###############################################################################
class QubDiscSelection(QubToggleImageAction):
    """
    Action acting on QubImage widget.
    Select a disc and send its (center, radius) parameters using
    PYSIGNAL("DiscSelected")
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        name ... :  string name of the action
        qubImage :  action will act on a QubImage object. It can be set in
                    the constructor method or using the "viewConnect" method
                    of the class 
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None)
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group
        Creates action widget to put in "group" dockarea of the "toolbar"
        Return this widget.
        Use name of the action to find icon file
        Initialyse disc position variables
        """
        QubToggleImageAction.__init__(self, *args, **keys)

        self.__rectCoord = qt.QRect(0, 0, 1, 1)
        self.__x0 = 0
        self.__y0 = 0
        self.__radius = 0
              
        if self._name == "default":
            self._name = "disc"
    
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__disc = qtcanvas.QCanvasEllipse( self.__rectCoord.width(),
                                         self.__rectCoord.height(),
                                         self._qubImage.canvas()
                                         )
        self.setColor(self._qubImage.foregroundColor())

    def setColor(self, color):
        """   
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        """
        self.__disc.setBrush(qt.QBrush(color, qt.Qt.DiagCrossPattern))
        self.__disc.setPen(qt.QPen(color))
        self.__disc.update()

    def _setState(self, bool):
        """
        Draw or Hide disc canvas item
        """
        self.__state = bool
        if self.__disc is not None:
            if self.__state:
                self.signalConnect(self._qubImage)
                self.setColor(self._qubImage.foregroundColor())
                self.__disc.show()
            else:
                self.signalDisconnect(self._qubImage)
                self.__disc.hide()
            
            self.__disc.update()

    def mousePress(self, event):
        """
        Update upper-left corner position of the rectangle and sets its
        width and height to 1
        """
        print "mousePress %d,%d" % (event.x(), event.y())
        (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), event.y())
        self.__x0 = x
        self.__y0 = y
        self.__rectCoord.setRect(x, y, 1, 1)
        self.viewportUpdate()
    
    def mouseMove(self, event):
        """
        Upper-left corner of the rectangle has been fixed when mouse press,
        Updates now the width and height to follow the mouse position
        """
        if event.state() == qt.Qt.LeftButton:
            (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), 
                                                           event.y())
            
            dx = x - self.__x0
            dy = y - self.__y0
            radius = math.sqrt( pow(dx,2) + pow(dy,2) )
            w = radius * 2.0
            h = radius * 2.0
            xc = self.__x0 - radius
            yc = self.__y0 - radius
            self.__radius = radius
            self.__rectCoord.setRect(xc, yc, w, h)
            self.viewportUpdate()
            
    def mouseRelease(self, event):
        """
        Rectangle selection is finished, send corresponding signal
        with coordinates
        """
        self.emit(qt.PYSIGNAL("DiscSelected"), 
                  (self.__x0, self.__y0, self.__radius))
        
        self.viewportUpdate()
        
    def viewportUpdate(self):
        """
        Draw Disc either if qubImage pixmap has been updated or
        rectangle coordinates have been changed by the user
        """
        rect = self._qubImage.matrix().map(self.__rectCoord)
        (x,y) = self._qubImage.matrix().map(self.__x0, self.__y0)

        self.__disc.setSize(rect.width(), rect.height())
        self.__disc.move(x, y)
        
        self.__disc.update()            



###############################################################################
####################            QubZoomListAction          ####################
###############################################################################
class QubZoomListAction(QubAction):
    """
    This class add a zoom facility for QubImageView as a list of zoom factor:
    keepROI .. : keep the ROI of the zoom
    zoomValList : list of zoom , be default zoom list is [0.1, 0.25, 0.5, 0.75, 1, 2, 3, 4, 5]
    initZoom : zoom value at init
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        Initialyse variables
        """
        QubAction.__init__(self, *args, **keys)

        self._zoomValList = keys.get("zoomValList",[0.1, 0.25, 0.5, 0.75, 1, 2, 3, 4, 5])
        self._initZoom = keys.get('initZoom',1)
        
        self._keepROI = keys.get("keepROI",False)

        self._zoomVal = 1

        self._item = None
        
        self._qubImage = None

        self._listPopupMenu = None
        
    def viewConnect(self, qubImage):
        """
        connect actio0n with the QubImage object on which it will be applied
        """
        self._qubImage = qubImage
              
    def changeZoomList(self,zoomValList,defaultzoom) :
        """
        zoomValList : list of zoom
        initZoom : zoom vlaue at init
        """
        self._zoomValList = zoomValList[:]
        self._initZoom = defaultzoom
        if self._listPopupMenu is not None :
            self._listPopupMenu,idDefaultZoom = self._createPopMenu(self._listPopupMenu.parentWidget())
            self._widget.setPopup(self._listPopupMenu)
            self._widget.setText(qt.QString('%d%%' % int(self._zoomValList[idDefaultZoom] * 100)))
            
    def setZoomOnFullImage(self,flag) :
        if self._keepROI == flag :
            self._keepROI = not flag
            if self._qubImage is not None :
                self._qubImage.setZoom(self._zoomVal, self._zoomVal,self._keepROI)

    def addToolWidget(self, parent):
        """
        Creates widgets to be added in the toolbar
        """

        """
        menu to select zoom value
        """
        self._listPopupMenu,idDefaultZoom = self._createPopMenu(parent)
        """
        tool button to use selected zoom value
        """
        self._widget = qt.QToolButton(parent)
        self._widget.setAutoRaise(True)
        self._widget.setPopup(self._listPopupMenu)
        self._widget.setPopupDelay(0)
        self._widget.setText(qt.QString('%d%%' % int(self._zoomValList[idDefaultZoom] * 100)))
        
        qt.QToolTip.add(self._widget, "Zoom List")
                                     
        return self._widget
        
    def addMenuWidget(self, menu):
        self._menu = menu
        
        if self._item is None:
            qstr = qt.QString("%d%%"%(int(self._zoomVal*100)))
            self._item = menu.insertItem(qstr, self._listPopupMenu)
            menu.connectItem(self._item, self._listPopupMenu.exec_loop)

    def _createPopMenu(self,parent) :
        popMenu = qt.QPopupMenu(parent)
        idDefaultZoom = 0
        for i,zoomVal in enumerate(self._zoomValList) :
            popMenu.insertItem('%d%%' % int(zoomVal * 100), i)
            if zoomVal == self._initZoom :
                idDefaultZoom = i
        self.connect(popMenu, qt.SIGNAL("activated(int )"),
                     self._applyZoomFromList)
        return (popMenu,idDefaultZoom)
 
    def _applyZoomFromList(self, index):
            """
            Calculate zoom value from array
            """        
            try:
                self._applyZoom(self._zoomValList[index])
            except :
                traceback.print_exc()
    
    def _applyZoom(self, zoomVal):
        if self._qubImage is not None:
            """
            set wait cursor as changing zoom factor could take some times
            """
            self._qubImage.setCursor(qt.QCursor(qt.Qt.WaitCursor))

            """
             zoom value
            """
            self._zoomVal = zoomVal

            """
            update zoom value as percentage in toolbar and menu widget
            """   
            self.writeStrValue("%d%%"%(int(self._zoomVal*100)))    

            """
            calculate and display new pixmap not centered
            """
            self._qubImage.setZoom(self._zoomVal, self._zoomVal,self._keepROI)
            """
            restore cursor
            """
            self._qubImage.setCursor(qt.QCursor(qt.Qt.ArrowCursor))
    
    def writeStrValue(self, strVal):
            """
            update zoom value in toolbar and menu widget
            """        
            qstr = qt.QString(strVal)
            self._widget.setText(qstr)
            if self._item is not None:
                self._menu.changeItem(self._item, qstr)

###############################################################################
####################              QubZoomAction            ####################
###############################################################################
class QubZoomAction(QubAction):
    """
    This class add a zoom facility for QubImageView as a list:
        + fit to screen (keep image ratio)
        + fill screen (do not keep image ratio)
    This action can be linked to a ZoomListAction object in order to
    see the exact value of the zoom. Use "setList" method with the
    ZoomListAction object as parameter to do that
    """
    def __init__(self, *args, **keys):
        """
        Constructor method
        Initialyse variables
        """
        QubAction.__init__(self, *args, **keys)
        
        self._selIndex = 0
        self._selName  = "Fit2Screen"
        
        self._toolName = ["Fit2Screen", "FillScreen"]
        self._toolIcon = {}
        self._toolIcon["Fit2Screen"] = qt.QIconSet(loadIcon("zfit.png"))
        self._toolIcon["FillScreen"] = qt.QIconSet(loadIcon("zfill.png"))
        
        self._item = None
        self._qubImage = None
        self._sigConnected = False
        self._name = "Zoom tools"
                
    def viewConnect(self, qubImage):
        """
        connect action with the QubImage object on which it will be applied
        """
        self._qubImage = qubImage
        
    def addToolWidget(self, parent):
        """
        Creates widgets to be added in the toolbar
        """

        """
        menu to select zoom tool
        """
        self._toolPopupMenu = qt.QPopupMenu(parent)
        for i in range(len(self._toolName)):
            self._toolPopupMenu.insertItem(self._toolIcon[self._toolName[i]],
                                           qt.QString(self._toolName[i]),i)
        self.connect(self._toolPopupMenu, qt.SIGNAL("activated(int )"),
                        self._selectToolFromList)
        
        """
        ToolButton to set or not selected zoom tool
        """
        self._widget = qt.QToolButton(parent, "%s"%self._name)
        self._widget.setIconSet(self._toolIcon[self._selName])
        self._widget.setAutoRaise(True)
        self._widget.setToggleButton(True)
        self._widget.setPopup(self._toolPopupMenu)
        self._widget.setPopupDelay(0)
        self.connect(self._widget, qt.SIGNAL("toggled(bool)"),self.setState)
        qt.QToolTip.add(self._widget, "%s"%self._name)

        return self._widget
        
    def addMenuWidget(self, menu):
        self._menu = menu
        
        if self._item is None:
            icon = self._toolIcon[self._selName]
            self._item = menu.insertItem(icon, qt.QString(self._selName),
                                         self._toolPopupMenu)
            menu.connectItem(self._item, self._toolPopupMenu.exec_loop)
                
    def setState(self, state):
        """
        "state" is True or False.
        Set toolbar, contextmenu or statusbar widgets of the action to
        the "state" value.
        Call the internal method _setState which manage the behavior.
        """
        if self._widget is not None:
            self._widget.setOn(state)
        
        if self._item is not None:
            self._menu.setItemChecked(self._item, state)
        
        self._setState(state)
        
    def _setState(self, state):
        """
        manage behavior of the action toolbutton according to the "state" value
        """
        self.__state = state
        
        if self._qubImage is not None:
            if state:
                self._qubImage.setScrollbarMode(self._selName)
                
                """
                update zoom value on the ZoomListAction  object if needed
                and link update zoom value to the view resize event
                """
                if self._listAction is not None:
                    self._updateZoomValue()
                    
                    if self._selName == "Fit2Screen":
                        if self._sigConnected == False:
                            self.connect(self._qubImage,
                                         qt.PYSIGNAL("ViewportResized"),
                                         self._updateZoomValue)
                            self._sigConnected = True
                    else:
                        if self._sigConnected == True:
                            self.disconnect(self._qubImage,
                                            qt.PYSIGNAL("ViewportResized"),
                                            self._updateZoomValue)
                            self._sigConnected = False
            else:
                self._qubImage.setScrollbarMode("Auto")

                if self._sigConnected == True:
                    self.disconnect(self._qubImage,
                                    qt.PYSIGNAL("ViewportResized"),
                                    self._updateZoomValue)
                    self._sigConnected = False
                

        
    def _selectToolFromList(self, index):
        """
        change zoom tool
        set it to on automatically
        """
        self._selIndex = index
        self._selName = self._toolName[index]
        
        if self._widget is not None:                
            self._widget.setIconSet(self._toolIcon[self._selName])
            if self._item is not None:
                self._menu.changeItem(self._item, self._toolIcon[self._selName],
                                      qt.QString(self._selName))
            
            self.setState(1)
        
    def setList(self, listAction):
        self._listAction = listAction
        
    def _updateZoomValue(self):
        """
        when a new zoom tool is selected or when image view is resized,
        update zoom value in the ZoomStrListAction object if necessary
        """
        if self._listAction is not None:
            (zoomx, zoomy) = self._qubImage.zoom()
            if zoomx == zoomy:
                strVal = "%d%%"%(int(zoomx*100))
            else:
                strVal = "???"
                    
            self._listAction.writeStrValue(strVal)
        


###############################################################################
####################        QubForegroundColorAction       ####################
###############################################################################
class QubForegroundColorAction(QubAction):
    """
    This action allow to select a color.
    When the color is selected, it call the "setForegroundColor" method of
    the "view()" to wich it is connected.
    """
    def __init__(self, view =None, *args, **keys):
        """
        Constructor method
        name ... :  string name of the action
        view ... :  action will act on the "view()" object of a QubView.
                    the view can be set in the constructor method or using
                    the "viewConnect" method of the class 
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None)
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it
        index .. :  Position of the selection widget of the action in its
                    group
        """
        QubAction.__init__(self, *args, **keys)
        
        self._view = None
        
        self._colorMenu = None
        
        if view is not None:
            self.viewConnect(view)

    def viewConnect(self, view):
        """
        reference the "QubView.view()" object in order to its
        "setForegroundColor" method
        """
        self._view = view
       
    def addToolWidget(self, parent):
        """
        Creates action widget to put in "group" dockarea of the "toolbar"
        Return this widget.
        """
        if self._widget is None:
            self._widget = QubColorToolButton(parent)
            self.connect(self._widget, qt.PYSIGNAL("colorSelected"),
                         self.colorChanged)
            qt.QToolTip.add(self._widget, "change color pen for selections")
        
        return self._widget
             
    def addMenuWidget(self, menu):
        """
        This method should be reimplemented.
        Creates item in contextmenu "menu" for the action.
        """
        self._menu = menu
        
        if self._item is None:
            if self._colorMenu is None:
                self._colorMenu = QubColorToolMenu(menu)
                self.connect(self._colorMenu, qt.PYSIGNAL("colorSelected"),
                             self.colorChanged)
                    
            self._item = menu.insertItem(self._colorMenu.iconSet,
                                         qt.QString("Color"), self._colorMenu)
            menu.connectItem(self._item, self._colorMenu.exec_loop)

    def colorChanged(self, color):
        if self._view is not None:
            self._view.setForegroundColor(color)
        
        if self._item is not None:
            self._menu.changeItem(self._item, self._colorMenu.iconSet,
                                  qt.QString("Color"))
                                  
    def setColor(self, color="Black"):
        try:
            qcolor = qt.QColor(color)
        except:
            print "Color %s does not exist"%color
        else:
            if self._widget is not None:
                self._widget.setColor(qcolor)
            
            if self._item is not None:
                self._colorMenu.setColor(qcolor)
                
            if self._view is not None:
                self._view.setForegroundColor(qcolor)
                                                  
####################################################################
##########                                                ##########
##########                 QubPositionAction               ##########
##########                                                ##########
####################################################################
class QubPositionAction(QubImageAction):
    def __init__(self, *args, **keys):
        QubImageAction.__init__(self, autoConnect=True, *args, **keys)
        
    def addStatusWidget(self, parent):
        if self._widget is None:
            self._widget = qt.QWidget(parent)
            
            hlayout = qt.QHBoxLayout(self._widget)

            xlabel = qt.QLabel("X:", self._widget)
            hlayout.addWidget(xlabel)
            
            self.xLabel = qt.QLabel("xxxx.xx", self._widget)
            font = self.xLabel.font()
            font.setBold(True)
            self.xLabel.setFont(font)
            minsize = self.xLabel.sizeHint()
            self.xLabel.setMinimumSize(minsize)
            hlayout.addWidget(self.xLabel)
            
            hlayout.addSpacing(5)
                   
            ylabel = qt.QLabel("Y:", self._widget)
            hlayout.addWidget(ylabel)
            
            self.yLabel = qt.QLabel(" ", self._widget)
            self.yLabel.setFont(font)
            self.yLabel.setMinimumSize(minsize)
            hlayout.addWidget(self.yLabel)
                        
        return self._widget
        
    def mouseMove(self, event):
        (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), 
                                                         event.y())
    
        self.xLabel.setText(str(x))
        self.yLabel.setText(str(y))
        
        
####################################################################
##########                                                ##########
##########                 QubBeamAction                  ##########
##########                                                ##########
####################################################################
class QubBeamAction(QubToggleImageAction):
    def __init__(self, *args, **keys):
        QubToggleImageAction.__init__(self, *args, **keys)

        self.__center = qt.QPoint(0,0)

        self._name = "beam"
        self.__state = False
        self.__onMove = False
        
    def viewConnect(self, qubImage):
        """
        Once the qubImage is connected, create QCanvas Item
        """
        QubToggleImageAction.viewConnect(self, qubImage)

        self.__centerE = QubCanvasEllipse(7,7,0,5760,self._qubImage.canvas())
        self.__roundE = QubCanvasEllipse(29,19,0,5760, self._qubImage.canvas())

        self.setColor(self._qubImage.foregroundColor())
        self.signalConnect(self._qubImage)

    def setColor(self, color):
        """   
        Slot connected to "ForegroundColorChanged" "qubImage" signal
        """
        self.__centerE.setPen(qt.QPen(color))
        self.__roundE.setPen(qt.QPen(color))
        
        self.__centerE.update()
        self.__roundE.update()
       
    def _setState(self, aFlag):
        """
        Draw or Hide the 2 ellipse canvas items
        """
        self.__state = aFlag

        if self.__centerE is not None and self.__roundE is not None:
            if self.__state:
                self.setColor(self._qubImage.foregroundColor())
                self.__centerE.show()
                self.__roundE.show()
            else:
                self.__centerE.hide()
                self.__roundE.hide()
            
            self.__centerE.update()
            self.__roundE.update()

    def setBeamPosition(self, y, z):
        self.__center.setX(y)
        self.__center.setY(z)
        self.viewportUpdate()
        
    def mousePress(self, event):
        """
        Update upper-left corner position of the rectangle and sets its
        width and height to 1
        """
        if self.__state and event.button() == qt.Qt.LeftButton:
            (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), event.y())

            if self.inBeam(x, y):
                self.__onMove = True
                self.__center.setX(x)
                self.__center.setY(y)

                self.viewportUpdate()
    
    def mouseMove(self, event):
        if self.__state and self.__onMove and event.state() == qt.Qt.LeftButton :
            (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), 
                                                           event.y())
            self.__center.setX(x)
            self.__center.setY(y)
        
            self.viewportUpdate()
    
    def mouseRelease(self, event):
        if self.__state and event.state() == qt.Qt.LeftButton :
            if self.__onMove :
                (x, y) = self._qubImage.matrix().invert()[0].map(event.x(), 
                                                               event.y())
                self.__center.setX(x)
                self.__center.setY(y)

                self.emit(qt.PYSIGNAL("BeamSelected"), (x, y))

                self.viewportUpdate()
            self.__onMove = False
            
    def viewportUpdate(self):
        point = self._qubImage.matrix().map(self.__center)
                
        self.__centerE.move(point.x(), point.y())  
        self.__roundE.move(point.x(), point.y())  

    def inBeam(self, x, y):
        cenx = self.__center.x()
        ceny = self.__center.y()
        
        if (x >= cenx - 14 and x <= cenx + 14) and \
           (y >= ceny - 9  and y <= ceny + 9):
           return True
           
        return False
        
####################################################################
##########                                                ##########
##########            QubHidePointSelection               ##########
##########                                                ##########
####################################################################
class QubHidePointSelection(QubPointSelection):
    def __init__(self, *args, **keys):
        QubPointSelection.__init__(self, *args, **keys)
        
    def addToolWidget(self, parent):        
        return None
        
    def addMenuWidget(self, menu):
        pass
        
    def addStatusWidget(self, parent):
        return None
       
    def menuChecked(self):
        pass        
            
    def setState(self, state):        
        self._setState(state)
        
####################################################################
##########                                                ##########
##########          QubHideRectangleSelection             ##########
##########                                                ##########
####################################################################
class QubHideRectangleSelection(QubRectangleSelection):
    def __init__(self, *args, **keys):
        QubRectangleSelection.__init__(self, *args, **keys)
   
    def addToolWidget(self, parent):
        return None
        
    def addMenuWidget(self, menu):
        pass
        
    def addStatusWidget(self, parent):
        return None
       
    def menuChecked(self):
        pass        
            
    def setState(self, state):        
        self._setState(state)
                   
#####################################################################
##########                  QubScaleAction                 ##########
#####################################################################
class QubScaleAction(QubToggleImageAction) :
    HORIZONTAL,VERTICAL,BOTH = (0x1,0x2,0x3)
    def __init__(self,*args,**keys) :
        QubToggleImageAction.__init__(self,*args,**keys)
        self.__xPixelSize = 0
        self.__yPixelSize = 0
        self.__mode = keys.get("mode",QubScaleAction.BOTH)
        self.__unit = [(1e-3,'m'),(1e-6,'u'),(1e-9,'n')]
        self.__autorizeValues = keys.get('authorized_values',[1,2,5,10,20,50,100,200,500])

        self.__hLine = None
        self.__hText = None
        self.__vLine = None
        self.__vText = None
        self.__state = False
        
    def viewConnect(self, qubImage):
        QubToggleImageAction.viewConnect(self,qubImage)
        color = qt.QColor('green')
        self.__hLine = qtcanvas.QCanvasLine(qubImage.canvas())
        self.__hLine.setPen(qt.QPen(color,4))
        self.__hText = qtcanvas.QCanvasText(qubImage.canvas())
        self.__hText.setColor(color)
        
        self.__vLine = qtcanvas.QCanvasLine(qubImage.canvas())
        self.__vLine.setPen(qt.QPen(color,4))
        self.__vText = qtcanvas.QCanvasText(qubImage.canvas())
        self.__vText.setColor(color)

        self.viewportUpdate()
        
    def setXPixelSize(self,size) :
        self.__xPixelSize = abs(size)
        if(self.__state and self.__mode & QubScaleAction.HORIZONTAL and
           self.__xPixelSize is not None and self.__xPixelSize) :
            self.viewportUpdate()
            self.__hText.show()
            self.__hLine.show()
        else:
            self.__hText.hide()
            self.__hLine.hide()
            
    def setYPixelSize(self,size) :
        self.__yPixelSize = abs(size)
        if (self.__state and self.__mode & QubScaleAction.VERTICAL and
            self.__yPixelSize is not None and self.__yPixelSize) :
            self.__vText.show()
            self.__vLine.show()
            self.viewportUpdate()
        else :
            self.__vText.hide()
            self.__vLine.hide()
 
        
    def viewportUpdate(self) :
        if self.__state and self._qubImage is not None :
            (canvasX,canvasY) = (self._qubImage.canvas().width(),self._qubImage.canvas().height())
            (viewSizeX,viewSizeY) = (self._qubImage.visibleWidth(),self._qubImage.visibleHeight())
            (nbXPixel,nbYPixel) =  min(canvasX,viewSizeX),min(canvasY,viewSizeY)
            (widthUse,heightUse) = (nbXPixel,nbYPixel)
            (xOriCrop,yOriCrop) = self._qubImage.matrix().invert()[0].map(0,0)
            (xOri,yOri) = (self._qubImage.contentsX(),self._qubImage.contentsY())
                
            if self.__mode & QubScaleAction.HORIZONTAL :
                nbXPixel /= 4 # 1/4 of image display
                dummy,y1 = self._qubImage.matrix().invert()[0].map(0,0)
                dummy,y2 = self._qubImage.matrix().invert()[0].map(0,nbXPixel)
                unit,XSize = self.__getUnitNAuthValue((y2 - y1) * self.__xPixelSize)
                try:
                    nbXPixel = int(XSize * unit[0] / self.__xPixelSize)
                    (nbXPixel,dummy) = self._qubImage.matrix().map(nbXPixel + xOriCrop,0)
                    y0 = heightUse - 10 + yOri
                    self.__hLine.setPoints (14 + xOri,y0,nbXPixel + 14 + xOri,y0)
                    self.__hText.setText('%d %s' % (XSize,unit[1]))
                    rect = self.__hText.boundingRect()
                    xTextPos = nbXPixel + 14 - rect.width()
                    if xTextPos < 14 :
                        self.__hText.move(nbXPixel + 16 + xOri,y0 - rect.height() / 2)
                    else:
                        self.__hText.move(xTextPos + xOri,y0 - 20)
                except:
                    pass
                
            if self.__mode & QubScaleAction.VERTICAL :
                nbYPixel /= 4
                dummy,y1 = self._qubImage.matrix().invert()[0].map(0,0)
                dummy,y2 = self._qubImage.matrix().invert()[0].map(0,nbYPixel)
                unit,YSize = self.__getUnitNAuthValue((y2 - y1) * self.__yPixelSize)
                try:
                    nbYPixel = int(YSize * unit[0] / self.__yPixelSize)
                    (dummy,nbYPixel) = self._qubImage.matrix().map(0,nbYPixel + yOriCrop)
                    y0 = heightUse - 14 + yOri
                    self.__vLine.setPoints(10 + xOri,y0,10 + xOri,y0 - nbYPixel)
                    self.__vText.move(15 + xOri,y0 - nbYPixel)
                    self.__vText.setText('%d %s' % (YSize,unit[1]))
                except :
                    pass

            if self.__mode & QubScaleAction.BOTH :
                hRect = self.__hText.boundingRect()
                vRect = self.__vText.boundingRect()
                
                vPoint = vRect.bottomRight()
                hPoint = hRect.topLeft()
                if hPoint.y() - vPoint.y() < 5 :
                    hLinePoint = self.__hLine.endPoint()
                    self.__hText.move(hLinePoint.x() + 2,hLinePoint.y() - hRect.height() / 2)

                    vLinePoint = self.__vLine.endPoint()
                    vTextRect = self.__vText.boundingRect()
                    self.__vText.move(vLinePoint.x() - 4,vLinePoint.y() - vTextRect.height())
            
                    
    def _setState(self,aFlag) :
        self.__state = aFlag
        if aFlag :
            self.viewportUpdate()
            self.signalConnect(self._qubImage)
            if self.__mode & QubScaleAction.HORIZONTAL and self.__xPixelSize is not None and self.__xPixelSize :
                self.__hText.show()
                self.__hLine.show()
            if self.__mode & QubScaleAction.VERTICAL and self.__yPixelSize is not None and self.__yPixelSize :
                self.__vText.show()
                self.__vLine.show()
        else :
            self.signalDisconnect(self._qubImage)
            self.__hText.hide()
            self.__hLine.hide()
            self.__vText.hide()
            self.__vLine.hide()
    
    def __getUnitNAuthValue(self,size) :
        for unit in self.__unit :
                tmpSize = size / unit[0]
                if 1. < tmpSize < 1000. :
                    size = int(tmpSize)
                    aFindFlag = False
                    for i,autValue in enumerate(self.__autorizeValues) :
                        if size < autValue :
                            if i > 0 :
                                size = self.__autorizeValues[i - 1]
                            else :
                                size = autValue
                            aFindFlag = True
                            break
                        elif size == autValue:
                            aFindFlag = True
                            break
                    if not aFindFlag :
                        size = autValue
                    break
        return (unit,size)

####################################################################
##########                                                ##########
##########              QubOpenSaveDialogAction           ##########
##########                                                ##########
####################################################################
class QubOpenDialogAction(QubAction):
    """
    This action will allow to open a dialog 
    """
    def __init__(self,*args, **keys):
        """
        Constructor method
        name ... :  string name of the action.
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None).
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu.
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it.
        index .. :  Position of the selection widget of the action in its
                    group.
        """
        QubAction.__init__(self, *args, **keys)

        self.__dialog = None
        self._label = keys.get('label',self._name)
        self.__iconName = keys.get('iconName','fileopen')
        
    def addToolWidget(self, parent):
        """
        create save pushbutton in the toolbar of the view
        create the save dialog if not already done
        """
        
        """
        create widget for the view toolbar
        """   
        if self._widget is None:
            self._widget = qt.QToolButton(parent,self._name)
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("%s.png" % self.__iconName)))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                            self.__showSaveDialog)
            qt.QToolTip.add(self._widget,self._label)

        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        self._menu = menu
        iconSet = qt.QIconSet(loadIcon("%s.png" % self.__iconName))
        self._item = menu.insertItem(iconSet, qt.QString(self._label),
                                      self.__showSaveDialog)
        
    def setDialog(self,dialog) :
        """ Interface to manage the dialogue window.
        this interface must have the methode :
             -> show()
             -> refresh()
        """
        self.__dialog = dialog
        
    def __showSaveDialog(self):
        if self.__dialog is not None :
            self.__dialog.show()
            self.__dialog.raiseW()
            if hasattr(self.__dialog, "refresh"):
                self.__dialog.refresh()

####################################################################
##########                                                ##########
##########            QubBrightnessContrastAction         ##########
##########                                                ##########
####################################################################
class QubBrightnessContrastAction(QubAction):
    """
    This action will allow to open a dialog 
    """
    def __init__(self,*args, **keys):
        from Qub.Widget.QubDialog import QubBrightnessContrastDialog
        
        """
        Constructor method
        name ... :  string name of the action.
        place .. :  where to put in the view widget, the selection widget
                    of the action ("toolbar", "statusbar", None).
        show ... :  If in view toolbar, tells to put it in the toolbar
                    itself or in the context menu.
        group .. :  actions may grouped. Tells the name of the group the
                    action belongs to. If not present, a "misc." group is
                    automatically created and the action is added to it.
        index .. :  Position of the selection widget of the action in its
                    group.
        """
        QubAction.__init__(self, *args, **keys)

        self.__dialog = QubBrightnessContrastDialog(None)
        self._label = keys.get('label',self._name)
        self.__iconName = keys.get('iconName','bright-cont')
        
    def addToolWidget(self, parent):
        """
        create save pushbutton in the toolbar of the view
        create the save dialog if not already done
        """
        
        """
        create widget for the view toolbar
        """   
        if self._widget is None:
            self._widget = qt.QToolButton(parent,self._name)
            self._widget.setAutoRaise(True)
            self._widget.setIconSet(qt.QIconSet(loadIcon("%s.png" % self.__iconName)))
            self._widget.connect(self._widget, qt.SIGNAL("clicked()"),
                            self.__showDialog)
            qt.QToolTip.add(self._widget,self._label)

        return self._widget
        
    def addMenuWidget(self, menu):
        """
        Create context menu item pushbutton
        """
        self._menu = menu
        iconSet = qt.QIconSet(loadIcon("%s.png" % self.__iconName))
        self._item = menu.insertItem(iconSet, qt.QString(self._label),
                                      self.__showSaveDialog)
                
    def __showDialog(self):
        if self.__dialog is not None :
            self.__dialog.show()
            self.__dialog.raiseW()

    def setCamera(self, camera):
        self.__dialog.setCamera(camera)
                
################################################################################
####################    TEST -- QubViewActionTest -- TEST   ####################
################################################################################
class QubMain(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        self.colormapSps = [spslut.GREYSCALE, spslut.REVERSEGREY, spslut.TEMP,
                            spslut.RED, spslut.GREEN, spslut.BLUE, spslut.MANY]
        #pixmap = qt.QPixmap(file)
        self.readEdfFile(file)
        self.colormap = 0
        self.colorMin = self.dataMin
        self.colorMax = self.dataMax
        self.autoscale = 0
        
        actions = []
        
        # A1
        action = QubColormapAction(show=1, group="color")
        actions.append(action)
        
        action.setParam(self.colormap, self.colorMin, self.colorMax,
                        self.dataMin, self.dataMax, self.autoscale)
        self.connect(action, qt.PYSIGNAL("ColormapChanged"),
                        self.colormapChanged)
        
        action = QubForegroundColorAction(name="Foreground", group="color")
        actions.append(action)
        
        action = QubSeparatorAction(name="sep1", show=1, group="admin")
        actions.append(action)

        action = QubPrintPreviewAction(name="PP", show=1, group="admin")
        actions.append(action)
        
        # A2
        action = QubHLineSelection(show=1, group="selection")
        actions.append(action)

        action = QubVLineSelection(show=1, group="selection")
        actions.append(action)

        action = QubLineSelection(show=1, group="selection")
        actions.append(action)

        action = QubRectangleSelection(show=1, group="selection")
        actions.append(action)

        action = QubPointSelection(show=1, group="selection")
        actions.append(action)

        action = QubCircleSelection(show=1, group="selection")
        actions.append(action)

        action = QubSeparatorAction(name="sep2", show=1, group="selection")
        actions.append(action)

        action = QubDiscSelection(show=1, group="selection")
        actions.append(action)

        # A3
        action1 = QubZoomAction(show=1, group="zoom")
        actions.append(action1)
        
        action = QubZoomListAction(show=1, group="zoom")
        actions.append(action)
        
        action1.setList(action)
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
    
        self.qubImage = QubImageView(container, "actions", None, actions)
        
        hlayout.addWidget(self.qubImage)
        self.updatePixmap()
    
        self.setCentralWidget(container)

    def colormapChanged(self, colormap, autoscale, colorMin, colorMax):
        print "ColormapChanged (TEST)"
        self.colormap  = colormap
        self.autoscale = autoscale
        self.colorMin  = colorMin
        self.colorMax  = colorMax
        self.updatePixmap()
        
    def updatePixmap(self):
        (image_str, size, minmax) = spslut.transform(self.data ,
                                               (1,0), 
                                               (spslut.LINEAR, 3.0),
                                               "BGRX", 
                                               self.colormapSps[self.colormap],
                                               self.autoscale, 
                                               (self.colorMin, self.colorMax))
        image = qt.QImage(image_str, size[0], size[1], 32, None, 0,
                          qt.QImage.IgnoreEndian)
        pixmap = qt.QPixmap()
        pixmap.convertFromImage(image)         	      
        
        if self.qubImage is not None:
            self.qubImage.setPixmap(pixmap)       
        
    def readEdfFile(self, file):    
        edf = EdfFile.EdfFile(file)
        self.data = edf.GetData(0)
        self.dataMin = min(Numeric.ravel(self.data))
        self.dataMax = max(Numeric.ravel(self.data))

                       
##  MAIN   
if  __name__ == '__main__':
    from Qub.Widget.QubImageView import QubImageView
    import EdfFile
    import Numeric
    import spslut
    
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    if len(sys.argv) < 2:
        print "Usage to test : QubActionSet.py file.edf"
        sys.exit()

    window = QubMain(None, file = sys.argv[1])
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
