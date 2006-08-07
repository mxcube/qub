import qt
import thread
import threading
import sys
import Numeric
import time

import spslut
import sps

from Qub.Widget.QubProfiler import AppProfiler
#import blisspixmap

################################################################################
####################            QubThreadUpdater            ####################
################################################################################
class QubThreadUpdater(qt.QThread):
    """
    QubThreadUpdater is a base class to update data structure without blocking
    the Qt main event loop.
    Using start() method, you enter in an infinite loop which will poll for an
    update generated by the update() method. Once the update is received, a Qt
    CustomEvent is build in the buildEvent method which should be reimplemented
    and a CustomEvent is sent.
    You can stop the infinite loop using the stop() method.
    """
    def __init__(self, receiver=None, name=None):
        """
        Create the thread.
        Register the receiver of the CustomEvent
        Connect the aboutToQuit() signal of the application to the stop()
        method of the thread in order to leave safely the application.
        """
        qt.QThread.__init__(self)
        
        self.receiver = receiver
        self.name = name
        
        qt.QObject.connect(qt.qApp, qt.SIGNAL("aboutToQuit()"), self.stop)
        
        self.mutex = qt.QMutex()
        self.cond = qt.QWaitCondition()
        self.updateEvent = 0
        self.stopEvent   = 1

    def start(self, priority=qt.QThread.InheritPriority):
        """
        Start the thread
        """
        if self.stopEvent != 0:
            self.stopEvent = 0
            qt.QThread.start(self, priority)
        
    def stop(self):
        """
        stop the thread
        """
        self.mutex.lock()
        self.stopEvent = 1
        self.cond.wakeOne()
        self.mutex.unLock()
        
        self.wait()
        
    def update(self):
        """
        Send update to the infinite loop
        """
        self.mutex.lock()
        self.updateEvent = 1
        self.cond.wakeOne()
        self.mutex.unlock()
        

    def run(self):
        """
        Main Thread method.
        Enter in an infinite loop waiting for updateEvent.
        Once received, build event calling buildEvent method and
        send a Qt CustomEvent.
        """
        
        self.mutex.lock()
        while not self.stopEvent:
                        
            while not self.updateEvent and not self.stopEvent:
                self.cond.wait(self.mutex)
             
            if not self.stopEvent:
                self.updateEvent = 0

                event = self.buildEvent()      

                if event is not None:
                    qt.QApplication.postEvent(self.receiver, event)
                
        self.mutex.unlock()
                                
    def builldEvent(self):
        """
        To be reimplemented
        Build the event send to "receiver"
        """
        pass
 

################################################################################
####################            QubPixmap2Canvas            ####################
################################################################################
class QubPixmap2Canvas(QubThreadUpdater):
    """
    Create the displayable bckPixmap of a QubImage with dataPixmap and 
    the Transformation matrix of the QubImage Object ("receiver").
    When event is sent, bckPixmap is ready to be displayed
    """
    def __init__(self, receiver=None, name=None):
        """
        Constructor method
        Variables initialization
        """
        QubThreadUpdater.__init__(self, receiver, name)
        
        self.bckSize = (-1, -1)
        self.dataPixmap = None
        
    def buildEvent(self):
        """
        Build the event which will be sent to the QubImage object ("receiver")
        The event will not have any parameter as this class modify directly
        the QubImage attributes bckPixmap using the QubImage attributes
        dataPixmap and matrix
        """
        try:
            AppProfiler.interStop("t12")
            AppProfiler.interStart("t13", "BuildPixmap")
            update = 0

            if self.receiver.dataPixmap is not None:
                AppProfiler.interStart("t14", "    Resize bckPixmap")
                neww = self.receiver.matrix.m11() * \
                       self.receiver.dataPixmap.width()
                newh = self.receiver.matrix.m22() * \
                       self.receiver.dataPixmap.height()

                if self.bckSize != (neww, newh):
                    qt.qApp.lock()
                    if self.receiver.bckPixmap is not None:
                        self.receiver.bckPixmap.resize(neww, newh)
                    else:
                        self.receiver.bckPixmap = qt.QPixmap(neww, newh)
                    qt.qApp.unlock()
                    self.bckSize = (neww, newh)
                    update = 1

                if self.receiver.dataPixmap != self.dataPixmap:
                    self.dataPixmap = self.receiver.dataPixmap
                    update = 1           
                AppProfiler.interStop("t14")

            if update:
                AppProfiler.interStart("t15", "    Paint bckPixmap")
                qt.qApp.lock()
                painter  = qt.QPainter()
                painter.begin(self.receiver.bckPixmap)
                painter.setWorldMatrix(self.receiver.matrix)
                painter.drawPixmap(0, 0, self.receiver.dataPixmap)
                painter.end()
                qt.qApp.unlock()

                AppProfiler.interStop("t15")
                event = qt.QCustomEvent(qt.QEvent.User)
                event.event_name = "Pixmap2CanvasUpdated"

                return event
            else:
                return None
            AppProfiler.interStop("t13")
            AppProfiler.interStart("t16", "Calling DisplayPixmap")
        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])


