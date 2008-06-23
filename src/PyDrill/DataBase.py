from PyDrill.Objects.Pulse import Pulse
import ZODB.config
from copy import copy
import ZEO
import pdb

class Layer:
    def __init__(self,host='localhost',port='8050',configFile=None,file=None):
        """A layer for trafficing Teledrill data types in and out of a ZODB through a ZEO client.
        host - the hostname
        port - the port
        """
        from ZEO import ClientStorage
        from ZODB import DB,FileStorage
        import ZODB

        #error checking
        self.host, self.port, self.configFile = host, port, configFile
        self.addr = self.host,self.port
        self.lf = '/tmp/mwdlf'
                
        #create the storage
        if file is None:
            if self.configFile is not None:
                self.storage = None
                self.db = ZODB.config.databaseFromURL(self.configFile)
            else:
                self.storage = ClientStorage.ClientStorage(self.addr,wait=False) #try to connect, don't wait
                self.db = DB(self.storage)
        else:
            self.storage = FileStorage.FileStorage(file)
            self.db = DB(self.storage)
        
        self.conn = self.db.open()
        self.root = self.conn.root()

    def sync(func):
        def inner_func(*args,**kwargs):
            my_self = args[0]
            ret = func(*args,**kwargs)
            my_self.conn.sync()
            return ret
        return inner_func
          

    def disconnect(self):
        """Disconnect from the connection, only call this on a program close."""
        self.conn.close()
        self.db.close()
        if self.storage is not None:
            self.storage.close()

        self.disconnected = False
        
    def cleanSystem(self):
        """Wipe out any data in the DataBase"""
        #get the transaction module
        import transaction
        #and our BTrees and PL
        data = [] #for saving the data
        for key in self.root.keys(): #for all of the keys
            data.append(self.root.pop(key)) #pop the data
        
        #make the changes permanent
        transaction.commit()

        #self.disconnect()
        #return the data
        return data
        
    @sync
    def newData(self,data,overWrite=False):
        """Insert new data into the database.
        Data must have an attribute called 'fileKey' which is a string
        The fileKey decides which bucket the data will be placed into"""

        import string

        data = copy(data)

        
        try: #checking to see if it's iterable
            for d in data:
                pass
        except TypeError: #if not make it so
            data = [data]

        #DATA VALIDATION

        #for all of the data
        err = AttributeError('All Data inserted into the database must have a fileKey!',data)
        for d in data: 
            try:
                if d.fileKey is None:
                    raise err
                
            except AttributeError, e:
                raise err
                
        err = ValueError('All Data inserted into the database must have a timeStamp!',data) #define our error

        try: #validating the data
            for d in data:
                if d.timeStamp == None: #if the timeStamp is none
                    raise err
        except AttributeError: #or the object has no such attribute
            raise err

        for d in range(len(data)):
            data[d].fileKey = string.lower(data[d].fileKey)

        #start the transaction
        import transaction 
        
        #for all of our data
        for d in data:
            
            #test to see if we already have a "bucket" for that
            try: 
                self.root[d.fileKey]
            except KeyError:
                #if we don't have a bucket, create one
                from BTrees import OOBTree
                self.root[d.fileKey] = OOBTree.OOBTree()
                
                
            #see if the data already exists in that bucket
            if self.root[d.fileKey].has_key(d.timeStamp) and not overWrite: #if we're not overwriting
                raise ValueError('Data already exists!',d) #raise an error
            
            
            self.root[d.fileKey].insert(d.timeStamp,d) #else write it
            

        transaction.commit() #commit the trans

    @sync
    def slice(self,key,begin=None,end=None,last=None,first=None,debug=False):
        """Return a section or all of the data for a particular "bin" in the database."""
        #self.conn.sync()
        from copy import copy
        #checks
        if last is not None:
            last = int(last)

        
        allKeys = []
        if begin is not None and end is None:
            allKeys = self.root[key].keys(min=begin)
        elif end is not None and begin is None:
            allKeys = self.root[key].keys(max=end)
        elif begin is not None and end is not None:
            allKeys = self.root[key].keys(min=begin,max=end)
        else:
            allKeys = self.root[key].keys()
                
        finalKeys = []
        
        if first:
            l = len(allKeys)
            if l < first:
                first = l
            
            for i in range(first):
                finalKeys.append(allKeys[i])

        if last:
            s = len(allKeys) - last
            
            if s<0: s=0
            
            for k in allKeys[s:]:
                finalKeys.append(k)

        #if nothing else:
        if len(finalKeys) == 0: 
            finalKeys = allKeys
        
        data = []
        for k in finalKeys:
            data.append(copy(self.root[key][k]))

        return data
            
            
