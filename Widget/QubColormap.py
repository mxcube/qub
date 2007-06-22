import qt

import numpy

from Qub.Icons.QubIcons import loadIcon
from Qub.Widget.Graph.QubGraph import QubGraph
from Qub.Widget.Graph.QubGraphCurve import  QubGraphCurve

from Qub.Tools.QubWeakref import createWeakrefMethod
from Qub.CTools.pixmaptools import LUT

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
        self.__data = None
        self.__histoTimer = qt.QTimer(self)
        qt.QObject.connect(self.__histoTimer,qt.SIGNAL('timeout()'),self.__calcHistogram)
        
        self.__colormapSps = [("Greyscale",LUT.Palette.GREYSCALE),
                              ("Reverse Grey",LUT.Palette.REVERSEGREY),
                              ("Temperature",LUT.Palette.TEMP),
                              ("Red",LUT.Palette.RED),
                              ("Green",LUT.Palette.GREEN),
                              ("Blue",LUT.Palette.BLUE),
                              ("Many",LUT.Palette.MANY)]

        self.__lutType = [('Linear',LUT.LINEAR),('Logarithm',LUT.LOG),('Shift Logarithm',LUT.SHIFT_LOG)]
                         
        
        """
        main layout (VERTICAL)
        """
        vlayout = qt.QVBoxLayout(self, 0, -1, "Main ColormapDialog Layout")
        vlayout.setMargin(10)
        vlayout.setSpacing(10)

        """
        combo for colormap
        """
        colormapData = numpy.resize(numpy.arange(60), (10,60))
        self.__colormapCombo = qt.QComboBox(self)
        palette = LUT.Palette()
        for colormapName,colormapType in self.__colormapSps:
            palette.fillPalette(colormapType)
            image,(minVal,maxVal) = LUT.map_on_min_max_val(colormapData,palette,LUT.LINEAR)
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
                     self.__minMaxTextChanged)
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
                     self.__minMaxTextChanged)
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
        self.__colormapGraph.enableAxis(self.__colormapGraph.yLeft,False)
        self.__colormapGraph.setXLabel("Data Values")

        """
        set the curve _/-
        """
        self.colormapCurve = QubGraphCurve("ColormapCurve")
        self.colormapCurve.setData(numpy.array([0, 10, 20, 30]),numpy.array([-10, -10, 10, 10 ]))
        self.colormapCurve.attach(self.__colormapGraph)
        self.__minControl = self.colormapCurve.getPointControl(1)
        self.__minControl.setConstraints(10, 20, -10, -10)
        self.__minControl.setValueChangeCallback(self.__minMoved)
        
        self.__maxControl = self.colormapCurve.getPointControl(2)
        self.__maxControl.setConstraints(10, 20,  10,  10)
        self.__maxControl.setValueChangeCallback(self.__maxMoved)
        
        self.__lowerBound = self.colormapCurve.getPointMarked(0)
        self.__upperBound = self.colormapCurve.getPointMarked(3)


        self.__colormapGraph.setMinimumSize(qt.QSize(250,200))

        hlayout4.addWidget(self.__colormapGraph)

        #Histogram curve
        self.__histoCurve = QubGraphCurve("Histo")
        self.__histoCurve.setAxis(QubGraph.xBottom,QubGraph.yRight)
        self.__histoCurve.setStyle(self.__histoCurve.Sticks)
        self.__histoCurve.setPen(qt.QPen(qt.Qt.blue,2))
        self.__histoCurve.attach(self.__colormapGraph)
        self.__colormapGraph.setAxisAutoScale(QubGraph.yRight)
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
        sigma
        """
        self.__sigmaScaleMode = [('\xb1 std dev / 2',0,0.5),
                                 ('\xb1 std dev',1,1.),
                                 ('\xb1 std dev * 2',2,2.)]
        
        self.__sigmaScale = qt.QToolButton(self,"sigma")
        qt.QObject.connect(self.__sigmaScale, qt.SIGNAL("clicked()"),
                           self.__sigmaScaleChanged)
        popupMenu = qt.QPopupMenu(self.__sigmaScale)
        qt.QObject.connect(popupMenu, qt.SIGNAL("activated(int )"),
                           self.__sigmaModeSelected)

        self.__sigmaScale.setPopup(popupMenu)
        self.__sigmaScale.setPopupDelay(0)
        for itemText,itemVal,_ in self.__sigmaScaleMode :
            popupMenu.insertItem(itemText,itemVal)
        self.__sigmaModeSelected(1)
        hlayout5.addWidget(self.__sigmaScale)
        """
        colormap window can not be resized
        """
##        self.setFixedSize(vlayout.minimumSize())
        self.__refreshCallback = None
        self.__colormap = None
        
    def __del__(self) :
        self.__refreshCallback = None
                
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
    def __minMaxTextChanged(self):
        """
        min value changed
            - update the colormap dialog
            - send the "ColormapChanged" signal
        """
        if self.__colormap :
            minMax,_ = self.__minText.text().toFloat()
            maxVal,_ = self.__maxText.text().toFloat()

            self.__colormap.setMinMax(minMax,maxVal)
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
                       self.__minText,self.__maxText,self.__sigmaScale] :
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

    def __sigmaScaleChanged(self) :
        minMax = self.__get_min_max_with_sigma()
        self.__colormap.setMinMax(*minMax)
        self.__refreshImage()
        
    def __sigmaModeSelected(self,index) :
        self.__sigmaScaleSelectedMode = index
        self.__sigmaScale.setText(self.__sigmaScaleMode[index][0])


    def __get_min_max_with_sigma(self) :
        nbValue = 1
        for val in self.__data.shape:
            nbValue *= val
        integralVal = self.__data.sum() 
        average = integralVal / nbValue
        stdDeviation = self.__data.std()
        stdDeviation *= self.__sigmaScaleMode[self.__sigmaScaleSelectedMode][2]
        return (average - stdDeviation,average + stdDeviation)
 
    #############################################
    ### GRAPH
    #############################################
    def __maxMoved(self,x,y) :
        if self.__colormap:
            minVal,_ = self.__colormap.minMax()
            self.__colormap.setMinMax(minVal,x)
        self.__refreshImage()
        
    def __minMoved(self,x,y) :
        if self.__colormap:
            _,maxVal = self.__colormap.minMax()
            self.__colormap.setMinMax(x,maxVal)
        self.__refreshImage()
        
    def setData(self,data):
        colormap = self.__colormap
        if colormap and data is not None:
            self.__data = data

            if colormap.lutType() == LUT.LOG :
                self.__dataMin,self.__dataMax = colormap.minMaxMappingMethode()
            else:
                self.__dataMin,self.__dataMax = self.__data.min(),self.__data.max()
                
                     ####### GRAPH UPDATE #######
            """
            calculate visible part of the graph outside data values (margin)
            """
            marge = (abs(self.__dataMax) + abs(self.__dataMin)) / 6.0
            minmd = self.__dataMin - marge
            maxpd = self.__dataMax + marge
            self.__colormapGraph.setAxisScale(self.__colormapGraph.xBottom,minmd-marge/2, maxpd)
            self.__colormapGraph.setAxisScale(self.__colormapGraph.yLeft,-11.5, 11.5)
            """
            tells where points can move:
                first and last : do not move
                second and third: cannot move in Y dir.,can move
                                  in X dir. between datamin and datamax
            """
            self.__minControl.setConstraints(self.__dataMin, self.__dataMax, -10, -10)
            self.__maxControl.setConstraints(self.__dataMin, self.__dataMax,  10,  10)

            """
            move points to their values
            """
            if colormap.autoscale() :
                minValue,maxValue = self.__dataMin,self.__dataMax
            else:
                minValue,maxValue = colormap.minMax()

            self.__lowerBound.setValue(minmd, -10)
            self.__minControl.setValue(minValue, -10)
            self.__maxControl.setValue(maxValue, 10)
            self.__upperBound.setValue(maxpd, 10)
            self.__colormapGraph.replot()
                         ####### TEXT UPDATE #######
            if isinstance(minValue,int):
                self.__minText.setText('%d' % minValue)
                self.__maxText.setText('%d' % maxValue)
            else:
                self.__minText.setText('%lf' % minValue)
                self.__maxText.setText('%lf' % maxValue)
 
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
        #HISTO
        if self.isShown() and not self.__histoTimer.isActive():
            self.__histoTimer.start(5000)
        
    def __refreshImage(self) :
        if self.__refreshCallback :
            self.__refreshCallback()

    def __calcHistogram(self) :
        if self.__data is not None:
            minVal,maxVal = self.__colormap.minMax()
            YHisto,XHisto = numpy.histogram(self.__data,bins = 25,range=[minVal,maxVal])
            self.__histoCurve.setData(XHisto,YHisto)
            self.__colormapGraph.replot()
            
    def show(self) :
        qt.QWidget.show(self)
        self.__histoTimer.stop()
        self.__calcHistogram()
################################################################################
####################    TEST -- QubViewActionTest -- TEST   ####################
################################################################################
def Edf2Pixmap(file):
    edf = EdfFile.EdfFile(file)
    data = edf.GetData(0)
##    minData = Numeric.minimum.reduce(Numeric.minimum.reduce(data))
##    maxData = Numeric.maximum.reduce(Numeric.maximum.reduce(data))
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
    app = qt.QApplication(sys.argv)

    qt.QObject.connect(app, qt.SIGNAL("lastWindowClosed()"),
                    app, qt.SLOT("quit()"))

    window = QubMain()
    
    window.resize(500,300)
    app.setMainWidget(window)
    
    window.show()
    app.exec_loop()
 
