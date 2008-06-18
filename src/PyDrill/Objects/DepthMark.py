from persistent import Persistent

class DepthMark(Persistent):
    def __init__(self,depth,timeStamp=None):
        self.depth = depth
        self.timeStamp = timeStamp
        self.fileKey = 'depthmark'

    def __copy__(self):
        return DepthMark(self.depth,timeStamp=self.timeStamp)

    def __eq__(self,other):
        if not isinstance(other,DepthMark): #check to make sure it's one of us
            return NotImplemented
        
        return self.depth == other.depth and self.timeStamp == other.timeStamp

    def __ne__(self,other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
        

if __name__ == "__main__":

    import unittest,mx.DateTime
    from PyDrill import Debug,Globals
    from copy import copy
    

    class DepthMarkTests(unittest.TestCase):
        def setup(self):
            self.dm1 = DepthMark(100,mx.DateTime.now())

        def testEQ(self):
            self.setup()
            self.failUnlessEqual(self.dm1,self.dm1)
            self.failIfEqual(self.dm1,10)
            

        def testCP(self):
            self.setup()
            self.failUnlessEqual(self.dm1,copy(self.dm1))

        def testPersistence(self):
            self.setup()
            Debug.writeToFS()
            if Debug.readFromFS()!=None:
                self.fail()
            
            Debug.writeToFS(self.dm1)
            self.failUnlessEqual(Debug.readFromFS(),self.dm1)
                

    unittest.main()
            

    
    
    
