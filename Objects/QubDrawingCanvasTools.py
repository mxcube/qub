import qt
import qtcanvas
##@defgroup DrawingCanvasTools Low level objects drawing
#@brief this is the group of all vector objects which can be put in a simple QCanvas.
#
#HOW TO COOK a new QubDrawingCanvasTools:
# - for all new object with several qtcanvas object base, you need to redefine :
#   - def show(self)
#   - def hide(self)
#   - def setPen(self,pen)
#   - def setCanvas(self,canvas)
#
# - for object acting as a point, you need to redefine :
#   - def move(self,x,y)
#
# - for object acting as a line, you need to redefine :
#   - def setPoints(self,x1,y1,x2,y2)
#
# - for object acting as a surface ie (a simple rectangle define by TOP LEFT and BOTTOM RIGH points),
#you need to redefine :
#   - def move(self,x,y)
#   - def setSize(self,width,height)
#
#
# - if your object need the scrollView, you have to redefine :
#   - def setScrollView(self,scrollView)
# - if your object need the matrix, you have to redefine :
#   - def setMatrix(self,matrix)


##@defgroup DrawingCanvasToolsPoint Point objects
#@brief all drawingObject in this group can be used with Qub::Objects::QubDrawingManager::QubPointDrawingMgr
#@ingroup DrawingCanvasTools
#

##@defgroup DrawingCanvasToolsContainer Stand alone drawing object
#@brief all drawingObject in this group can only be use with Qub::Objects::QubDrawingManager::QubContainerDrawingMgr
#@ingroup DrawingCanvasTools
#

##@defgroup DrawingCanvasToolsPolygone Polygone objects
#@brief all drawing in this group can only be use with Qub::Objects::QubDrawingManager::QubPolygoneDrawingMgr
#@ingroup DrawingCanvasTools
#

##@brief the Ellipse object
#@ingroup DrawingCanvasToolsPoint

class QubCanvasEllipse(qtcanvas.QCanvasEllipse):
    def drawShape(self, p):
        p.drawArc(int(self.x()-self.width()/2+0.5), 
                  int(self.y()-self.height()/2+0.5), 
                  self.width(), self.height(), 
                  self.angleStart(), self.angleLength())       
        
##@brief the Donut Object
#@ingroup DrawingCanvasToolsPoint
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
 

##@brief the Beam Object
#@ingroup DrawingCanvasToolsPoint
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

##@brief this is a simple target with a circle and a cross
#@ingroup DrawingCanvasToolsPoint
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
##@brief simple text with rotation
#@ingroup DrawingCanvasToolsPoint
class QubCanvasText(qtcanvas.QCanvasText) :
    def __init__(self,canvas) :
        qtcanvas.QCanvasText.__init__(self,canvas)
        self.__rotation_angle = 0
    def setRotation(self,angle) :
        self.__rotation_angle = angle
    def rotation(self) :
        return self.__rotation_angle
    def boundingRect(self) :
        rect = qtcanvas.QCanvasText.boundingRect(self)
        if self.__rotation_angle :
            rotMatrix = qt.QWMatrix(1,0,0,1,0,0)
            rotMatrix.translate(rect.x(),rect.y())
            rotMatrix.rotate(self.__rotation_angle)
            rotMatrix.translate(-rect.x(),-rect.y())
            rect = rotMatrix.map(rect)
        return rect
    def draw(self,painter) :
        if self.__rotation_angle :
            painter.translate(self.x(),self.y())
            painter.rotate(self.__rotation_angle)
            painter.translate(-self.x(),-self.y())
        qtcanvas.QCanvasText.draw(self,painter)
        if self.__rotation_angle:
            painter.translate(self.x(),self.y())
            painter.rotate(-self.__rotation_angle)
            painter.translate(-self.x(),-self.y())
##@brief this is a vertical line draw on the height of the canvas
#@ingroup DrawingCanvasToolsPoint
class QubCanvasVLine(qtcanvas.QCanvasLine) :
    def __init__(self,canvas) :
        qtcanvas.QCanvasLine.__init__(self,canvas)

    def move(self,x,y) :
        height = self.canvas().height()
        self.setPoints(x,0,x,height)

