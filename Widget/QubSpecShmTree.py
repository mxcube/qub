import numpy
import weakref
from Qub.CTools import sps
import qt
if __name__ == "__main__" :
    a = qt.QApplication([])

_TypeCode = {
    numpy.dtype('float32') : "Float",
    numpy.dtype('float64') : "Double",
    numpy.dtype('int') : "Int",
    numpy.dtype('int16') : "short",
    numpy.dtype('int32') : "Int",
    numpy.dtype('int8') : "Byte",
    numpy.dtype('uint16') : "Unsigned short",
    numpy.dtype('uint32') : "Unsigned int",
    numpy.dtype('uint8') : "Unsigned Byte",
    numpy.dtype('uint64') : "Unsigned long"}

from Qub.Data.Plug.QubPlug import QubPlug
from Qub.Data.Source.QubSpecSource import getSpecVersions,QubSpecSource2Version
from Qub.Data.Source.QubSpecVersion import QubSpecVersion2Shm

class _SpecVersionPlug(QubSpecSource2Version) :
    def __init__(self,tree) :
        QubSpecSource2Version.__init__(self,getSpecVersions(),anActiveFlag = True,timeout = 2000)
        self.__tree = tree

    def newObject(self,specSource,versions) :
        for version_name in versions:
            self.__tree.newSpecVersion(specSource,version_name)
    
    def destroy(self,specSource,versions) :
        for version_name in versions:
            self.__tree.removeSpecVersionInTree(version_name)

    
class _SpecShmPlug(QubSpecVersion2Shm) :
    def __init__(self,specVersion,tree) :
        QubSpecVersion2Shm.__init__(self,specVersion,anActiveFlag = True,timeout = 2000)
        self.__tree = tree
        
    def newObject(self,specVersion,shms) :
        for shm_name in shms :
            self.__tree.newSpecShm(specVersion,shm_name)

    def destroy(self,specVersion,shms) :
        for shm_name in shms:
            self.__tree.removeSpecShm(specVersion.name(),shm_name)


class _ShmCheckUpDate(QubPlug) :
    def __init__(self,item) :
        QubPlug.__init__(self,timeout = 5000)
        self.__item = weakref.ref(item)

    def update(self,specVersion,specShm,dataArray) :
        item = self.__item()
        if item:
            item.setText(1,'%d,%d' % dataArray.shape)
            try:
                item.setText(2,_TypeCode[dataArray.dtype])
            except KeyError:
                item.setText(2,'?')
        return not item
            
class QubSpecShmTree(qt.QListView) :
    def __init__(self,parent = None,name = "",f = 0):
        qt.QListView.__init__(self,parent,name,f)
        self.__openCbk = None
        self.addColumn('Spec')
        self.addColumn('Size')
        self.addColumn('Type')
        specSource = getSpecVersions()
        specSource.plug(_SpecVersionPlug(self))
        qt.QObject.connect(self,qt.SIGNAL('clicked(QListViewItem*)'),self.__clickedCBK)

        for specversion_name in sps.getspeclist() :
            self.newSpecVersion(specSource,specversion_name)
            specVersion = specSource.getObjects(specversion_name)
            for array_name in sps.getarraylist(specversion_name) :
                self.newSpecShm(specVersion,array_name)
                
    def newSpecVersion(self,specSource,version_name) :
        specItem = qt.QListViewItem(self)
        specItem.setText(0,version_name)
        specItem.specObject = specSource.getObjects(version_name)
        specItem.specObject.plug(_SpecShmPlug(specItem.specObject,self))
        specItem.setOpen(True)
        
    def removeSpecVersionInTree(self,version_name) :

        for item in self.__getIterator() :
            if item.text(0) == version_name:
                self.takeItem(item)
                break
    
    def newSpecShm(self,specVersion,shm_name) :
        for specVersionItem in self.__getIterator() :
            if specVersionItem.text(0) == specVersion.name() :
                shmItem = qt.QListViewItem(specVersionItem)
                shmItem.shm = specVersion.getObjects(shm_name)
                plug = _ShmCheckUpDate(shmItem)
                shmItem.shm.plug(plug)
                plug.update(specVersion,shmItem.shm,shmItem.shm.getSpecArray(True))
                shmItem.setText(0,shm_name)
                break

    def removeSpecShm(self,specVersion,shm_name) :
        aEndFlag = False
        for specVersionItem in self.__getIterator() :
            if specVersionItem.text(0) == specVersion:
                for shmItem in self.__getIterator(specVersionItem) :
                    if shmItem.text(0) == shm_name :
                        specVersionItem.takeItem(shmItem)
                        break
                aEndFlag = not specVersionItem.firstChild() # If No shm
                break
        return aEndFlag

    def setOpenShmCallback(self,cbk) :
        self.__openCbk = cbk
        
    def __getIterator(self,parentIterator = None) :
        if parentIterator is not None :
            Item = parentIterator.firstChild()
        else :
            Item = self.firstChild()
        while Item :
            NextItem = Item.nextSibling()
            yield Item
            Item = NextItem
    def __clickedCBK(self,item) :
        try:
            shmObject = item.shm
            specvesrion = shmObject.container()
            if self.__openCbk :
                self.__openCbk('%s:%s' % (specvesrion.name(),shmObject.name()))
        except AttributeError,err:
            pass
                
            
if __name__ == "__main__" :
    w = QubSpecShmTree(None)
    w.show()
    a.setMainWidget(w)
    a.exec_loop()
