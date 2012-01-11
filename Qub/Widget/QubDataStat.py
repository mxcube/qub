# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QubDataStat.ui'
#
# Created: Thu Apr 19 15:46:03 2007
#      by: The PyQt User Interface Compiler (pyuic) 3.17.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class Histogram(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        if not name:
            self.setName("Histogram")


        HistogramLayout = QVBoxLayout(self,11,6,"HistogramLayout")

        layout4 = QGridLayout(None,1,1,0,6,"layout4")

        self.__stdDevLE = QLineEdit(self,"__stdDevLE")
        self.__stdDevLE.setReadOnly(1)

        layout4.addWidget(self.__stdDevLE,2,3)

        self.textLabel3 = QLabel(self,"textLabel3")

        layout4.addWidget(self.textLabel3,0,2)

        self.textLabel4 = QLabel(self,"textLabel4")

        layout4.addWidget(self.textLabel4,1,2)

        self.textLabel5 = QLabel(self,"textLabel5")

        layout4.addWidget(self.textLabel5,2,0)

        self.__widthLE = QLineEdit(self,"__widthLE")
        self.__widthLE.setReadOnly(1)

        layout4.addWidget(self.__widthLE,0,1)

        self.textLabel7 = QLabel(self,"textLabel7")

        layout4.addWidget(self.textLabel7,2,2)

        self.textLabel1 = QLabel(self,"textLabel1")

        layout4.addWidget(self.textLabel1,0,0)

        self.textLabel2 = QLabel(self,"textLabel2")

        layout4.addWidget(self.textLabel2,1,0)

        self.__maxValLE = QLineEdit(self,"__maxValLE")
        self.__maxValLE.setReadOnly(1)

        layout4.addWidget(self.__maxValLE,1,3)

        self.__averageLE = QLineEdit(self,"__averageLE")
        self.__averageLE.setReadOnly(1)

        layout4.addWidget(self.__averageLE,2,1)

        self.__nbPixelLE = QLineEdit(self,"__nbPixelLE")
        self.__nbPixelLE.setReadOnly(1)

        layout4.addWidget(self.__nbPixelLE,3,3)

        self.textLabel6 = QLabel(self,"textLabel6")

        layout4.addWidget(self.textLabel6,3,0)

        self.__heightLE = QLineEdit(self,"__heightLE")
        self.__heightLE.setReadOnly(1)

        layout4.addWidget(self.__heightLE,1,1)

        self.__minValLE = QLineEdit(self,"__minValLE")
        self.__minValLE.setReadOnly(1)

        layout4.addWidget(self.__minValLE,0,3)

        self.__integralLE = QLineEdit(self,"__integralLE")
        self.__integralLE.setReadOnly(1)

        layout4.addWidget(self.__integralLE,3,1)

        self.textLabel8 = QLabel(self,"textLabel8")

        layout4.addWidget(self.textLabel8,3,2)
        HistogramLayout.addLayout(layout4)

        self.__graphFrame = QFrame(self,"__graphFrame")
        self.__graphFrame.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding,0,0,self.__graphFrame.sizePolicy().hasHeightForWidth()))
        self.__graphFrame.setFrameShape(QFrame.GroupBoxPanel)
        self.__graphFrame.setFrameShadow(QFrame.Raised)
        __graphFrameLayout = QVBoxLayout(self.__graphFrame,11,6,"__graphFrameLayout")

        layout3 = QHBoxLayout(None,0,6,"layout3")

        self.textLabel1_2 = QLabel(self.__graphFrame,"textLabel1_2")
        layout3.addWidget(self.textLabel1_2)

        self.__minHisto = QLineEdit(self.__graphFrame,"__minHisto")
        layout3.addWidget(self.__minHisto)

        self.textLabel2_2 = QLabel(self.__graphFrame,"textLabel2_2")
        layout3.addWidget(self.textLabel2_2)

        self.__maxHisto = QLineEdit(self.__graphFrame,"__maxHisto")
        layout3.addWidget(self.__maxHisto)
        __graphFrameLayout.addLayout(layout3)

        layout6 = QHBoxLayout(None,0,6,"layout6")

        self.textLabel9_3 = QLabel(self.__graphFrame,"textLabel9_3")
        layout6.addWidget(self.textLabel9_3)

        self.__numberOfChannels = QLineEdit(self.__graphFrame,"__numberOfChannels")
        layout6.addWidget(self.__numberOfChannels)
        __graphFrameLayout.addLayout(layout6)
        HistogramLayout.addWidget(self.__graphFrame)

        self.languageChange()

        self.resize(QSize(292,200).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("Histogram"))
        self.textLabel3.setText(self.__tr("Min. Val"))
        self.textLabel4.setText(self.__tr("Max. Val:"))
        self.textLabel5.setText(self.__tr("Average Val.:"))
        self.textLabel7.setText(self.__tr("Std Dev.:"))
        self.textLabel1.setText(self.__tr("Width:"))
        self.textLabel2.setText(self.__tr("Height:"))
        self.textLabel6.setText(self.__tr("Integral Val."))
        self.textLabel8.setText(self.__tr("Nb Pixels:"))
        self.textLabel1_2.setText(self.__tr("Min. :"))
        self.textLabel2_2.setText(self.__tr("Max. :"))
        self.textLabel9_3.setText(self.__tr("Number of Channels :"))


    def __tr(self,s,c = None):
        return qApp.translate("Histogram",s,c)
