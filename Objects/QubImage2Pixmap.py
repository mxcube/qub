import sys
import qt
import QubPixmapTools

from Qub.Tools.QubThread import QubLock
from Qub.Tools.QubThread import QubThreadProcess
from opencv import cv
from QubOpenCv import qtTools

class QubImage2Pixmap :
    class _Idle(qt.QTimer) :
        def __init__(self,skipSmooth) :
            qt.QTimer.__init__(self)
            self.connect(self,qt.SIGNAL('timeout()'),self.__idleCopy)
            self.__plugsNimagesPending = []
            self.__plugs = []
            self.__skipSmooth = skipSmooth
            self.__mutex = qt.QMutex()
            self.__PrevImageNeedZoom = None
            self.__imageZoomProcess = _ImageZoomProcess(self)
        def plug(self,aPlug) :
            if isinstance(aPlug,QubImage2PixmapPlug) :
                aLock = QubLock(self.__mutex)
                aPlug.setManager(self)
                self.__plugs.append(aPlug)
            else :
                raise StandardError('Must be a QubImage2PixmapPlug')
            
        def getPlugs(self) :
            aLock = QubLock(self.__mutex)
            return self.__plugs
        
        def putImage(self,aQImage,aLockFlag = True) :
            aLock = QubLock(self.__mutex,aLockFlag)
            if len(self.__plugs) :
                needZoomFlag = False
                for plug in self.__plugs :
                    zoom = plug.zoom()
                    if zoom.needZoom():
                        needZoomFlag = True
                        break
                self.__PrevImageNeedZoom = aQImage
                if needZoomFlag :
                    self.__imageZoomProcess.putImage(aQImage)
                else :
                    self.appendPendingList([(plug,aQImage,aQImage) for plug in self.__plugs],False)

        def appendPendingList(self,aList,aLock = True) :
            aLock = QubLock(self.__mutex,aLock)
            self.__plugsNimagesPending.append(aList)
            aLock.unLock()
            aQtLock = QubLock(qt.qApp)
            try :
                qt.qApp.lock()
                if not self.isActive() :
                    self.start(0)
            finally:
                qt.qApp.unlock()
                    
        def refresh(self) :
            aLock = QubLock(self.__mutex)
            needzoom = False
            for plug in self.__plugs :
                zoom = plug.zoom()
                if zoom.needZoom():
                    needzoom = True
                    break
            previmage = self.__PrevImageNeedZoom
            if previmage is not None :
                if needzoom and previmage != self.__imageZoomProcess.lastImagePending() :
                    self.__imageZoomProcess.putImage(previmage)
                elif not needzoom :
                    if not len(self.__plugsNimagesPending) :
                        self.putImage(previmage,False)
                
                    
        def __idleCopy(self) :
            self.__copy()
            aLock = QubLock(self.__mutex)
            if not len(self.__plugsNimagesPending) :
                aLock.unLock()
                self.stop()
        
        def __copy(self) :
            aLock = QubLock(self.__mutex)
            self.decim(self.__plugsNimagesPending)
            if len(self.__plugsNimagesPending) :
                plugsNimages = self.__plugsNimagesPending.pop(0)
                aLock.unLock()
                for plug,image,fullSizeImage in plugsNimages :
                    if not plug.isEnd() :
                        try:
                            qt.qApp.lock()
                            pixmap = plug.zoom().getPixmapFrom(image)
                            if plug.setPixmap(pixmap,fullSizeImage) :
                                aLock.lock()
                                self.__plugs.remove(plug)
                                aLock.unLock()
                        finally:
                            qt.qApp.unlock()
                    else :
                        aLock.lock()
                        try:
                            self.__plugs.remove(plug)
                        except:
                            pass
                        aLock.unLock()
        def decim(self,l) :
            lenght = len(l)
            if self.__skipSmooth  and lenght < 25 : # (<25 -> stream is up to 4x)
                nbSkip = lenght / 5
                for x in xrange(nbSkip) :
                    l.pop(0)
            elif lenght > 1 :                      # last
                for x in xrange(lenght - 1) :
                    l.pop(0)
    """
    This class manage the copy between QImage and QPixmap
    """
    def __init__(self,skipSmooth = True) :
        self.__idle = QubImage2Pixmap._Idle(skipSmooth)
        
    def putImage(self,aQImage) :
        """
        Asynchronous Image Put, the copy to pixmap will be made on idle
        """
        self.__idle.putImage(aQImage)

    def plug(self,aQubImage2PixmapPlug) :
        self.__idle.plug(aQubImage2PixmapPlug)

                    