##@brief this is a horizontal line draw on the width of the canvas
#@ingroup DrawingCanvasToolsPoint
class QubCanvasHLine(qtcanvas.QCanvasLine) :
    def __init__(self,canvas) :
        qtcanvas.QCanvasLine.__init__(self,canvas)

    def move(self,x,y) :
        width = self.canvas().width()
        self.setPoints(0,y,width,y)

##@brief this object display the scale on bottom left of the image
#@ingroup DrawingCanvasToolsContainer
class QubCanvasScale(qtcanvas.QCanvasLine) :
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
    ##@brief set the display mode
    #
    # - if mode == QubCanvasScale::HORIZONTAL the scale will only be horizontal
    # - if mode == QubCanvasScale::VERTICAL the scale will only be vertical
    # - if mode == QubCanvasScale::BOTH the scale will be horizontal and vertical
    def setMode(self,mode) :
        self.__mode = mode
        self.update()

    ##@brief define autorized values to be display
    #
    #example: if you set [1,10,100] scale display can only be 1nm,10nm,100nm...
    #@param values list of posible values, values must be ascending sort 
    def setAutorizedValues(self,values) :
        self.__autorizeValues = values
        self.update()
    ##@brief set the size of the horizontal pixel
    #@param size values in meter of a pixel
    #@see setYPixelSize
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
    ##@brief set the size of the vertical pixel
    #@param size values in meter of a pixel
    #@see setXPixelSize
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

