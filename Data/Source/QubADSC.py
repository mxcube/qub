import re

import numpy

from Qub.Data.Class.QubDataClass import QubDataImage

from Qub.Plugins.QubDataIOPlugin import QubDataIOPlugin

from Qub.Data.StreamIO.QubDataFileStreamIO import QubDataFileStreamIO

class QubADSC(QubDataIOPlugin) :
    class ReadHandler(QubDataIOPlugin.ReadHandler) :
        def __init__(self,fd) :
            QubDataIOPlugin.ReadHandler.__init__(self)
            self.__fd = None
            fd.seek(0,0)
            if fd.readline() == '{\n' : # CAN be a ADSC file
                try:
                    headerStringSize = fd.readline()
                    key,val = headerStringSize.split()
                    if not key.startswith('HEADER_BYTES') :
                        self.__raiseError(fd)
                    headerSize = int(val.replace(';',''))
                    header = fd.read(headerSize)
                except:
                    self.__raiseError(fd)
                else:
                    fd.seek(0)
                    try:
                        header = fd.read(headerSize)
                        exp = re.compile('([A-Z0-9_]+)=.*?([A-Za-z0-9_]+);')
                        self.__info = dict(exp.findall(header))
                    except:
                        self.__raiseError(fd)
                    self.__fd = fd
            else:
                self.__raiseError(fd)

        def __raiseError(self,fd) :
            fd.seek(0)
            raise IOError('Not a ADSC image file')

        def getNumData(self) :
            return 1

        def get(self,index = 0,roi = None,**keys) :
            headerOffset = int(self.__info['HEADER_BYTES'])
            self.__fd.seek(headerOffset)
            format = ''
## TODO
##            if self.__info['BYTE_ORDER'] == 'little_endian' : format = '<'
##            else: format = '>'

            width = int(self.__info['SIZE1'])
            height = int(self.__info['SIZE2'])
            
            if self.__info['TYPE'] == 'unsigned_short' :
                dtype = numpy.uint16
            if roi is not None:
                x,y,w,h = roi
                self.__fd.seek((y * width + x) * 2,1)
                seekStep = (width - w) * 2
                lineSize = w * 2
                dataRaw = ''
                width,height = w,h
                while h:
                    h -= 1
                    dataRaw += self.__fd.read(lineSize)
                    self.__fd.seek(seekStep,1)
            else:
                dataRaw = self.__fd.read()

            data = numpy.frombuffer(dataRaw,dtype=dtype)
            data.shape = height,width
            return data
            
        def info(self,index = 0) :
            return self.__info

        def getDataSource(self) :
            basename = os.path.split(self.__fd.name)[1]
            parent = QubDataImage(read_plugin = QubDataFileStreamIO(filepath = self.__fd.name,
                                                                  index = 0,plugInClass = QubADSC),
                                  name = 'File : %s ' % basename,key = self.__fd.name)
            return {parent : {}}

    def __init__(self,**keys) :
        QubDataIOPlugin.__init__(self,**keys)

    def getMode(self) :
        return QubDataIOPlugin.READ

    def extensionFilter(self) :
        return ['.img']

    def readHandler(self,fd) :
        return QubADSC.ReadHandler(fd)
