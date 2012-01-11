import struct, string
import os
import Image
import numpy

from Qub.Plugins.QubDataIOPlugin import QubDataIOPlugin

from Qub.Data.Class.QubDataClass import QubDataImage

from Qub.Data.StreamIO.QubDataFileStreamIO import QubDataFileStreamIO

class QubMarCCD(QubDataIOPlugin) :
    class ReadHandler(QubDataIOPlugin.ReadHandler) :
        def __init__(self,fd) :
            QubDataIOPlugin.ReadHandler.__init__(self)
##            fd.seek(2464,0)
##            header = fd.read(4096 - 2464)
##            if header.startswith('Created by: marccd') : # BINGO
            self.__header = MccdHeader(fd)
##            else: raise IOError('Not a MarCCD image file')
            fd.seek(0,0)


            self.__image = Image.open(fd)
            if(self.__image.format != 'TIFF' or self.__image.info['compression'] != 'raw' or
               self.__image.mode != 'I;16') :
                raise IOError('Type format not managed for MarCCD image file')
            else:
                self.__fileName = fd.name

        def getNumData(self) :
            return 1

        def get(self,index = 0,roi = None,**keys) :
            if roi is not None:
                x,y,w,h = roi
                im = self.__image.crop((x,y,x+w,y+h))
            else:
                im = self.__image
            s = im.tostring()
            returnArray = numpy.frombuffer(s,dtype=numpy.uint16)
            returnArray.shape = im.size
            return returnArray

        def info(self,index = 0) :
            info = {}
            info.update(self.__header.getGonio())
            info.update(self.__header.getDetector())
            info.update(self.__header.getFile())
            return info

        def getDataSource(self) :
            basename = os.path.split(self.__fileName)[1]
            parent = QubDataImage(read_plugin = QubDataFileStreamIO(filepath = self.__fileName,
                                                                  index = 0,plugInClass = QubMarCCD),
                                  name = 'File : %s ' % basename,key = self.__fileName)
            return {parent : {}}
        
    def __init__(self,**keys) :
        QubDataIOPlugin.__init__(self,**keys)

    def getMode(self) :
        return QubDataIOPlugin.READ

    def extensionFilter(self) :
        return ['.mccd']

    def readHandler(self,fd) :
        return QubMarCCD.ReadHandler(fd)




class MccdHeader:
	gonioHead= [	"xtal_to_detector",
        		"beam_x",
        		"beam_y",
        		"integration_time",
        		"exposure_time",
        		"readout_time",
        		"nreads",
        		"start_twotheta",
        		"start_omega",
        		"start_chi",
        		"start_kappa",
        		"start_phi",
        		"start_delta",
        		"start_gamma",
        		"start_xtal_to_detector",
        		"end_twotheta",
        		"end_omega",
        		"end_chi",
        		"end_kappa",
        		"end_phi",
        		"end_delta",
        		"end_gamma",
        		"end_xtal_to_detector",
        		"rotation_axis",
        		"rotation_range",
        		"detector_rotx",
        		"detector_roty",
        		"detector_rotz"
	]

	detectorHead= [	"detector_type",
			"pixelsize_x",
			"pixelsize_y"
	]

	fileHead= [	("filetitle", 128),
			("filepath", 128),
			("filename", 64),
			("acquire_timestamp", 32),
			("header_timestamp", 32),
			("save_timestamp", 32),
			("file_comments", 512)
	]

	def __init__(self, fd):
		self.gonioValue= []
		self.detectorValue= []
		self.fileValue= []
		self.datasetValue= None
		self.__read(fd)
		self.__unpack()

	def __read(self, fp):
		fp.seek(1024)
		self.raw= fp.read(3072)


	def __unpack(self):
		self.__unpack_gonio()
		self.__unpack_detector()
		self.__unpack_file()
		self.__unpack_dataset()

	def __unpack_gonio(self):
		idx= 640
		size= struct.calcsize("i")
		for nb in range(len(self.gonioHead)):
			self.gonioValue.append(struct.unpack("i", self.raw[idx+nb*size:idx+(nb+1)*size])[0])

	def __unpack_detector(self):
		idx= 768
		size= struct.calcsize("i")
		for nb in range(len(self.detectorHead)):
			self.detectorValue.append(struct.unpack("i", self.raw[idx+nb*size:idx+(nb+1)*size])[0])

	def __unpack_file(self):
		idx= 1024
		for (name, size) in self.fileHead:
			str= string.replace(self.raw[idx:idx+size], "\x00","")
			self.fileValue.append(str)
			idx= idx+size

	def __unpack_dataset(self):
		idx= 2048
		str= string.replace(self.raw[idx:idx+512], "\x00", "")
		if len(str):
			self.datasetValue= str
		else:	self.datasetValue= None

	def getGonio(self):
		gonio= {}
		for (name, value) in zip(self.gonioHead, self.gonioValue):
			gonio[name]= value
		return gonio

	def getDetector(self):
		det= {}
		for (name, value) in zip(self.detectorHead, self.detectorValue):
			det[name]= value
		return det

	def getFile(self):
		file= {}
		for (head, value) in zip(self.fileHead, self.fileValue):
			file[head[0]]= value
		return file

	def getDataset(self):
		return self.datasetValue


		
