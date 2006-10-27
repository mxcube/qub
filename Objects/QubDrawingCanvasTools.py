import qt
import qtcanvas
"""
this file group all vector objects which can be put in a simple QCanvas.

HOW TO COOK a new QubDrawingCanvasTools:
for all new object with several qtcanvas object base, you need to redefine :
       -> def show(self)
       -> def hide(self)
       -> def setPen(self,pen)
       -> def setCanvas(self,canvas)
for object acting as a point, you need to redefine :
       -> def move(self,x,y)
for object acting as a line, you need to redefine :
       -> def setPoints(self,x1,y1,x2,y2)
for object acting as a surface ie (a simple rectangle define by TOP LEFT and BOTTOM RIGH points),
you need to redefine :
       -> def move(self,x,y)
       -> def setSize(self,width,height)
if your object need the scrollView, you have to redefine :
       -> def setScrollView(self,scrollView)
if your object need the matrix, you have to redefine :
       -> def setMatrix(self,matrix)
"""
################################################################################
####################           QubCanvasEllipse               ##################
################################################################################
class QubCanvasEllipse(qtcanvas.QCanvasEllipse):
    def drawShape(self, p):
        p.drawArc(int(self.x()-self.width()/2+0.5), 
                  int(self.y()-self.height()/2+0.5), 
                  self.width(), self.height(), 
                  self.angleStart(), self.angleLength())       
        
################################################################################
####################           QubCanvasDonut                 ##################
################################################################################
class QubCanvasDonut(qtcanvas.QCanvasEllipse):
    """
    """
    def setClip(self, w, h):
        self.win = w
        self.hin = h
             
    def drawShape(self, p):
        try:
            xout = int(self.x() - self.width()/2+0.5)
            yout = int(self.y() - self.height()/2+0.5)
            
            xin  = int(self.x() - self.win/2+0.5)
            yin  = int(self.y() - self.hin/2+0.5)
            
            self.regionout = QRegion(xout, yout,
                                     self.width() + 2,
                                     self.height()+2, 
                                     QRegion.Ellipse)
            
            self.regionin  = QRegion(xin, yin, self.win, self.hin,
                                     QRegion.Ellipse)
            self.region = self.regionout.subtract(self.regionin)
            
            p.setClipRegion(self.region, QPainter.CoordPainter)
            p.setPen(Qt.NoPen)
            p.drawEllipse(xout, yout, self.width(), self.height())
            
            p.setClipping(0)       
        except:
            sys.excepthook(sys.exc_info()[0],
                       sys.exc_info()[1],
                       sys.exc_info()[2])
 

################################################################################
####################           QubCanvasEllipse               ##################
################################################################################
class QubCanvasBeam(QubCanvasEllipse):
    def __init__(self,canvas) :
        QubCanvasEllipse.__init__(self, 29,19,0,5760, canvas)
        
        self.__centerE = QubCanvasEllipse(7,7,0,5760, canvas)

    def move(self,x,y) :
        QubCanvasEllipse.move(self,x,y)
        self.__centerE.move(x, y)

    def show(self) :
        QubCanvasEllipse.show(self)
        self.__centerE.show()

    def hide(self) :
        QubCanvasEllipse.hide(self)
        self.__centerE.hide()

    def setPen(self,pen) :
        QubCanvasEllipse.setPen(self,pen)
        self.__centerE.setPen(pen)

    def setCanvas(self,aCanvas) :
        QubCanvasEllipse.setCanvas(self,aCanvas)
        self.__centerE.setCanvas(aCanvas)

