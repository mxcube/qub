import qt
import Numeric

import spslut

from Qub.Icons.QubIcons import loadIcon
from Qub.Widget.QubImage import QubImage
from Qub.Widget.QubGraph import QubGraph, QubGraphCurve

from Qub.Tools.QubWeakref import createWeakrefMethod

################################################################################
####################                QubAction               ####################
################################################################################
class QubColormapDialog(qt.QWidget):
    """
    Creates a dialog box to change a colormap.
    It allows to change colormaps (Greyscale, Reverse Grey, Temperature,
    Red, Green, Blue, Many) and the mapping on the selected colormap of
    the min and max value of the data. it also allows to set the colormap in
    autoscale mode or not.
    When any of these parameters change, the signal "ColormapChanged" is
    sent with the parameters colormap, autoscale, minValue, maxValue
    """
    def __init__(self, parent=None, name="Colormap"):
        """
        Constructor method
        Create the layout of the colormap dialog widget using default value
        """
        qt.QWidget.__init__(self, parent,name)
        self.setIcon(loadIcon('colormap.png'))
        self.__dataMin = 0
        self.__dataMax = 255
        
        self.__colormapSps = [("Greyscale",spslut.GREYSCALE),
                              ("Reverse Grey",spslut.REVERSEGREY),
                              ("Temperature",spslut.TEMP),
                              ("Red",spslut.RED),
                              ("Green",spslut.GREEN),
                              ("Blue",spslut.BLUE),
                              ("Many",spslut.MANY)]

        self.__lutType = [('Linear',spslut.LINEAR),('Logarithm',spslut.LOG)]
                         
        
        """
        main layout (VERTICAL)
        """
        vlayout = qt.QVBoxLayout(self, 0, -1, "Main ColormapDialog Layout")
        vlayout.setMargin(10)
        vlayout.setSpacing(10)

        """
        combo for colormap
        """
        colormapData = Numeric.resize(Numeric.arange(60), (10,60))
        self.__colormapCombo = qt.QComboBox(self)
        for colormapName,colormapType in self.__colormapSps:
            (image_str, size, minmax) = spslut.transform(colormapData ,
                                                         (1,0), 
                                                         (spslut.LINEAR, 3.0),
                                                         "BGRX", 
                                                         colormapType,
                                                         1, 
                                                         (0, 0))
            image = qt.QImage(image_str,size[0],size[1],32,None,0,
                          qt.QImage.IgnoreEndian)
            self.__colormapCombo.insertItem(qt.QPixmap(image),colormapName)
        self.connect(self.__colormapCombo, qt.SIGNAL("activated(int)"),
                     self.__colormapTypeChanged)
        vlayout.addWidget(self.__colormapCombo)

        self.__lutTypeCombo = qt.QComboBox(self)
        for lutTypeName,lutType in self.__lutType:
            self.__lutTypeCombo.insertItem(lutTypeName)
        vlayout.addWidget(self.__lutTypeCombo)
        self.connect(self.__lutTypeCombo, qt.SIGNAL("activated(int)"),
                     self.__lutTypeChanged)
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
        self.__minLabel  = qt.QLabel("Minimum", self)
        hlayout2.addWidget(self.__minLabel)
        
        """
        min label text
        """
        hlayout2.addSpacing(5)
        hlayout2.addStretch(1)
        self.__minText  = qt.QLineEdit(self)
        self.__minText.setValidator(qt.QDoubleValidator(self.__minText))
        self.__minText.setFixedWidth(150)
        self.__minText.setAlignment(qt.Qt.AlignRight)
        self.connect(self.__minText, qt.SIGNAL("returnPressed()"),
                     self.__minTextChanged)
        hlayout2.addWidget(self.__minText)
        
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
        self.__maxLabel  = qt.QLabel("Maximum", self)
        hlayout3.addWidget(self.__maxLabel)
        
        """
        max label text
        """
        hlayout3.addSpacing(5)
        hlayout3.addStretch(1)
        self.__maxText  = qt.QLineEdit(self)
        self.__maxText.setValidator(qt.QDoubleValidator(self.__maxText))
        self.__maxText.setFixedWidth(150)
        self.__maxText.setAlignment(qt.Qt.AlignRight)
        
        self.connect(self.__maxText, qt.SIGNAL("returnPressed()"),
                     self.__maxTextChanged)
        hlayout3.addWidget(self.__maxText)
        
        """
        hlayout 4 (HORIZONTAL)
            - graph
        """
        hlayout4 = qt.QHBoxLayout(vlayout, -1, "layout 4")
        hlayout4.setSpacing(10)
        
        """
        graph
        """
        self.__colormapGraph  = QubGraph(self)
        
        """
        remove Y axis label
        set X axis label
        remove curves legends
        """
        self.__colormapGraph.enableYLeftAxis(0)
        self.__colormapGraph.setXLabel("Data Values")
        self.__colormapGraph.useLegend(False)

        """
        set the curve _/-
        """
        self.colormapCurve = QubGraphCurve (self.__colormapGraph,
                                            "ColormapCurve",
                                            [0, 10, 20, 30],
                                            [-10, -10, 10, 10 ]
                                            )
        
        self.colormapCurve.defConstraints(1, 10, 20, -10, -10)
        self.colormapCurve.defConstraints(2, 10, 20,  10,  10)
        self.colormapCurve.setPointControlled(1)
        self.colormapCurve.setPointControlled(2)

        self.colormapCurve.setPointMarked(0)
        self.colormapCurve.setPointMarked(3)

        self.__colormapGraph.setCurve(self.colormapCurve)

        self.__colormapGraph.setMinimumSize(qt.QSize(250,200))

        self.connect (self.__colormapGraph, qt.PYSIGNAL("PointMoved"),
                      self._graphMove)
        self.connect (self.__colormapGraph, qt.PYSIGNAL("PointReleased"),
                      self._graphRelease)

        hlayout4.addWidget(self.__colormapGraph)
        
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
        self.__autoscaleToggle = qt.QPushButton("Autoscale", self)
        self.__autoscaleToggle.setToggleButton(True)
        self.connect(self.__autoscaleToggle, qt.SIGNAL("toggled(bool)"),
                     self.__autoscaleChanged)
        hlayout5.addWidget(self.__autoscaleToggle)

        """
        scale 90%
        """
        self.__scale90Button = qt.QPushButton("90%", self)
        self.connect(self.__scale90Button, qt.SIGNAL("clicked()"),
                     self.__scale90Changed)
        hlayout5.addWidget(self.__scale90Button)

        """
        full scale
        """
        self.__fullscaleButton = qt.QPushButton("Full", self)
        self.connect(self.__fullscaleButton, qt.SIGNAL("clicked()"),
                     self.__fullscaleChanged)
        hlayout5.addWidget(self.__fullscaleButton)

        """
        colormap window can not be resized
        """
        self.setFixedSize(vlayout.minimumSize())
        self.__refreshCallback = None
        self.__colormap = None

    ##@brief setCaptionPrefix
    def setCaptionPrefix(self,prefix) :
        self.setCaption(prefix)
        
    ##@brief this methode set the callback fro refresh when colormap has changed
    def setColormapNRefreshCallBack(self,colormap,cbk) :
        self.__colormap = colormap
        self.__refreshCallback = createWeakrefMethod(cbk)
    #############################################
    ### COLORMAP
    #############################################
    def __colormapTypeChanged(self, colormapID):
        """
        type of colormap has changed
            - update the colormap dialog
            - send the "ColormapChanged" signal
        """
        if self.__colormap:
            self.__colormap.setColorMapType(self.__colormapSps[colormapID][1])
            self.__refreshImage()
    #############################################
    ### LUT
    #############################################
    def __lutTypeChanged(self,lutID) :
        if self.__colormap:
            self.__colormap.setLutType(self.__lutType[lutID][1])
            self.__refreshImage()
    #############################################
    ### MIN/MAX VALUES
    #############################################
    def __minTextChanged(self):
        """
        min value changed
            - update the colormap dialog
            - send the "ColormapChanged" signal
        """
        if self.__colormap :
            minVal,maxVal = colormap.minMax()
            val,_ = self.__minText.text().toFloat()
            colormap.setMinMax(val,maxVal)
            self.__refreshImage()

    def __maxTextChanged(self):
        """
        max value changed
            - update the colormap dialog
            - send the "ColormaChanged" signal
        """
        if self.__colormap:
            minVal,maxVal = colormap.minMax()
            val,_ = self.__maxText.text().toFloat()
            colormap.setMinMax(minVal,val)
            self.__refreshImage()
            
    #############################################
    ### SCALES
    #############################################
    def __autoscaleChanged(self, val):
        """
        autoscale value changed
            - update the colormap dialog
            - send the "ColormaChanged" signal
        """
        for widget in [self.__colormapGraph,self.__scale90Button,self.__fullscaleButton,
                       self.__minText,self.__maxText] :
            widget.setEnabled(not val)
        if self.__colormap:
            self.__colormap.setAutoscale(val)
            self.__refreshImage()
            
    def __scale90Changed(self):
        """
        set min value to be the min value of the data and max value to be
        the value corresponding to 90% of the different value of the data
        """
        if self.__colormap:
            self.__colormap.setMinMax(self.__dataMin,0.9 * self.__dataMax)
            self.__refreshImage()

    def __fullscaleChanged(self):
        """
        set min/max value of the colormap to the min/max value of the data
        """
        if self.__colormap:
            self.__colormap.setMinMax(self.__dataMin,self.__dataMax)
            self.__refreshImage()
        

    #############################################
    ### GRAPH
    #############################################
    def _graphMove(self, *args):
        """
        user is moving a point given by args[0] to the position given
        by(args[1],args[2])
        """
        self._graphRelease(*args)
        
    def _graphRelease(self, *args):
        """
        user is release mouse on point given by (args[1],args[2]) for
        the point given by args[0]
        This will be the new min or max value for the colormap.
        Send the signal "ColormapChanged"
        """
        (curve, point , x ,y) = (args[0], args[1], args[2], args[3])

        if self.__colormap :
            minVal,maxVal = self.__colormap.minMax()
            if point == 1:
                self.__colormap.setMinMax(x,maxVal)
            elif point == 2:
                self.__colormap.setMinMax(minVal,x)
            self.__refreshImage()
        
    def update(self,data):
        colormap = self.__colormap
        if colormap and data:
            data = Numeric.ravel(data)
            self.__dataMin,self.__dataMax = min(data),max(data)
                     ####### GRAPH UPDATE #######
            """
            calculate visible part of the graph outside data values (margin)
            """
            marge = (abs(self.__dataMax) + abs(self.__dataMin)) / 6.0
            minmd = self.__dataMin - marge
            maxpd = self.__dataMax + marge
            self.__colormapGraph.setZoom(minmd-marge/2, maxpd, -11.5, 11.5)

            """
            tells where points can move:
                first and last : do not move
                second and third: cannot move in Y dir.,can move
                                  in X dir. between datamin and datamax
            """ 
            self.colormapCurve.defConstraints(1, self.__dataMin, self.__dataMax, -10, -10)
            self.colormapCurve.defConstraints(2, self.__dataMin, self.__dataMax,  10,  10)

            """
            move points to their values
            """
            if colormap.autoscale() :
                minValue,maxValue = self.__dataMin,self.__dataMax
            else:
                minValue,maxValue = colormap.minMax()
            self.__colormapGraph.deplace(self.colormapCurve, 0, minmd, -10)
            self.__colormapGraph.deplace(self.colormapCurve, 1, minValue, -10)
            self.__colormapGraph.deplace(self.colormapCurve, 2, maxValue, 10)
            self.__colormapGraph.deplace(self.colormapCurve, 3, maxpd, 10)

            self.__colormapGraph.replot()
                         ####### TEXT UPDATE #######
            self.__minText.setText('%d' % minValue)
            self.__maxText.setText('%d' % maxValue)

            colormapType = self.__colormapSps[self.__colormapCombo.currentItem()]
            if colormapType[1] != colormap.colorMapType():
                for i,(colorTypeName,colorType) in enumerate(self.__colormapSps):
                    if colorType == colormap.colorType() :
                        self.__colormapCombo.setCurrentItem(i)
                        break

            lutType = self.__lutType[self.__lutTypeCombo.currentItem()]
            if lutType[1] != colormap.lutType() :
                for i,(lutTypeName,lutType) in enumerate(self.__lutType):
                    if lutType == colormap.lutType() :
                        self.__lutTypeCombo.setCurrentItem(i)
                        break

            self.__autoscaleToggle.setOn(colormap.autoscale())
            
    def __refreshImage(self) :
        if self.__refreshCallback :
            self.__refreshCallback()
            
 
