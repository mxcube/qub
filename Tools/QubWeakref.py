import weakref

class _WeakMethod :
    def __init__(self,meth) :
        self.__object = weakref.ref(meth.im_self,self._dead)
        self.__meth = weakref.ref(meth.im_func)

    def _dead(self,objectRef) :
        self.__object = None

    def callback(self,*args,**keys) :
        if self.__object is not None and self.__object() is not None :
            return self.__meth()(self.__objet(),*args,**keys)

def createWeakrefMethod(meth) :
    aWeakRefMeth = _WeakMethod(meth)
    return aWeakRefMeth.callback