################################################################################
####################           QubCanvasTarget                ##################
################################################################################
class QubCanvasTarget(QubCanvasEllipse) :
    def __init__(self,canvas) :
        self.__pointWidth = 20
        qtcanvas.QCanvasItem.__init__(self,self.__pointWidth,self.__pointWidth,canvas)

        self.__hLine = qtcanvas.QCanvasLine(canvas)
        self.__hLine.setPoints(0,0,self.__pointWidth,self.__pointWidth)
        self.__vLine = qtcanvas.QCanvasLine(canvas)
        self.__vLine.setPoints(0,self.__pointWidth,self.__pointWidth,0)

    def move(self,x,y) :
        QubCanvasEllipse.move(self,x,y)
        self.__hLine.move(x - self.__pointWidth / 2,y - self.__pointWidth / 2)
        self.__vLine.move(x - self.__pointWidth / 2,y - self.__pointWidth / 2)

    def show(self) :
        QubCanvasEllipse.show(self)
        self.__hLine.show()
        self.__vLine.show()

    def hide(self) :
        QubCanvasEllipse.hide(self)
        self.__hLine.hide()
        self.__vLine.hide()

    def drawShape(self,p) :
        QubCanvasEllipse.drawShape(self,p)
        self.__hLine.drawShape(p)
        self.__vLine.drawShape(p)

    def setCanvas(self,canvas) :
        QubCanvasEllipse.setCanvas(self,canvas)
        self.__hLine.setCanvas(canvas)
        self.__vLine.setCanvas(canvas)

    def setPen(self,pen) :
        QubCanvasEllipse.setPen(self,pen)
        self.__hLine.setPen(pen)
        self.__vLine.setPen(pen)

################################################################################
####################              QubVLine                    ##################
################################################################################

class QubCanvasVLine(qtcanvas.QCanvasLine) :
    def __init__(self,canvas) :
        qtcanvas.QCanvasLine.__init__(self,canvas)

    def move(self,x,y) :
        height = self.canvas().height()
        self.setPoints(x,0,x,height)

################################################################################
####################              QubHLine                    ##################
################################################################################

class QubCanvasHLine(qtcanvas.QCanvasLine) :
    def __init__(self,canvas) :
        qtcanvas.QCanvasLine.__init__(self,canvas)

    def move(self,x,y) :
        width = self.canvas().width()
        self.setPoints(0,y,width,y)

################################################################################
####################           QubCanvasScale                 ##################
################################################################################