if __name__ == '__main__': #if we're in the main
    import unittest
    
    # #testing for connection to the test database
#     import ZEO
#     from ZEO import ClientStorage
#     from ZODB import DB
#     host = 'localhost'
#     port = 8059
#     addr = host,port
#     storage = ClientStorage.ClientStorage(addr,wait=False)
#     try:
#         db = DB(storage)
#     except ZEO.Exceptions.ClientDisconnected:
#         print "Cannot connect to the test Zeo Server, please make sure that it is running, and retry!"
#         raise SystemExit()

    #defining the test-cases
    class LayerTests(unittest.TestCase):
        def setUp(self):

            try: 
                self.testLayer
            except AttributeError:
                
                #testLayer = Layer(host,port)
                testLayer = Layer(file='./test.fs')
                testLayer.cleanSystem()
                
                self.testLayer = testLayer
                
                #create some test pulses
                import mx.DateTime

                self.pulses = [] #a list of pulses

                t = mx.DateTime.now()
            
                for i in range(30):
                    self.pulses.append(Pulse(timeStamp=t+mx.DateTime.DateTimeDeltaFrom(i)))
            
                #insert the data into the database
                self.testLayer.newData(self.pulses)
        def tearDown(self):
            self.testLayer.disconnect()

        def testSetup(self):
            pass

        #def testDisconnect(self):
        #    self.setup()
        #    self.testLayer.disconnect()

        #def testCreateAndVerify(self):
        #    """Doc"""
        #    self.testLayer.createDBSystem()
        #    self.testLayer.verifyIntegrity()

        def testInsertPulses(self):

            bools = [] #keep a list of bools

            for key in self.testLayer.root['pulse'].keys(): #get all the present keys
                exists = False 
                for p in self.pulses: #for each pulse
                    exists = p.timeStamp == key or exists #make sure we have a pulse with a timeStamp that matches the key
                bools.append(exists) #append it to the list
                
            #make sure all the bools are true

            final = True
            
            for b in bools:
                final = final and b

            self.failUnless(final)

        def testSliceAllPulses(self):

            #test the entire slice

            newPulses = self.testLayer.slice('pulse') #should return all the pulses we put in

            bools = [] #keep a list of bools
            for np in newPulses:
                exists = False
                for p in self.pulses:
                    exists = p == np or exists
                bools.append(exists)


            final = True
            
            for b in bools:
                final = final and b

            self.failUnless(final)

#             #test the minimum slice
#             import math
#             index = int(math.floor(len(self.pulses)/2))
            
#             newPulses = self.testLayer.slice('pulse',begin=self.pulses[index].timeStamp)

#             self.failUnlessEqual(newPulses[0],self.pulses[index])
#             self.failIf(newPulses[-1]<self.pulses[index])

#             #test the maximum slice
#             index = int(math.floor(len(self.pulses)/2))
            
#             newPulses = self.testLayer.slice('pulse',end=self.pulses[index].timeStamp)

#             self.failUnlessEqual(newPulses[-1],self.pulses[index])
#             self.failIf(newPulses[0]>self.pulses[index])

        def testSliceBeginEndPulses(self):
            """Tests slicing a range specified by begin and end."""
             #test the range slice
            newPulses = self.testLayer.slice('pulse',end=self.pulses[-1].timeStamp,begin=self.pulses[0].timeStamp)
            
            self.failUnlessEqual(self.pulses[0],newPulses[0])
            self.failUnlessEqual(self.pulses[-1],newPulses[-1])

    unittest.main()
 
