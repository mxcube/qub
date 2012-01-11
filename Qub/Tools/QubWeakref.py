import weakref

class _WeakMethod :
    def __init__(self,meth) :
        self.__object = weakref.ref(meth.im_self)
        self.__meth = weakref.ref(meth.im_func)

    def callback(self,*args,**keys) :
        anObject = self.__object()
        if anObject :
            return self.__meth()(anObject,*args,**keys)

def createWeakrefMethod(meth) :
    aWeakRefMeth = _WeakMethod(meth)
    return aWeakRefMeth.callback