class QubImage2PixmapPlug :
    class Zoom :
        def __init__(self,cnt) :
            self.__cnt = cnt
            self.__zoom = (1,1)
            self.__ox,self.__oy = (0,0)
            self.__width,self.__height = (0,0)
            self.__allimage = True
            self.__mutex = qt.QMutex()
            self._interpolation = cv.CV_INTER_LINEAR
            self.__interpolationInUse = self._interpolation
            
            self.__pixmapIO = [QubPixmapTools.IO(),QubPixmapTools.IO()]
            self.__pixmapbuffer = [qt.QPixmap(),qt.QPixmap()]
            self.__bufferId = 0
            for buffer in self.__pixmapIO :
                buffer.setShmPolicy(QubPixmapTools.IO.ShmKeepAndGrow)

        def zoom(self) :
            aLock = QubLock(self.__mutex)
            return self.__zoom
        def setZoom(self,zoomx,zoomy,keepROI = False) :
            aLock = QubLock(self.__mutex)
            if self.__zoom != (zoomx,zoomy) :
                self.__zoom = (zoomx,zoomy)
                self.__allimage = not keepROI
                aLock.unLock()
                self.__cnt.refresh()
        
        def setRoiNZoom(self,ox,oy,width,height,zoomx,zoomy) :
            aLock = QubLock(self.__mutex)
            self.__allimage = False
            self.__ox,self.__oy,self.__width,self.__height = (ox,oy,width,height)
            self.__zoom = (zoomx,zoomy)
            if self.__zoom < (1,1) :
                self.__interpolationInUse = cv.CV_INTER_NN
            else :
                self.__interpolationInUse = self._interpolation
            aLock.unLock()    
            self.__cnt.refresh()

        def isRoiZoom(self) :
            return not self.__allimage
        
        def roi(self) :
            aLock = QubLock(self.__mutex)
            return (self.__ox,self.__oy,self.__width,self.__height)

               ####### USE by ImageZoomProcess #######
        def needZoom(self) :
            aLock = QubLock(self.__mutex)
            return self.__zoom != (1,1)

        def getZoomedImage(self,imageOpencv) :
            aLock = QubLock(self.__mutex) # LOCK
            width = imageOpencv.width
            height = imageOpencv.height
            if not self.__allimage :
                width = self.__width
                height = self.__height

            width *= self.__zoom[0]
            height *= self.__zoom[1]
            width = int(width)
            height = int(height)
            oldroi = imageOpencv.roi
            roiX,roiY,roiWidth,roiHeight = (0,0,0,0)
            if oldroi is not None :
                roiX,roiY,roiWidth,roiHeight = (oldroi.xOffset,oldroi.yOffset,oldroi.width,oldroi.height)

            if self.__allimage :
                if oldroi is not None :
                    cv.cvResetImageROI(imageOpencv)
            else:
                cv.cvSetImageROI(imageOpencv,cv.cvRect(self.__ox,self.__oy,self.__width,self.__height))
            aLock.unLock()              # UNLOCK

            destImage = cv.cvCreateImage(cv.cvSize(width,height),imageOpencv.depth,imageOpencv.nChannels)

            cv.cvResize(imageOpencv,destImage,self.__interpolationInUse)

            zoomedImage = qtTools.getQImageFromImageOpencv(destImage)

            if oldroi is not None :
                cv.cvSetImageROI(imageOpencv,cv.cvRect(roiX,roiY,roiWidth,roiHeight))
            elif not self.__allimage :
                cv.cvResetImageROI(imageOpencv)
            return zoomedImage
        
        def getPixmapFrom(self,zoomedImage) :
            pixmapbuffer = self.__pixmapbuffer[self.__bufferId % len(self.__pixmapbuffer)]
            pixmapIO = self.__pixmapIO[self.__bufferId % len(self.__pixmapIO)]
            self.__bufferId += 1

            if(pixmapbuffer.width() != zoomedImage.width() or
               pixmapbuffer.height() != zoomedImage.height()) :
                pixmapbuffer.resize(zoomedImage.width(),zoomedImage.height())

            pixmapIO.putImage(pixmapbuffer,0,0,zoomedImage)
            
            return pixmapbuffer

    def __init__(self) :
        self.__endFlag = False
        self._zoom = QubImage2PixmapPlug.Zoom(self)
        self._mgr = None
        
    def zoom(self) :
        return self._zoom
    
    def setPixmap(self,pixmap,image) :
        """
        This methode is call when an image is copied on pixmap
        """
        return True

    def refresh(self) :
        if self._mgr is not None :
            self._mgr.refresh()

    def setEnd(self) :
        """
        this is the end ... of the plug. after this call, the plug will be removed from every polling.
        """
        self.__endFlag = True

    def isEnd(self) :
        return self.__endFlag
    
    def setManager(self,aMgr) :
        self._mgr = aMgr
