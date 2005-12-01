import qt
import sys
import os
import Numeric

from Qub.Icons.QubIcons import loadIcon
from Qub.Widget.QubImage import QubImage
from Qub.Widget.QubGraph import QubGraph
from Qub.Widget.QubAction import QubAction

        
################################################################################
####################                QubAction               ####################
################################################################################
class QubColormapDialog(qt.QDialog):
    """
    Creates a dialog box to change a colormap.
    It allows to change colormaps (Greyscale, Reverse Grey, Temperature,
    Red, Green, Blue, Many) and the mapping on the selected colormap of
    the min and max value of the data. it also allows to set the colormap in
    autoscale mode or not.
    When any of these parameters change, the signal "ColormapChanged" is
    sent with the parameters colormap, autoscale, minValue, maxValue
    """
    def __init__(self, parent=None, name=None):
        """
        Constructor method
        Create the layout of the colormap dialog widget using default value
        """
        qt.QDialog.__init__(self, parent)
        
        self.parent = parent

        self.colormap = 0
        self.colormapList = ["Greyscale", "Reverse Grey", "Temperature",
                                 "Red", "Green", "Blue", "Many"]
        self.colormapSps = [spslut.GREYSCALE, spslut.REVERSEGREY, spslut.TEMP,
                             spslut.RED, spslut.GREEN, spslut.BLUE, spslut.MANY]

                         
        parentName = self.parent.name()
        file  = os.path.basename(parentName)
        self.title = "COLORMAP for " + file
        self.setCaption(self.title)

        """
        default values
        """
        self.dataMin   = 0
        self.dataMax   = 199
        self.minValue  = 50
        self.maxValue  = 150

        self.autoscale   = False
        self.autoscale90 = False

        self.colormapData = Numeric.resize(Numeric.arange(200), (50,200))
        """
        main layout (VERTICAL)
        """
        vlayout = qt.QVBoxLayout(self, 0, -1, "Main ColormapDialog Layout")
        vlayout.setMargin(10)
        vlayout.setSpacing(10)

        """
        layout 1 (HORIZONTAL)
            - combo for colormap names
            - QubImage to view chosen colormap
        """
        hlayout1 = qt.QHBoxLayout(vlayout, -1, "layout 1")
        hlayout1.setSpacing(10)

        """
        combo for colormap names
        """
        self.colormapCombo = qt.QComboBox(self)
        for colormap in self.colormapList:
            self.colormapCombo.insertItem(colormap)
        self.connect(self.colormapCombo, qt.SIGNAL("activated(int)"),
                     self.colormapChanged)
        hlayout1.addWidget(self.colormapCombo)

        """
        QubImage to view chosen colormap
        """
        self.colormapImage = QubImage(self)
        self.colormapImage.setScrollbarMode("FullScreen")
        self.colormapImage.setMinimumHeight(2*self.colormapCombo.sizeHint().height())
        hlayout1.addWidget(self.colormapImage)
        
        self._updateColormap()
        
        """
        layout 2 (HORIZONTAL)
            - min value label
            - min value text
        """
        hlayout2 = qt.QHBoxLayout(vlayout, -1, "layout 2")
        hlayout2.setSpacing(10)

        """
        min value label
        """
        self.minLabel  = qt.QLabel(self)
        self.minLabel.setText("Minimum")
        hlayout2.addWidget(self.minLabel)
        
        """
        min label text
        """
        hlayout2.addSpacing(5)
        hlayout2.addStretch(1)
        self.minText  = qt.QLineEdit(self)
        self.minText.setFixedWidth(150)
        self.minText.setAlignment(qt.Qt.AlignRight)
        self.connect(self.minText, qt.SIGNAL("returnPressed()"),
                     self.minTextChanged)
        hlayout2.addWidget(self.minText)
        
        """
        layout 3 (HORIZONTAL)
            - max value label
            - max value text
        """
        hlayout3 = qt.QHBoxLayout(vlayout, -1, "layout 3")
        hlayout3.setSpacing(10)

        """
        max value label
        """
        self.maxLabel  = qt.QLabel(self)
        self.maxLabel.setText("Maximum")
        hlayout3.addWidget(self.maxLabel)
        
        """
        max label text
        """
        hlayout3.addSpacing(5)
        hlayout3.addStretch(1)
        self.maxText  = qt.QLineEdit(self)
        self.maxText.setFixedWidth(150)
        self.maxText.setAlignment(qt.Qt.AlignRight)
        self.connect(self.maxText, qt.SIGNAL("returnPressed()"),
                     self.maxTextChanged)
        hlayout3.addWidget(self.maxText)
        
        """
        hlayout 4 (HORIZONTAL)
            - graph
        """
        hlayout4 = qt.QHBoxLayout(vlayout, -1, "layout 4")
        hlayout4.setSpacing(10)
        
        """
        graph
        """
        self.colormapGraph  = QubGraph(self)
        
        """
        remove Y axis label
        set X axis label
        remove curves legends
        """
        self.colormapGraph.enableYLeftAxis(0)
        self.colormapGraph.setXLabel("Data Values")
        self.colormapGraph.useLegend(False)

        """
        set the curve _/-
        """
        self.colormapGraph.setMarkedCurve( "ConstrainedCurve",
                               [0, 10, 20, 30],
                               [-10, -10, 10, 10 ]
                             )

        self.colormapGraph.setMinimumSize(qt.QSize(250,200))

        self.connect (self.colormapGraph , qt.PYSIGNAL("PointMoved"),
                      self._graphMove)
        self.connect (self.colormapGraph , qt.PYSIGNAL("PointReleased"),
                      self._graphRelease)

        hlayout4.addWidget(self.colormapGraph)
        
        """
        hlayout 5 (HORIZONTAL)
            - autoscale
            - scale 90%
            - full scale
        """
        hlayout5 = qt.QHBoxLayout(vlayout, -1, "layout 5")
        hlayout5.setSpacing(10)
        
        """
        autoscale
        """
        self.autoscaleToggle = qt.QPushButton("Autoscale", self)
        self.autoscaleToggle.setToggleButton(True)
        self.connect(self.autoscaleToggle, qt.SIGNAL("toggled(bool)"),
                     self.autoscaleChanged)
        hlayout5.addWidget(self.autoscaleToggle)

        """
        scale 90%
        """
        self.scale90Button = qt.QPushButton("90%", self)
        self.connect(self.scale90Button, qt.SIGNAL("clicked()"),
                     self.scale90Changed)
        hlayout5.addWidget(self.scale90Button)

        """
        full scale
        """
        self.fullscaleButton = qt.QPushButton("Full", self)
        self.connect(self.fullscaleButton, qt.SIGNAL("clicked()"),
                     self.fullscaleChanged)
        hlayout5.addWidget(self.fullscaleButton)

        """
        update dialog with default values
        """
        self._update()
        
        """
        colormap window can not be resized
        """
        self.setFixedSize(vlayout.minimumSize())

    #############################################
    ### COLORMAP
    #############################################
    def colormapChanged(self, colormap):
        """
        type of colormap has changed
            - update the colormap dialog
            - send the "ColormapChanged" signal
        """
        self._setColormap(colormap)
        self._update()
        self._sendColormap()

    def _setColormap(self, colormap):
        """
        set colormap parameter
        """
        self.colormap = colormap

    def _updateColormap(self):
        """
        update the test image
        update the selection in the combo list
        """
        
        """
        update the test image
        """
        self.colormapImage.setPixmap(self._colormapPixmap())
        
        """
        update the selection in the combo
        """
        self.colormapCombo.setCurrentItem(self.colormap)

    def _colormapPixmap(self):
        """
        Build a ixmap with the test image array of the choosen colormap
        """
        (image_str, size, minmax) = spslut.transform(self.colormapData ,
                                        (1,0), 
                                        (spslut.LINEAR, 3.0),
                                        "BGRX", 
                                        self.colormapSps[self.colormap],
                                        1, 
                                        (0, 199))            
        image = qt.QImage(image_str,size[0],size[1],32,None,0,
                          qt.QImage.IgnoreEndian)
        pixmap = qt.QPixmap()
        pixmap.convertFromImage(image)         	      
        return pixmap        


    #############################################
    ### MIN/MAX VALUES
    #############################################
    def minTextChanged(self):
        """
        min value changed
            - update the colormap dialog
            - send the "ColormapChanged" signal
        """
        val = float(str(self.minText.text()))
        
        self._setText(val, self.maxValue)
        self._update()
        self._sendColormap()

    def maxTextChanged(self):
        """
        max value changed
            - update the colormap dialog
            - send the "ColormaChanged" signal
        """
        val = float(str(self.maxText.text()))
        
        self._setText(self.minValue, val)
        self._update()
        self._sendColormap()

    def _setText(self, colorMin, colorMax):
        """
        check and set min/max color parameters
        """
        val = colorMin
        if val > self.dataMax:
            val = self.dataMax
        if val < self.dataMin:
            val = self.dataMin
        
        self.minValue = val
        
        val = colorMax
        if val > self.dataMax:
            val = self.dataMax
        if val < self.dataMin:
            val = self.dataMin
        
        self.maxValue = val
        
    
    def _updateText(self):
        """
        update text widget for min and max values using self.minValue
        and self.maxValue
        """
        self.minText.setText("%g"%self.minValue)
        self.maxText.setText("%g"%self.maxValue)

    #############################################
    ### SCALES
    #############################################
    def autoscaleChanged(self, val):
        """
        autoscale value changed
            - update the colormap dialog
            - send the "ColormaChanged" signal
        """
        self._setAutoscale(val) 
        self._update()
        self._sendColormap()
    
    def _setAutoscale(self, autoscale):
        self.autoscale = autoscale
        if self.autoscale:
            self.minValue = self.dataMin
            self.maxValue = self.dataMax
            
    def _updateAutoscale(self):
        """
        update colormap dialog according to self.autoscale value
        """
        if self.autoscale:
            self.maxText.setEnabled(0)
            self.minText.setEnabled(0)
            self.colormapGraph.setEnabled(0)
            self.scale90Button.setEnabled(0)
            self.fullscaleButton.setEnabled(0)
        else:
            self.maxText.setEnabled(1)
            self.minText.setEnabled(1)
            self.colormapGraph.setEnabled(1)
            self.scale90Button.setEnabled(1)
            self.fullscaleButton.setEnabled(1)
        
    def scale90Changed(self):
        """
        set min value to be the min value of the data and max value to be
        the value corresponding to 90% of the different value of the data
        """
        self.minValue = self.dataMin
        self.maxValue = 0.9 * self.dataMax       
        
        self._update()

        self._sendColormap()

    def fullscaleChanged(self):
        """
        set min/max value of the colormap to the min/max value of the data
        """
        self.minValue = self.dataMin
        self.maxValue = self.dataMax
        
        self._update()
             
        self._sendColormap()
        

    #############################################
    ### GRAPH
    #############################################
    def _graphMove(self, *args):
        """
        user is moving a point given by args[0] to the position given
        by(args[1],args[2])
        """
        (diam , x ,y) = (args[0], args[1], args[2])

        if diam == 2:
            self.minValue = x
        if diam == 3:
            self.maxValue = x
            
        self._update()

    
    def _graphRelease(self, *args):
        """
        user is release mouse on point given by (args[1],args[2]) for
        the point given by args[0]
        This will be the new min or max value for the colormap.
        Send the signal "ColormapChanged"
        """
        (diam , x ,y) = (args[0], args[1], args[2])

        if diam == 2:
            self.minValue = x
        if diam == 3:
            self.maxValue = x
            
        self._update()

        self._sendColormap()
        
    def _updateGraph(self):
        """
        update graph with object values
        """
        
        """
        calculate visible part of the graph outside data values (margin)
        """
        marge = (abs(self.dataMax) + abs(self.dataMin)) / 6.0
        minmd = self.dataMin - marge
        maxpd = self.dataMax + marge
        self.colormapGraph.setZoom(minmd-marge/2, maxpd, -11.5, 11.5)

        """
        tells where points can move:
            first and last : do not move
            second and third: cannot move in Y dir.,can move
                              in X dir. between datamin and datamax
        """ 
        self.colormapGraph.markedCurves["ConstrainedCurve"].defConstraints(
            [(minmd, minmd,   -10, -10 ),
             (self.dataMin, self.dataMax, -10, -10 ),
             (self.dataMin, self.dataMax,  10,  10 ),
             (maxpd, maxpd,    10,  10 )])
             
        """
        move points to their values
        """
        self.colormapGraph.markedCurves["ConstrainedCurve"].deplace(
                                                        0, minmd, -10)
        self.colormapGraph.markedCurves["ConstrainedCurve"].deplace(
                                                        1, self.minValue, -10)
        self.colormapGraph.markedCurves["ConstrainedCurve"].deplace(
                                                        2, self.maxValue, 10)
        self.colormapGraph.markedCurves["ConstrainedCurve"].deplace(
                                                        3, maxpd, 10)
     

    #############################################
    ### GENERAL
    #############################################
    def setParam(colormap=None, colorMin=None, colorMax=None,
                dataMin=None, dataMax=None, autoscale=None):
        """
        set parameters which are not none
        update the colormap dialog
        send "COlormapChanged" signal
        """
        update = 0
        
        if colormap is not None and colormap in range(len(self.colormapList)):
            self._setColormap(colormap)
            update = 1
            
        if colorMin is not None:
            self._setText(colorMin, self.maxValue)
            update = 1
            
        if colorMax is not None:
            self._setText(self.minValue, colorMax)
            update = 1
            
        if dataMin is not None:
            self.dataMin = dataMin
            update = 1
            
        if dataMax is not None:
            self.dataMax = dataMax
            update = 1
            
        if autoscale is not None:
            self._setAutoscale(autoscale)
            update = 1
            
        if update:
            self._update()
            
    def _update(self):
        """
        update all colormap dialog widget with default values
        """
        self._updateColormap()
        self._updateText()
        self._updateAutoscale()
        self._updateGraph()
        
    def _sendColormap(self):
        try:
            if self.parent is not None:                
                self.parent.emit(qt.PYSIGNAL("ColormapChanged"),
                        (self.colormap, self.autoscale,
                         self.minValue, self.maxValue))
        except:
            sys.excepthook(sys.exc_info()[0],
                           sys.exc_info()[1],
                           sys.exc_info()[2])
        
        
        
