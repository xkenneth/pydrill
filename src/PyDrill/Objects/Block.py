from persistent import Persistent
import persistent.list
from PyDrill import Debug
from PyDrill.Objects import Chirp,ToolData

class Block(Persistent):
	#BASIC CONSTRUCTOR
	def __init__(self,chirpLengths=None,name=None,timeStamp=None,xml=None,value=None,symbolLength=None):
		"""chirpLengths: a list of integers representing the lengths of the chirps in the frame"""
		
		self.chirpLengths = persistent.list.PersistentList()
		if chirpLengths!=None:
			self.chirpLengths.extend(chirpLengths)
		self.name = name
		self.timeStamp = timeStamp
		self.value = value
		self.symbolLength = symbolLength
		
		
		if (xml!=None):
			self.loadFromXML(xml)

		#Library Specific
		self.fileKey = 'block'

	def __len__(self):
		"""Return the length of the block in symbols"""
		return self.symbolLength

	def __copy__(self):
		return Block(chirpLengths=self.chirpLengths,name=self.name,timeStamp=self.timeStamp,symbolLength=self.symbolLength)

	def loadFromXML(self,doc):


		if (doc.nodeName!='Block'):
			raise Expeption(('Expected Block Tag, recieved: ' + doc.nodeName))
		
		try:
			nameTag = doc.xpath('./Name')
			self.name = nameTag[0].firstChild.nodeValue
		except Exception, e:
			pass
		
		
		self.chirpLengths = []
			
		try:
			chirpTags = doc.xpath('.//Chirp')
			
			for tag in chirpTags:
				self.chirpLengths.append(int(tag.firstChild.nodeValue))

		except Exception:
			raise ValueError('Unable to find chirps for block!')
	
		try:
			symbolLengthTag = doc.xpath('.//SymbolLength')[0]
			
			self.symbolLength = int(symbolLengthTag.firstChild.nodeValue)

		except IndexError:
			pass
			
		

	


	 #OPERATOR OVERLOADERS
	def __eq__(self,other):
		
		 #check if the chirp lengths are equal
		if not isinstance(other,Block):
			return False

		if self.chirpLengths != other.chirpLengths:
			return False

		return True
		
	def __ne__(self,other):
		return not(self.__eq__(other))
	
	def decompose(self):
		if self.name != None:
			slowData=False
			return ToolData.ToolData(self.name,self.value,self.timeStamp,slowData)

	def __repr__(self):
		t = "Block "
		
		if self.timeStamp!=None:
			t += "time: "
			t += str(self.timeStamp)
			t += " "

		if self.name!=None:
			t += "Name: " + self.name + " "
		else:
			t += " Ignorable Block "
		
		
		
		if self.value!=None:
			t += "Value: " + str(self.value) + " "
			
		if self.chirpLengths is not None and self.chirpLengths != persistent.list.PersistentList():
			t += " Chirp Lengths " 
			for i in self.chirpLengths:
				t += " " + repr(i) + " "

		if self.symbolLength!=None:
			t += "Symbol Length: " + str(self.symbolLength) + " "
		
		t += " End Block"
		
		return t

	def __str__(self):
		return self.__repr__()

	def sim(self):
		chirps = []
		for i in self.chirpLengths:
			chirps.append(Chirp.Chirp(chirpLength=i))

		if self.symbolLength is not None:
			for s in range(self.symbolLength):
				chirps.append(Chirp.Chirp())

		return chirps
	
	def writeToXml(self,writer):
		writer.startElement(u'Block')
		
		if self.name!=None:
			writer.simpleElement(u"Name",content=unicode(self.name))

		for i in self.chirpLengths:
			writer.simpleElement(u"Chirp",content=unicode(i))

		if self.symbolLength!=None:
			writer.simpleElement(u'SymbolLength',content=unicode(self.symbolLength))
			
		writer.endElement(u'Block')


if __name__ == '__main__':
    import unittest

    class BlockObjectTests(unittest.TestCase):
        def setup(self):
            self.testBlock = Block(chirpLengths=[5,4,4],name='Test',symbolLength=7)
            
        def testCopy(self):
            self.setup()
            from copy import copy,deepcopy
            self.failUnlessEqual(self.testBlock,copy(self.testBlock))
            
        def testEQ(self):
            self.setup()
            self.failUnlessEqual(self.testBlock,self.testBlock)

        def testEQNone(self):
            self.setup()
            self.failIfEqual(self.testBlock,None)
            
        def testPersistence(self):
            self.setup()
            Debug.writeToFS(self.testBlock)
            self.failUnlessEqual(self.testBlock,Debug.readFromFS())

	def testXmlPersistence(self):
		from Ft.Xml import MarkupWriter,Parse
		self.setup()
		testFile = file('/tmp/testBlock.xml','w')
		writer = MarkupWriter(testFile)
		writer.startDocument()
		writer.startElement(u'Test')
		
		self.testBlock.writeToXml(writer)
		
		writer.endElement(u'Test')
		writer.endDocument()
		
		testFile.close()

		testFile = file('/tmp/testBlock.xml','r')
		
		doc = Parse(testFile)
		
		readBlock = Block(xml=doc.xpath('.//Block')[0])

		self.failUnlessEqual(readBlock,self.testBlock)

	def testSim(self):
		selfsetup()
		
		
		
		

    unittest.main()