################################################################################
####################    TEST -- QubViewActionTest -- TEST   ####################
################################################################################
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
                
        container = qt.QWidget(self)
        
        hlayout = qt.QHBoxLayout(container)
    
        """
        LABEL
        """
        vlayout1 = qt.QVBoxLayout(hlayout)

        colormapLabel = qt.QLabel("Colormap", container)
        vlayout1.addWidget(colormapLabel)

        colorminLabel = qt.QLabel("Color Min.", container)
        vlayout1.addWidget(colorminLabel)

        colormaxLabel = qt.QLabel("Color Max.", container)
        vlayout1.addWidget(colormaxLabel)

        dataminLabel = qt.QLabel("Data Min.", container)
        vlayout1.addWidget(dataminLabel)

        datamaxLabel = qt.QLabel("Data Max.", container)
        vlayout1.addWidget(datamaxLabel)

        autoscaleLabel = qt.QLabel("Autoscale", container)
        vlayout1.addWidget(autoscaleLabel)
        
        """
        TEXT
        """
        vlayout2 = qt.QVBoxLayout(hlayout)
        
        self.colormapText  = qt.QLineEdit(container)
        self.connect(self.colormapText, qt.SIGNAL("returnPressed()"),
                     self.colormapChanged)
        vlayout2.addWidget(self.colormapText)
        
        self.colorminText  = qt.QLineEdit(container)
        self.connect(self.colorminText, qt.SIGNAL("returnPressed()"),
                     self.colorminChanged)
        vlayout2.addWidget(self.colorminText)
        
        self.colormaxText  = qt.QLineEdit(container)
        self.connect(self.colormaxText, qt.SIGNAL("returnPressed()"),
                     self.colormaxChanged)
        vlayout2.addWidget(self.colormaxText)
        
        self.dataminText  = qt.QLineEdit(container)
        self.connect(self.dataminText, qt.SIGNAL("returnPressed()"),
                     self.dataminChanged)
        vlayout2.addWidget(self.dataminText)
        
        self.datamaxText  = qt.QLineEdit(container)
        self.connect(self.datamaxText, qt.SIGNAL("returnPressed()"),
                     self.datamaxChanged)
        vlayout2.addWidget(self.datamaxText)
        
        self.autoscaleText  = qt.QLineEdit(container)
        self.connect(self.autoscaleText, qt.SIGNAL("returnPressed()"),
                     self.autoscaleChanged)
        vlayout2.addWidget(self.autoscaleText)
        
        """
        BUTTON
        """
        hlayout.addSpacing(10)                
        vlayout3 = qt.QVBoxLayout(hlayout)
        
        button = qt.QPushButton("Set all parameters", container)
        self.connect(button, qt.SIGNAL("clicked()"), self.allChanged)
        vlayout3.addWidget(button)
        
        """
        create an show Colormap Dialog
        """
        
        self.colormapDialog = QubColormapDialog(container)
        self.colormapDialog.show()
        self.setCentralWidget(container)

    def colormapChanged(self):              
        val = int(str(self.colormapText.text()))
        self.colormapDialog.setParam(colormap=val)
        
    def colorminChanged(self):
        val = float(str(self.colorminText.text()))        
        self.colormapDialog.setParam(colorMin=val)
        
    def colormaxChanged(self):
        val = float(str(self.colormaxText.text()))        
        self.colormapDialog.setParam(colorMax=val)
        
    def dataminChanged(self):
        val = float(str(self.dataminText.text()))        
        self.colormapDialog.setParam(dataMin=val)
        
    def datamaxChanged(self):
        val = float(str(self.datamaxText.text()))        
        self.colormapDialog.setParam(dataMax=val)
        
    def autoscaleChanged(self):
        val = float(str(self.autoscaleText.text()))        
        self.colormapDialog.setParam(autoscale=val)
        
    def allChanged(self):
        _colormap  = int(str(self.colormapText.text()))        
        _colorMin  = float(str(self.colorminText.text()))        
        _colorMax  = float(str(self.colormaxText.text()))        
        _dataMin   = float(str(self.dataminText.text()))        
        _dataMax   = float(str(self.datamaxText.text()))        
        _autoscale = float(str(self.autoscaleText.text()))        
        self.colormapDialog.setParam(colormap=_colormap,
                                     colorMin=_colorMin,
                                     colorMax=_colorMax,
                                     dataMin=_dataMin,
                                     dataMax=_dataMax,
                                     autoscale=_autoscale)

##  MAIN   
if  __name__ == '__main__':
    import EdfFile
    import sys
    from Qub.Widget.QubImageView import QubImageView
    
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubMain()
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
