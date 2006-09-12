import qtcanvas

################################################################################
####################           QubCanvasEllipse               ##################
################################################################################
class QubCanvasEllipse(qtcanvas.QCanvasEllipse):
    def drawShape(self, p):
        p.drawArc(int(self.x()-self.width()/2+0.5), 
                  int(self.y()-self.height()/2+0.5), 
                  self.width(), self.height(), 
                  self.angleStart(), self.angleLength())       

    def removeInCanvas(self) :
        self.setCanvas(None)
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

    def removeInCanvas(self) :
        QubCanvasEllipse.removeInCanvas(self)
        self.__hLine.setCanvas(None)
        self.__vLine.setCanvas(None)