##@brief Simple ruler
#@ingroup DrawingCanvasToolsContainer
#
#this ruler can manage one or two cursors
class QubCanvasRuler(qtcanvas.QCanvasLine) :
    HORIZONTAL,VERTICAL = range(2)
    MARGIN = 4
    def __init__(self,canvas) :
        qtcanvas.QCanvasLine.__init__(self,canvas)
        self.__positionMode = QubCanvasRuler.HORIZONTAL
        self.__scrollViewPercent = 0.8
        self.__scrollView = None

        self.__limits = []
        self.__positions = []
        self.__textlimits = []
        self.__cursor = []
        self.__label = []

        self.__color = self.pen().color()
        self.__format = '%.2f'
        self.__globalShow = False
        
    ##@brief set where the ruler will be display on the image
    #@param mode can be:
    # - <b>HORIZONTAL</b> horizontal on the image's top
    # - <b>VERTICAL</b> vertical on the image's right
    def setPositionMode(self,mode) :
        try:
            self.__positionMode = mode
            self.update()
        except:
            import traceback
            traceback.print_exc()
            
    ##@brief set text label
    def setLabel(self,cursorID,text) :
        if 0 <= cursorID <= 1 :
            while len(self.__label) <= cursorID :
                self.__createCursor()
            self.__label[cursorID].setText(text)

    ##@brief set the cursor position
    def setCursorPosition(self,cursorID,position) :
        if 0 <= cursorID <= 1 :
            while len(self.__positions) <= cursorID :
                self.__createCursor()
            self.__positions[cursorID] = position
            self.update()
        else:
            raise StandardError('can only manage one or two cursor')
    ##@brief set the limit of a cursor
    def setLimits(self,cursorID,low,high) :
        if 0 <= cursorID <= 1 :
            while len(self.__limits) <= cursorID :
                self.__createCursor()
            self.__limits[cursorID] = (low,high)
            self.__textlimits[cursorID][0].setText(self.__format % low)
            self.__textlimits[cursorID][1].setText(self.__format % high)
            self.update()
    
    def setScrollView(self,scrollView) :
        self.__scrollView = scrollView

    def show(self) :
        self.__globalShow = True
        self.update()
        for t in self.__textlimits :
            for widget in t: widget.show()
            
        for l in [self.__label,self.__cursor] :
            for w in l :
                w.show()
        qtcanvas.QCanvasLine.show(self)
        
    def hide(self) :
        self.__globalShow = False
        for t in self.__textlimits :
            for widget in t: widget.hide()
            
        for l in [self.__label,self.__cursor] :
            for w in l :
                w.hide()
        qtcanvas.QCanvasLine.hide(self)
    
    def setPen(self,pen) :
        color = pen.color()
        for label in self.__label:
            label.setColor(color)
        for limits in self.__textlimits :
            for limitWidget in limits:
                limitWidget.setColor(color)
        qtcanvas.QCanvasLine.setPen(self,pen)
        for cursor in self.__cursor :
            brush = cursor.brush()
            brush.setColor(color)
            cursor.setBrush(brush)
    def update(self) :
        try:
            if self.__globalShow and self.__limits :
                if self.__scrollView is None :
                    (useSizeX,useSizeY) = self.canvas().width(),self.canvas().height()
                    (xOri,yOri) = 0,0
                else :
                    (xOri,yOri) = (self.__scrollView.contentsX(),self.__scrollView.contentsY())
                    (useSizeX,useSizeY) = (min(self.canvas().width(),self.__scrollView.visibleWidth()),
                                           min(self.__scrollView.visibleHeight(),self.canvas().height()))

                rotationAngle = 0
                if self.__positionMode == QubCanvasRuler.VERTICAL :
                    rotationAngle = 90
                for l,h in self.__textlimits :
                    l.setRotation(rotationAngle)
                    h.setRotation(rotationAngle)
                for l in self.__label :
                    l.setRotation(rotationAngle)

                if self.__positionMode == QubCanvasRuler.HORIZONTAL :
                    textBBox = [(x.boundingRect(),y.boundingRect()) for x,y in self.__textlimits]
                    maxLowWidth,maxHighWidth = 0,0
                    for lowRect,highRect in textBBox :
                        maxLowWidth += lowRect.width()
                        maxHighWidth += highRect.width()
                    spareSize = useSizeX - maxLowWidth - maxHighWidth - QubCanvasRuler.MARGIN
                    spareSize *= self.__scrollViewPercent
                    centerX = (useSizeX / 2) + xOri
                    textHeight = self.__textlimits[0][0].boundingRect().height()
                    for i,(ll,hl) in enumerate(self.__textlimits) :
                        ll.move(centerX - (spareSize + QubCanvasRuler.MARGIN) / 2 - ll.boundingRect().width(),
                                QubCanvasRuler.MARGIN + yOri + (textHeight + QubCanvasRuler.MARGIN / 2) * i)
                        hl.move(centerX + (spareSize + QubCanvasRuler.MARGIN) / 2,
                                QubCanvasRuler.MARGIN + yOri + (textHeight + QubCanvasRuler.MARGIN / 2) * i)
                    y0Line = QubCanvasRuler.MARGIN + yOri + textHeight
                    self.setPoints(centerX - spareSize / 2, y0Line,centerX + spareSize / 2,y0Line)
                    hTriangle = -textHeight
                    X0position = []

                    for pos,(ll,lh),cursor in zip(self.__positions,self.__limits,self.__cursor) :
                        diff = lh -ll
                        offsetPix = (pos - ll) * spareSize / diff
                        x0 = centerX - spareSize / 2 + offsetPix
                        y1Line = y0Line + hTriangle
                        xMin = x0 - hTriangle / 2
                        xMax = x0 + hTriangle / 2
                        array = qt.QPointArray()
                        array.putPoints(0,[xMin,y1Line,xMax,y1Line,x0,y0Line])
                        cursor.setPoints(array)
                        hTriangle = - hTriangle
                        X0position.append(x0)
                    labelOffset = (abs(hTriangle) + QubCanvasRuler.MARGIN) / 2
                    for label,x0,(ll,hl) in zip(self.__label,X0position,self.__textlimits) :
                        hlRect = hl.boundingRect()
                        label.move(x0 + labelOffset,hlRect.y())
                        labelRect = label.boundingRect()
                        if labelRect.intersects(hlRect) :
                            label.move(x0 - labelOffset - labelRect.width(),hlRect.y())
                else:
                    textBBox = [(x.boundingRect(),y.boundingRect()) for x,y in self.__textlimits]
                    maxLowHeight,maxHightHeight = 0,0
                    for lowRect,hightRect in textBBox :
                        maxLowHeight += lowRect.height()
                        maxHightHeight += hightRect.height()
                    spareSize = useSizeY - maxLowHeight - maxHightHeight - QubCanvasRuler.MARGIN
                    spareSize *= self.__scrollViewPercent
                    centerY = (useSizeY / 2) + yOri
                    textHeight = self.__textlimits[0][0].boundingRect().width()
                    for i,(ll,hl) in enumerate(self.__textlimits) :
                        ll.move(xOri + useSizeX - (QubCanvasRuler.MARGIN + (textHeight + QubCanvasRuler.MARGIN / 2) * i),
                                centerY - (spareSize + QubCanvasRuler.MARGIN) / 2 - ll.boundingRect().height())
                        hl.move(ll.x(),
                                centerY + (spareSize + QubCanvasRuler.MARGIN) / 2)
                    x0Line = xOri + useSizeX - (QubCanvasRuler.MARGIN + textHeight)
                    self.setPoints(x0Line,centerY - spareSize / 2,x0Line,centerY + spareSize / 2)
                    hTriangle = textHeight
                    Y0position = []

                    for pos,(ll,lh),cursor in zip(self.__positions,self.__limits,self.__cursor) :
                        diff = lh - ll
                        offsetPix = (pos - ll) * spareSize / diff
                        y0 = centerY - spareSize / 2 + offsetPix
                        x1Line = x0Line + hTriangle
                        yMin = y0 - hTriangle / 2
                        yMax = y0 + hTriangle / 2
                        array = qt.QPointArray()
                        array.putPoints(0,[x1Line,yMin,x1Line,yMax,x0Line,y0])
                        cursor.setPoints(array)
                        hTriangle = -hTriangle
                        Y0position.append(y0)
                        
                    labelOffset = (abs(hTriangle) + QubCanvasRuler.MARGIN) / 2
                    for label,y0,(ll,hl) in zip(self.__label,Y0position,self.__textlimits) :
                        hlRect = hl.boundingRect()
                        label.move(hl.x(),y0 + labelOffset)
                        labelRect = label.boundingRect()
                        if labelRect.intersects(hlRect) :
                            label.move(hl.x(),y0 - labelOffset - labelRect.height())
        except:
            import traceback
            traceback.print_exc()
            
    def __createCursor(self) :
        try:
            canvas = self.canvas()
            self.__limits.append((0,1))
            self.__positions.append(0)
            self.__textlimits.append((QubCanvasText(canvas),QubCanvasText(canvas)))
            poly = qtcanvas.QCanvasPolygon(canvas)
            brush = poly.brush()
            brush.setStyle(qt.Qt.SolidPattern)
            poly.setBrush(brush)
            self.__cursor.append(poly)
            self.__label.append(QubCanvasText(canvas))
        except:
            import traceback
            traceback.print_exc()
            
