import mx
from mx.DateTime import *
import Globals
import Objects
from Generics import *
import persistent
import persistent.list
import mx.DateTime
import Debug

class UniqueList(persistent.list.PersistentList):
    def appendUnique(self,data):

        try:
            for i in range(self.__len__()):
                if (self.__getitem__(i)==data):
                    raise ValueError(message='One or more of the data elements were already in the list')
                
            self.append(data)

        except ValueError, e:
            #print e
            #raise ValueError(message='One or more of the data elements were already in the list')
            pass

class UPQueue(persistent.list.PersistentList):
    """A simple unique priority queue"""
    def insertP(self,data):
        
        for i in range(self.__len__()):
            if self.__getitem__(i)>data:
                self.insert(i,data)
                return
            if self.__getitem__(i)==data:
                raise ValueError('Value already exists!')
        self.append(data)

    def index(self,data):
        for i in range(self.__len__()):
            if self.__getitem__(i)==data:
                return i
        raise ValueError('The value does not exist!')

    def getPulsesBefore(self,pulse,debug=False):

        exists = False
        pulses = UPQueue()
        
        if debug:
            print "Search Pulse:",pulse
        for i in range(self.__len__()):
            if debug:
                print self.__getitem__(i)
            if (mx.DateTime.cmp(pulse.timeStamp,self.__getitem__(i).timeStamp,Globals.AvgTimePrec)>=0):
                #print pulse.timeStamp, ">=", self.__getitem__(i).timeStamp
                #print self.__getitem__(i)
                
                pulses.insertP(self.__getitem__(i))
                    
            elif (mx.DateTime.cmp(pulse.timeStamp,self.__getitem__(i).timeStamp,Globals.AvgTimePrec)<=0):
                #print pulse.timeStamp, "<=", self.__getitem__(i).timeStamp
                exists = True

        return (pulses,exists)

class FrameList:
    def __init__(self):
        self.frames = UniqueList()

    def append(self,data):
        self.frames.appendUnique(data)
    
    #def __iter__(self):
    #    return self.frames

    def __getitem__(self,key):
        for frame in self.frames:
            try:
                if (val(frame.header)==key):
                    return frame
            except AttributeError:
                if frame.header==key:
                    return frame

        raise IndexError('Frame does not exist!',key)

class ChirpList(UniqueList):
    def indexChirp(self,length,value):
        length = int(length)
        value = int(value)

        for i in range(self.__len__()):
            
            #print len(self.__getitem__(i)),val(self.__getitem__(i))
            if ((len(self.__getitem__(i))==length)
                and
                (val(self.__getitem__(i))==value)):
                return self.__getitem__(i)            
            
        raise IndexError('Chirp does not exist!')

            
if __name__ == '__main__':
    import unittest
    class UPQueueTests(unittest.TestCase):
        def setup(self):
            rightNow = mx.DateTime.now()
            later = rightNow + mx.DateTime.DateTimeDeltaFrom(1)
            self.beforePulse = Objects.Pulse(timeStamp=rightNow)
            self.afterPulse = Objects.Pulse(timeStamp=later)

        def testInsert(self):
            self.setup()
            tqueue = UPQueue()
            tqueue.insertP(self.beforePulse)
            tqueue.insertP(self.afterPulse)
            self.failIfEqual(tqueue.pop(0),self.afterPulse)

        def testUniqueness(self):
            self.setup()
            try:
                tqueue = UPQueue()
                tqueue.insertP(self.beforePulse)
                tqueue.insertP(self.beforePulse)
                self.fail()
            except ValueError:
                pass

        def testPersistence(self):
            self.setup()
            tqueue = UPQueue()
            tqueue.insertP(self.beforePulse)
            tqueue.insertP(self.afterPulse)
            Debug.writeToFS(tqueue)
            readQueue = Debug.readFromFS()
            self.failUnlessEqual(tqueue,readQueue)

    unittest.main()
    
    
