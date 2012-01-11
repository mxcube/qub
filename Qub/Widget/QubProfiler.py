import time

class QubProfiler:
    def __init__(self, name):
        self.name = name
        self.on = 0
        self.running = 0
           
    def start(self):
        if self.on and not self.running:
            self.running = 1
            self.interList = {}
            self.startTime = time.time()
            self.stopTime = -1
            print "-----------------------------------------------"
            print "Profiler start"
    
    def stop(self):
        if self.on and self.running:
            self.stopTime = time.time()
            t = int((self.stopTime - self.startTime) * 1000)
            print "Profiler duration : %d"%(t,)
            print "-----------------------------------------------"
            print " "
            self.running = 0
            
    def interStart(self, key, comment=""):
        if self.on and self.running:
            if key not in self.interList:
                self.interList[key] = {}
            self.interList[key]["start"] = time.time()
            self.interList[key]["comment"]  = comment
              
    def interStop(self, key):
        if self.on and self.running:
            if key in self.interList:
                tstop = time.time()
                comment = self.interList[key]["comment"]
                tstart  = self.interList[key]["start"]

                tbeg = int((tstop - self.startTime)*1000)
                t    = int((tstop - tstart)*1000)

                print "    %d : %s : %s (%d)"%(tbeg, key, comment, t)

    def setOn(self, onoff):
        self.on = onoff
    
AppProfiler = QubProfiler("Application")
AppProfiler.setOn(1)
