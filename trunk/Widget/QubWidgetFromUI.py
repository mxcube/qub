import sys
import os.path

import qt
import qtui
## Create a widget from .ui file (designer)
#
#this class use qtui module to load at run time the widget tree of the ui file
#you can access to a widget by his name by using the methode <i>child('widget name')</i>.
#To use this simple class you have to derivate it
#@see Qub::Widget::QubPad::QubPad
class QubWidgetFromUI(qt.QWidget) :
    def __init__(self,parent = None,name = None,fl = 0) :
        qt.QWidget.__init__(self,parent,name,fl)
    ##@brief this methode load a ui file which is in the same diectory of the module and reparent the tree widget
    #
    #@param filename the file name of the ui file without the path
    #@param widgetName :
    # - if None reparent the whole tree
    # - else truncated the tree to the widgetName if exist
    #
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
        
