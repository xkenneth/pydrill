from persistent import Persistent
import mx.DateTime
from PyDrill import Debug,Globals

class ToolData(Persistent):
	def __init__(self,name,value=None,timeStamp=None,slowData=None):
		self.name = name
		self.fileKey = name
		self.value = value
		self.timeStamp = timeStamp
		self.slowData = slowData

		
	def __copy__(self):
		return ToolData(self.name,value=self.value,timeStamp=self.timeStamp,slowData=self.slowData)

	def __ne__(self,other):
		return not(self.__eq__(other))

	def __eq__(self,other):
		if not(isinstance(other,ToolData)):
			return False
                
                if self.name != other.name:
                    return False

                if self.value != other.value:
                    return False

                if self.timeStamp != other.timeStamp:
                    return False
                
                if self.slowData != other.slowData:
                    return False

                return True

	def __repr__(self):
		t = "ToolData: "
		try:
			t+= "N: " + str(self.name) + " "
		except AttributeError:
			pass
	
		try: 
			t+= "V: " + str(self.value) + " "
		except AttributeError:
			pass

		try: 
			t+= "T: " + str(self.timeStamp) + " "
		except AttributeError:
			pass

		try:
			t+= "SD: " + str(self.slowData) + " "
		except AttributeError:
			pass

		t +=  "End TD"
		
		return t
		
	def __str__(self):
		return self.__repr__()

	def writeToXml(self,writer):
		writer.startElement(u'ToolData')
		writer.simpleElement(u"Name",content=unicode(self.name))
		writer.simpleElement(u"Value",content=unicode(self.value))
		wtiter.simpleElement(u"TimeStamp",content=unicode(self.timeStamp))
		writer.endElement(u'ToolData')

if __name__ == '__main__':
    import unittest
    class ToolDataObjectTests(unittest.TestCase):
        def setup(self):
            self.testTD = ToolData('Test',5,mx.DateTime.now(),False)
        def testEqual(self):
            td = ToolData('Test',5,mx.DateTime.now(),False)
            self.failUnlessEqual(td,td)
        def testEqualNone(self):
            td = ToolData('Test',5,mx.DateTime.now(),False)
            self.failIfEqual(td,None)
        def testPersistence(self):
            Debug.writeToFS()
            if Debug.readFromFS()!=None:
                self.fail()
            td = ToolData('Test',5,mx.DateTime.now(),False)
            Debug.writeToFS(td)
            self.failUnlessEqual(Debug.readFromFS(),td)

        def testCopy(self):
            self.setup()
            from copy import copy,deepcopy
            self.failUnlessEqual(self.testTD,copy(self.testTD))

    unittest.main()