#Private
class _ImageZoomProcess(QubThreadProcess):
    class _process_struct :
        def __init__(self,image) :
            self.image = image
            self.plugNimage = []
            self.inProgress = False
            self.end = False
            
    def __init__(self,cnt) :
        QubThreadProcess.__init__(self)
        self.__end = False
        self.__cnt = cnt
        self.__mutex = qt.QMutex()
        self.__actif = False
        self.__imageZoomPending = []
        self.__InProgress = []
         
    def getFunc2Process(self) :
        aLock = QubLock(self.__mutex)
        self.__cnt.decim(self.__imageZoomPending)
        self.__InProgress.append(_ImageZoomProcess._process_struct(self.__imageZoomPending.pop(0)))
        if not len(self.__imageZoomPending) :
            self.__actif = False
            aLock.unLock()
            self._threadMgr.pop(self,False)
        return self.zoomProcess

    def lastImagePending(self) :
        aLock = QubLock(self.__mutex)
        lastImagePending = None
        if len(self.__imageZoomPending) :
            lastImagePending = self.__imageZoomPending[-1]
        return lastImagePending
    
    def putImage(self,image) :
        aLock = QubLock(self.__mutex)
        self.__imageZoomPending.append(image)
        if not self.__actif :
            self.__actif = True
            aLock.unLock()
            self._threadMgr.push(self)
            
    def zoomProcess(self) :
        plugs = self.__cnt.getPlugs()
        aLock = QubLock(self.__mutex)
        struct = None
        for s in self.__InProgress :
            if not s.inProgress :
                s.inProgress = True
                struct = s
                break
        aLock.unLock()

        imageOpencv = qtTools.getImageOpencvFromQImage(struct.image)
                
        for plug in plugs :
            zoom = plug.zoom()
            if zoom.needZoom() :
                try:
                    imageZoomed = zoom.getZoomedImage(imageOpencv)
                    struct.plugNimage.append((plug,imageZoomed,struct.image))
                except:
                    sys.excepthook(sys.exc_info()[0],
                                   sys.exc_info()[1],
                                   sys.exc_info()[2])

            else :
                struct.plugNimage.append((plug,struct.image,struct.image))

        aLock.lock()
        struct.end = True
        tmplist = []
        if struct == self.__InProgress[0] :
            lastid = 0
            for i,s in enumerate(self.__InProgress) :
                if s.end :
                    tmplist.append(s.plugNimage)
                    lastid = i
                else:
                    break
            self.__InProgress[0:lastid + 1] = []
        aLock.unLock()
        for plugnimage in tmplist:
            self.__cnt.appendPendingList(plugnimage)

                         ####### TEST #######
if __name__ == "__main__":
    class Image2Pixmap(QubImage2PixmapPlug) :
        def __init__(self,label) :
            QubImage2PixmapPlug.__init__(self)
            self.__label = label
                        
        def setPixmap(self,pixmap,image) :
            self.__label.setPixmap(pixmap)
            return False
        
    import os
    import os.path
    class PutImageTimer(qt.QTimer) :
        def __init__(self,pixmapMgr) :
            qt.QTimer.__init__(self)
            self.connect(self,qt.SIGNAL('timeout()'),self.__putImage)
            self.images = []
            for root,dirs,files in os.walk('/bliss/users/petitdem/TestGui/Image/resize') :
                for file_name in files :
                  basename,ext = os.path.splitext(file_name)
                  if ext == '.jpeg' :
                      self.images.append(qt.QImage(os.path.join(root,file_name)))
                break
            self.__pixmapManager = pixmapMgr
            self.id = 0
            self.start(10)

        def __putImage(self) :
            self.__pixmapManager.putImage(self.images[self.id % len(self.images)])
            self.id += 1
                                      
    a = qt.QApplication([])
    qt.QObject.connect(a,qt.SIGNAL("lastWindowClosed()"),a,qt.SLOT("quit()"))

    dialog = qt.QDialog()
    layout = qt.QHBoxLayout(dialog,11,6,"layout")
    label1 = qt.QLabel(dialog,"label1")
    layout.addWidget(label1)

    label2 = qt.QLabel(dialog,"label2")
    layout.addWidget(label2)

    pixmapMgr = QubImage2Pixmap()

    i2p = Image2Pixmap(label1)
    z = i2p.zoom()
    z.setZoom(1/2.,1/2.)
    i2pzoom = Image2Pixmap(label2)
    zoom = i2pzoom.zoom()
    zoom.setRoiNZoom(100,0,300,200,1,2.5)

    pixmapMgr.plug(i2p)
    pixmapMgr.plug(i2pzoom)

    timer = PutImageTimer(pixmapMgr)
    
    a.setMainWidget(dialog)
    dialog.show()
    a.exec_loop()