class QubCanvasScale(qtcanvas.QCanvasItem) :
    HORIZONTAL,VERTICAL,BOTH = (0x1,0x2,0x3)
    def __init__(self,canvas) :
        color = qt.QColor('green')
        self.__hLine = qtcanvas.QCanvasLine(canvas)
        self.__hLine.setPen(qt.QPen(color,4))
        self.__hText = qtcanvas.QCanvasText(canvas)
        self.__hText.setColor(color)
        
        self.__vLine = qtcanvas.QCanvasLine(canvas)
        self.__vLine.setPen(qt.QPen(color,4))
        self.__vText = qtcanvas.QCanvasText(canvas)
        self.__vText.setColor(color)

        self.__globalShow = False   # remember if the widget is shown
        self.__xPixelSize = 0
        self.__yPixelSize = 0
        self.__mode = QubCanvasScale.BOTH
        self.__unit = [(1e-3,'mm'),(1e-6,'\xb5m'),(1e-9,'nm')]
        self.__autorizeValues = [1,2,5,10,20,50,100,200,500]

        self.__scrollView = None
        self.__matrix = None
        self.__canvas = canvas
        
    def setMode(self,mode) :
        self.__mode = mode
        self.update()

    def setAutorizedValues(self,values) :
        self.__autorizeValues = values
        self.update()
        
    def setXPixelSize(self,size) :
        try:
            self.__xPixelSize = abs(size)
        except:
            self.__xPixelSize = 0
        if(self.__globalShow and self.__mode & QubCanvasScale.HORIZONTAL and self.__xPixelSize) :
            self.__hText.show()
            self.__hLine.show()
            self.update()
        else:
            self.__hText.hide()
            self.__hLine.hide()
            
    def setYPixelSize(self,size) :
        try:
            self.__yPixelSize = abs(size)
        except:
            self.__yPixelSize = 0
        if self.__vText is not None :
            if (self.__globalShow and self.__mode & QubCanvasScale.VERTICAL and self.__yPixelSize) :
                self.__vText.show()
                self.__vLine.show()
                self.update()
            else :
                self.__vText.hide()
                self.__vLine.hide()

    def show(self) :
        self.__globalShow = True
        self.setXPixelSize(self.__xPixelSize)
        self.setYPixelSize(self.__yPixelSize)
        self.update()
        
    def hide(self) :
        self.__globalShow = False
        self.__vText.hide()
        self.__vLine.hide()
        self.__hText.hide()
        self.__hLine.hide()
    
    def update(self) :
        if self.__globalShow :
            (canvasX,canvasY) = (self.__canvas.width(),self.__canvas.height())
            if self.__scrollView is None :
                (viewSizeX,viewSizeY) = canvasX,canvasY
                (xOri,yOri) = 0,0
            else :
                (xOri,yOri) = (self.__scrollView.contentsX(),self.__scrollView.contentsY())
                (viewSizeX,viewSizeY) = (self.__scrollView.visibleWidth(),self.__scrollView.visibleHeight())

            (nbXPixel,nbYPixel) =  min(canvasX,viewSizeX),min(canvasY,viewSizeY)
            (widthUse,heightUse) = (nbXPixel,nbYPixel)

            if self.__matrix is None :
                (xOriCrop,yOriCrop) = 0,0
            else :
                (xOriCrop,yOriCrop) = self.__matrix.invert()[0].map(0,0)
                
            if self.__mode & QubCanvasScale.HORIZONTAL :
                nbXPixel /= 4 # 1/4 of image display
                if self.__matrix is None :
                    y1,y2 = 0,nbXPixel
                else:
                    dummy,y1 = self.__matrix.invert()[0].map(0,0)
                    dummy,y2 = self.__matrix.invert()[0].map(0,nbXPixel)
                unit,XSize = self.__getUnitNAuthValue((y2 - y1) * self.__xPixelSize)
                try:
                    nbXPixel = int(XSize * unit[0] / self.__xPixelSize)
                    if self.__matrix is not None :
                        (nbXPixel,dummy) = self.__matrix.map(nbXPixel + xOriCrop,0)
                    y0 = heightUse - 10 + yOri
                    self.__hLine.setPoints (14 + xOri,y0,nbXPixel + 14 + xOri,y0)
                    self.__hText.setText('%d %s' % (XSize,unit[1]))
                    rect = self.__hText.boundingRect()
                    xTextPos = nbXPixel + 14 - rect.width()
                    if xTextPos < 14 :
                        self.__hText.move(nbXPixel + 16 + xOri,y0 - rect.height() / 2)
                    else:
                        self.__hText.move(xTextPos + xOri,y0 - rect.height() - 2)
                except:
                    pass
                
            if self.__mode & QubCanvasScale.VERTICAL :
                nbYPixel /= 4
                if self.__matrix is None :
                    y1,y2 = 0,nbYPixel
                else:
                    dummy,y1 = self.__matrix.invert()[0].map(0,0)
                    dummy,y2 = self.__matrix.invert()[0].map(0,nbYPixel)
                unit,YSize = self.__getUnitNAuthValue((y2 - y1) * self.__yPixelSize)
                try:
                    nbYPixel = int(YSize * unit[0] / self.__yPixelSize)
                    if self.__matrix is not None :
                        (dummy,nbYPixel) = self.__matrix.map(0,nbYPixel + yOriCrop)
                    y0 = heightUse - 14 + yOri
                    self.__vLine.setPoints(10 + xOri,y0,10 + xOri,y0 - nbYPixel)
                    self.__vText.move(15 + xOri,y0 - nbYPixel)
                    self.__vText.setText('%d %s' % (YSize,unit[1]))
                except :
                    pass

            if self.__mode & QubCanvasScale.BOTH :
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

    def setScrollView(self,scrollView) :
        self.__scrollView = scrollView

    def setMatrix(self,matrix) :
        self.__matrix = matrix

    def setCanvas(self,canvas) :
        self.__canvas = canvas
        self.__vText.setCanvas(canvas)
        self.__vLine.setCanvas(canvas)
        self.__hText.setCanvas(canvas)
        self.__hLine.setCanvas(canvas)

    def isVisible(self) :
        return self.__globalShow
    
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

