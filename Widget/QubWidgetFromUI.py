import sys
import os.path

import qt
import qtui

class QubWidgetFromUI(qt.QWidget) :
    def __init__(self,parent = None,name = None,fl = 0) :
        qt.QWidget.__init__(self,parent,name,fl)

    def createGUIFromUI(self,filename,widgetName = None) :
        modulePath = sys.modules[self.__class__.__module__].__file__
        path = os.path.dirname(modulePath)

        if not self.layout() :
            layout = qt.QHBoxLayout(self,0,0)

        widgetUI = qtui.QWidgetFactory.create(os.path.join(path,filename))
        tmpWidget = None
        if widgetName is not None :
            tmpWidget = widgetUI.child(widgetName)
        if tmpWidget is not None :
            tmpWidget.reparent(self,qt.QPoint(0,0))
            self.layout().addWidget(tmpWidget)
        else :
            widgetUI.reparent(self,qt.QPoint(0,0))
            self.layout().addWidget(widgetUI)
        
