from persistent import Persistent
from PyDrill.Objects.PyDrillObject import PyDrillObject
class Bar(Persistent,PyDrillObject):
    def __init__(self,peak,wide=False,timeStamp=None):
        self.peak,self.wide,self.timeStamp = peak,wide,timeStamp
        
        #Library Specific
        self.fileKey = 'bar'
        
    #def readFromXml(self,doc):
    #    value = doc.xpath('./Peak')
    #    self.value = 
        
    def writeToXml(self,writer):
        writer.startElement(u'Bar')
        writer.simpleElement(u'Peak',content=unicode(self.peak))
        if self.timeStamp is not None:
            writer.simpleElement(u'TimeStamp',content=unicode(self.timeStamp))
        if self.wide is not None:
            writer.simpleElement(u'Wide',content=unicode(self.wide))
        writer.endElement(u'Bar')

    def __eq__(self,other):
        if not isinstance(other,Bar):
            return NotImplemented

        return self.peak == other.peak and self.wide == other.wide

    def __repr__(self):
        t = ''
        if self.wide:
            t += 'Wide '
        else:
            t += 'Narrow '

        if self.peak:
            t += 'Peak'
        else:
            t += 'Space'
            
        return t



    def __copy__(self):
        return Bar(self.peak,wide=self.wide)


if __name__ == "__main__":

    import unittest,mx.DateTime
    from PyDrill import Debug,Globals
    from copy import copy
    

    class BarTests(unittest.TestCase):
        def setUp(self):
            self.testBar1 = Bar(True,wide=True,timeStamp=mx.DateTime.now())

        def testEQ(self):
            self.failUnlessEqual(self.testBar1,self.testBar1)
            self.failIfEqual(self.testBar1,10)
            self.failIfEqual(self.testBar1,None)
            

        def testCP(self):
            self.failUnlessEqual(self.testBar1,copy(self.testBar1))

        def testPersistence(self):
            Debug.writeToFS()
            if Debug.readFromFS()!=None:
                self.fail()
            
            Debug.writeToFS(self.testBar1)
            self.failUnlessEqual(Debug.readFromFS(),self.testBar1)
            
        def testXml(self):
            Debug.writeToXml(self.testBar1)
            

    unittest.main()

    
    