################################################################################
####################             QubJpeg2Pixmap             ####################
################################################################################
class QubJpeg2Pixmap(QubThreadUpdater):
    """
    As Jpeg decompression may be slow, this QubThreadUpdater subclass
    transform JPEG data in QPixmap
    """
    def buildEvent(self):
        """
        Build event which will be sent to "receiver"
        Update directly the pixmap attribute of the receiver object
        """
        if self.receiver.data is not None:
            self.receiver.pixmap = qt.QPixmap()
            self.receiver.pixmap.loadFromData(self.receiver.data)

            event = qt.QCustomEvent(QEvent.User)
            event.event_name = "Jpeg2PixmapUpdated"
           
            return event
        
        return None

################################################################################
####################              QubArray2Pixmap           ####################
################################################################################
class QubArray2Pixmap(QubThreadUpdater):
    def __init__(self, receiver, name):
        QubThreadUpdater.__init__(self, receiver, name)
        #self.pixmapIO = blisspixmap.IO()
        #self.pixmapIO.setShmPolicy(blisspixmap.IO.ShmKeepAndGrow)
        
        
    def buildEvent(self):
        if self.receiver.data is not None:
            try:
                AppProfiler.interStop("t3")
                AppProfiler.interStart("t4", "Data2Pixmap")
                if self.receiver.newData:
                    AppProfiler.interStart("t5", "    SPSData")
                    self.receiver.data = sps.getdata(self.receiver.sourceName, self.receiver.dataName)
                    self.receiver.minData = min(Numeric.ravel(self.receiver.data))
                    self.receiver.maxData = max(Numeric.ravel(self.receiver.data))
                    self.receiver.newData = False
                    AppProfiler.interStop("t5")
                
                AppProfiler.interStart("t6", "    spslut")
                cm = self.receiver.colormap.colormap("sps")
                autoscale = self.receiver.colormap.autoscale()
                colorVal = self.receiver.colormap.color()
                (image_str,size,minmax) = spslut.transform(self.receiver.data,
                                               (1,0), (spslut.LINEAR, 3.0),
                                               "BGRX", cm, autoscale, colorVal)            
                AppProfiler.interStop("t6")
                AppProfiler.interStart("t7", "    image")
                qt.qApp.lock()
                image = qt.QImage(image_str,size[0],size[1],32,None,0,
                                  qt.QImage.IgnoreEndian)
                AppProfiler.interStop("t7")
                self.receiver.pix = qt.QPixmap(size[0], size[1])
                
                AppProfiler.interStart("t8", "    pixmap")
                self.receiver.pix.convertFromImage(image, qt.Qt.ColorOnly)
                #self.pixmapIO.putImage(self.receiver.pix,0,0,image)
         	      
                AppProfiler.interStop("t8")
                
                qt.qApp.unlock()

                AppProfiler.interStop("t4")
                AppProfiler.interStart("t9", "Calling NewPixmap")
                event = qt.QCustomEvent(qt.QEvent.User)
                event.event_name = "Array2Pixmap"
            except:
                sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])
                return None

           
            return event
        
        return None
