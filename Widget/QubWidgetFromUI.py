import sys
import os.path

import qt
import qtui

class QubWidgetFromUI(qt.QWidget) :
    def __init__(self,parent = None,name = None,fl = 0) :
        qt.QWidget.__init__(self,parent,name,fl)
        self.__widgetTree = None
    def child(self,name) :
        if self.__widgetTree is not None :
            return self.__widgetTree.child(name)

    def createGUIFromUI(self,filename) :
        modulePath = sys.modules[self.__class__.__module__].__file__
        path = os.path.dirname(modulePath)

        self.__widgetTree = qtui.QWidgetFactory.create(os.path.join(path,filename))

        self.__widgetTree.reparent(self,qt.QPoint(0,0))
        if not self.layout() :
            layout = qt.QHBoxLayout(self,0,0)
        self.layout().addWidget(self.__widgetTree)
        
