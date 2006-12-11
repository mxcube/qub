import math

class QubAngleConstraint :
    def __init__(self,angle) :
        self.__xPixelSize = 0
        self.__yPixelSize = 0
        self.setAngle(angle)

    def setXPixelSize(self,size) :
        try:
            self.__xPixelSize = abs(size)
        except:
            self.__xPixelSize = 0

    def setYPixelSize(self,size) :
        try:
            self.__yPixelSize = abs(size)
        except:
            self.__yPixelSize = 0

    def setAngle(self,angle) :
        self.__contraintAngle = angle * math.pi / 180

    def calc(self,x1,y1,x2,y2) :
        if self.__contraintAngle != math.pi / 2 :
            X = x2 - x1
            if self.__xPixelSize :
                X *= self.__xPixelSize
            X = X ** 2
            Y = math.sqrt((X / (math.cos(self.__contraintAngle) ** 2)) - X)
            if self.__yPixelSize :
                Y /= self.__yPixelSize
            if y2 - y1 < 0:
                Y = -Y
            y2 = Y + y1
        else :  x2 = x1                 # 90 deg
        return (x1,y1,x2,y2)