#    def _update(self):
#        """
#        When any values change in the colormap Dialog, this method
#        update the its visual representation.
#        Should not be used only for values concerning the color graph
#        """
#        self.marge = (abs(self.dataMax) + abs(self.dataMin)) / 6.0
#        self.minmd = self.dataMin - self.marge
#        self.maxpd = self.dataMax + self.marge
#        self.c.setZoom(self.minmd, self.maxpd, -11.5, 11.5)
#
#        self.c.markedCurves["ConstrainedCurve"].defConstraints(
#            [(self.minmd,    self.minmd,   -10, -10 ),
#             (self.dataMin,  self.dataMax, -10, -10 ),
#             (self.dataMin,  self.dataMax,  10,  10 ),
#             (self.maxpd,    self.maxpd,    10,  10 )])
#
#        self.c.markedCurves["ConstrainedCurve"].deplace(0, self.minmd, -10)
#        self.c.markedCurves["ConstrainedCurve"].deplace(3, self.maxpd,  10)
#
#    def chval(self, *args):
#        (diam , x ,y) = (args[0], args[1], args[2])
#
#        if diam == 2:
#            self.setDisplayedMinValue(x)
#        if diam == 3:
#            self.setDisplayedMaxValue(x)
#
#    def chmap(self, *args):
#        (diam , x ,y) = (args[0], args[1], args[2])
#
#        if diam == 2:
#            self.setMinValue(x)
#        if diam == 3:
#            self.setMaxValue(x)
#        
#    """
#    Colormap
#    """
#    def setColormap(self, colormap):
#        self.colormap = colormap
#        self.combo.setCurrentItem(colormap)
#    
#    def colormapChange(self, colormap):
#        self.colormap = colormap
#        self.sendColormap()
#
#    """
#    Autoscale
#    """
#    def autoscaleChange(self, val):
#        self.autoscale = val
#        self.setAutoscale(val)        
#        self.sendColormap()
#
#    def setAutoscale(self, val):
#        if val:
#            self.autoScale90Button.setOn(False)
#            self.setMinValue(self.dataMin)
#            self.setMaxValue(self.dataMax)
#
#            self.maxText.setEnabled(0)
#            self.minText.setEnabled(0)
#            self.c.setEnabled(0)
#        else:
#            self.minText.setEnabled(1)
#            self.maxText.setEnabled(1)
#            self.c.setEnabled(1)
#    """
#    set rangeValues to dataMin ; dataMax-10%
#    """
#    def autoscale90Change(self, val):
#        self.autoscale90 = val
#        self.setAutoscale90(val)
#        self.sendColormap()
#
#    def setAutoscale90(self, val):
#        if val:
#            self.autoScaleButton.setOn(False)
#            self.setMinValue(self.dataMin)
#            self.setMaxValue(self.dataMax - abs(self.dataMax/10))
#
#            self.minText.setEnabled(0)
#            self.maxText.setEnabled(0)
#            self.c.setEnabled(0)
#        else:
#            self.minText.setEnabled(1)
#            self.maxText.setEnabled(1)
#            self.c.setEnabled(1)
#
#
#
#    # MINIMUM
#    """
#    change min value and update colormap
#    """
#    def setMinValue(self, val):
#        v = float(str(val))
#        self.minValue = v
#        self.minText.setText("%g"%v)
#        self.c.markedCurves["ConstrainedCurve"].deplace(1, v, -10)
#        self.sendColormap()
#
#    """
#    min value changed by text
#    """
#    def minTextChanged(self):
#        val = float(str(self.minText.text()))
#        self.setMinValue(val)
#        
#    """
#    change only the displayed min value
#    """
#    def setDisplayedMinValue(self, val):
#        self.minValue = val
#        self.minText.setText("%g"%val)
#
#    # MAXIMUM
#    """
#    change max value and update colormap
#    """
#    def setMaxValue(self, val):
#        v = float(str(val))
#        self.maxValue = v
#        self.maxText.setText("%g"%v)
#        self.c.markedCurves["ConstrainedCurve"].deplace(2, v, 10)
#        self.sendColormap()
#
#    """
#    max value changed by text
#    """
#    def maxTextChanged(self):
#        val = float(str(self.maxText.text()))
#        self.setMaxValue(val)
#            
#    """
#    change only the displayed max value
#    """
#    def setDisplayedMaxValue(self, val):
#        self.maxValue = val
#        self.maxText.setText("%g"%val)
#
#    # DATA values
#    """
#    set min/max value of data source
#    """
#    def setDataMinMax(self, minVal, maxVal):
#        if minVal is not None:
#            vmin = float(str(minVal))
#            self.dataMin = vmin
#        if maxVal is not None:
#            vmax = float(str(maxVal))
#            self.dataMax = vmax
#
#        # are current values in the good range ?
#        self._update()
#
#    """
#    send 'ColormapChanged' signal
#    """
#    def sendColormap(self):
#        try:
#            if self.parent is not None:                
#                self.parent.emit(qt.PYSIGNAL("ColormapChanged"),
#                        (self.colormap, self.autoscale,
#                         self.minValue, self.maxValue))
#        except:
#            sys.excepthook(sys.exc_info()[0],
#                           sys.exc_info()[1],
#                           sys.exc_info()[2])



