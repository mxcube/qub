_USE_THREAD = True

##@brief disable thread in the Qub library
#
#This methode must be called before import of QubThreads
def disableThread() :
    global _USE_THREAD
    _USE_THREAD = False

def useThread() :
    return _USE_THREAD