##@brief drawing object to display two line with one same corner
#
#it is use for an angle measurement
#@ingroup DrawingCanvasToolsPolygone
class QubCanvasAngle(qtcanvas.QCanvasLine) :
    def __init__(self,canvas) :
        qtcanvas.QCanvasLine.__init__(self,canvas)
        self.__secLine = None
        self.__showFlag = False
        
    def move(self,x,y,point_id) :
        if point_id == 0 :
            if self.__secLine is None : # Init
                self.setPoints(x,y,x,y)
            else:                       # Modif
                for line in [self,self.__secLine] :
                    endPoint = line.endPoint()
                    line.setPoints(x,y,endPoint.x(),endPoint.y())
        elif point_id == 1 :
            firstPoint = self.startPoint()
            self.setPoints(firstPoint.x(),firstPoint.y(),x,y)
        else:
            if self.__secLine is None :
                self.__secLine = qtcanvas.QCanvasLine(self.canvas())
                self.__secLine.setPen(self.pen())
                if self.__showFlag :
                    self.__secLine.show()
            firstPoint = self.startPoint()
            self.__secLine.setPoints(firstPoint.x(),firstPoint.y(),x,y)
            return True                 # END OF POLYGONE
                    
    def show(self) :
        qtcanvas.QCanvasLine.show(self)
        if self.__secLine is not None :
            self.__secLine.show()
        self.__showFlag = True

    def hide(self) :
        qtcanvas.QCanvasLine.hide(self)
        if self.__secLine is not None :
            self.__secLine.hide()
        self.__showFlag = False

    def setPen(self,pen) :
        qtcanvas.QCanvasLine.setPen(self,pen)
        if self.__secLine is not None :
            self.__secLine.setPen(pen)

    def setCanvas(self,aCanvas) :
        qtcanvas.QCanvasLine.setCanvas(self,aCanvas)
        if self.__secLine is not None :
            self.__secLine.setCanvas(aCanvas)