###############################################################################
####################            QubColormapAction          ####################
###############################################################################
class QubColormapAction(QubAction):
    """
    This action will allow in a display widget to open the QubColormap dialog
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
        """
        QubAction.__init__(self, *args, **keys)
        
        self._item = None
        self._colormapDialog = None
        
    def addToolWidget(self, parent):
        """
        create colormap pushbutton in the toolbar of the view
        create the colormap dialog if not already done
        """
        
        """
        create colormap dialog
        """
        if self._colormapDialog is None:
            self._colormapDialog = QubColormapDialog(parent)
        
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
         
    def setParam(self, param):
        """
        param[0] = colormap  0 = Greyscale
                             1 = Reverse Grey
                             2 = Temperature
                             3 = Red
                             4 = Green
                             5 = Blue
        param[1] = autoscale
        param[2] = min data value
        param[3] = max data value
        param[4] = min colormap value
        param[5] = max colormap value
        """
        parlen = len(param)
                
        if parlen >= 1 and param[0] is not None:
            self.colormapDialog.setColormap(param[0])
        
        if parlen >= 2 and param[1] is not None:
            self.colormapDialog.setAutoscale(param[1])
            
        if parlen >= 3:
            minVal = param[2]
        else:
            minVal = None            
        if parlen >= 4:
            maxVal = param[3]
        else:
            maxVal = None
        self.colormapDialog.setDataMinMax(minVal, maxVal)
            
        if parlen >= 5 and param[4] is not None:
            self.colormapDialog.setMinValue(param[4])
            
        if parlen >= 6 and param[5] is not None:
            self.colormapDialog.setMaxValue(param[5])

        self.colormapDialog._update()
        
                      
