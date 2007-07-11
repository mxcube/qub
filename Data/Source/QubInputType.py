import pickle
import numpy
import struct
import qt

class QubInputType:
    def __init__(self,**keys) :
        pass
    ##@brief this methode is called to display info about the value
    #
    #ie : "Select energy between 2 and 8 kev"
    #@return string info
    def getTooltipInfo(self) :
        pass
    ##@brief get a validator for widget like QLineEdit
    #
    def getValidator(self,parent) :
        pass
    ##@brief get mime object for drag and drop data
    #
    #@return a mime object that can decode drag or drop data
    def getMimeType(self) :
        pass

##@brief Type int class
class QubInputTypeInt(QubInputType) :
    def __init__(self,minval = None,maxval = None,**keys) :
        QubInputType.__init__(self,**keys)
        self._minVal = minval
        self._maxVal = maxval

    def getTooltipInfo(self) :
        if self._maxVal is not None and self._minVal is not None:
            return 'Set a value between %d and %d' % (self._minVal,self._maxVal)
        else:
            return 'Set a int value'

    def getValidator(self,parent) :
        if self._maxVal is not None and self._minVal is not None:
            return qt.QIntValidator(self._minVal,self._maxVal,parent)
        else:
            return qt.QIntValidator(parent)

class QubInputTypeFloat(QubInputType):
    def __init__(self,minval = None,maxval = None,decimals = None,**keys) :
        QubInputType.__init__(self,**keys)
        self._minVal = minval
        self._maxVal = maxval
        self._decimal = decimals

    def getTooltipInfo(self) :
        if self._maxVal is not None and self._minVal is not None:
            if self._decimal is not None:
                formatText = 'Set a value between %%.%df and %%.%df' % (self._decimal,self._decimal)
            else:
                formatText = 'Set a value between %f and %f'
            infoText = formatText % (self._minVal,self._maxVal)
        else:
            infoText = 'Set a int value'
        return infoText

    def getValidator(self,parent) :
        if self._maxVal is not None and self._minVal is not None:
            return qt.QDoubleValidator(self._minVal,self._maxVal,self._decimal or 0,parent)
        else:
            return qt.QDoubleValidator(parent)

class QubInputTypeString(QubInputType):
    ##@brief contructor of a simple string input Type or
    #an input that match a regular exp
    #@param pattern the regular expression
    def __init__(self,pattern = None,**keys) :
        QubInputType.__init__(self,**keys)
        self._pattern = pattern

    def getTooltipInfo(self) :
        if self._pattern is not None :
            return 'Set a string match this pattern %s' % self._pattern

    def getValidator(self) :
        pass                            # TODO (if Need)

class QubInputDataType(QubInputType) :
    class _drag(qt.QStoredDrag) :
        def __init__(self,mimes = [],widgetDragSource = None,name = '') :
            qt.QStoredDrag.__init__(self,'Typedata',widgetDragSource,name)

            if isinstance(mimes,list) : self.__format = mimes
            else: self.__format = ['Typedata',mimes]
            self.__Type = None
            
        def format(self,index = 0) :
            if 0 <= index  < len(self.__format) :
                return self.__format[index]
        ##@brief encode data for drag a QubInputType class
        #
        def setType(self,Type) :
            self.__Type = Type
        

        def canDecode(self,mimType) :
            aReturnFlag = False
            for format in self.__format:
                aReturnFlag = mimType.provide(format)
                if aReturnFlag: break
            return aReturnFlag

        def decode(self,mimType,TypeClass) :
            aReturnFlag = False
            if mimType:
                bArray = mimType.encodedData('Typedata')
                aReturnFlag = TypeClass.setByteArray(bArray)
            return aReturnFlag
        
        def encodedData(self,mimeType) :
            bArray = qt.QByteArray()
            if self.provide(mimeType) :
                bArray = self.__Type.getByteArray()
            return bArray

    def __init__(self,name = '',data_class = None,info = None,**keys) :
        self._data_class = data_class
        self._info = info
        self._name = name
        
    def setDataClass(self,data_class) :
        self._data_class = data_class

    def dataClass(self) :
        return self._data_class
    
    def setInfo(self,info) :
        self._info = info

    def info(self) :
        return self._info

    def setName(self,name) :
        self._name = name

    def name(self) :
        return self._name
    
    def getByteArray(self) :
        message = pickle.dumps(self)
        bArray = qt.QByteArray(len(message))
        bArray.assign(message)
        return bArray
    
    def loadFromData(self,bArray) :
        aReturnFlag = False
        try:
            message = str(bArray)
            TypeClass = pickle.loads(message)
            self._data_class = TypeClass.dataArray()
            self._info = TypeClass.info()
            self._name = TypeClass.name()
            aReturnFlag = True
        finally:
            return aReturnFlag

    def getMimeType(self,widgetDragSource) :
        return QubInputTypeData._drag(widgetDragSource = widgetDragSource)
        
class QubInputTypeDataImage(QubInputDataType) :
    def __init__(self,**keys) :
        QubInputDataType.__init__(self,**keys)

    def getMimeType(self,widgetDragSource) :
        return QubInputTypeData._drag(mimes = ['Typedata/image'],
                                   widgetDragSource = widgetDragSource)