################################################################################
####################    TEST -- QubViewActionTest -- TEST   ####################
################################################################################
from Qub.Widget.QubImageView import QubImageView
import EdfFile
import spslut

def Edf2Pixmap(file):
    edf = EdfFile.EdfFile(file)
    data = edf.GetData(0)
    minData = Numeric.minimum.reduce(Numeric.minimum.reduce(data))
    maxData = Numeric.maximum.reduce(Numeric.maximum.reduce(data))
    (image_str, size, minmax) = spslut.transform(data ,
                                                 (1,0), 
                                                 (spslut.LINEAR, 3.0),
                                                 "BGRX", 
                                                 spslut.GREYSCALE,
                                                 1, 
                                                 (minData, maxData))            
    image = qt.QImage(image_str,size[0],size[1],32,None,0,
                      qt.QImage.IgnoreEndian)
    pixmap = qt.QPixmap()
    pixmap.convertFromImage(image)         	      
    return pixmap        
      
class QubMain(qt.QMainWindow):
    def __init__(self, parent=None, file=None):
        qt.QMainWindow.__init__(self, parent)
        
        #pixmap = qt.QPixmap(file)
        pixmap = Edf2Pixmap(file)
        
        actions = []
        action = QubColormapAction(show=1, group="admin")
        actions.append(action)
        
        container = qt.QWidget(self)
        
        hlayout = qt.QVBoxLayout(container)
    
        qubImage = QubImageView(container, "Test QubImageAction's",
                                       pixmap, actions)
                                       
        hlayout.addWidget(qubImage)
    
        self.setCentralWidget(container)
               
##  MAIN   
if  __name__ == '__main__':
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubMain(file=sys.argv[1])
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
