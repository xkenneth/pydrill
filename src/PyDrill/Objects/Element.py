from persistent import Persistent
from PyDrill import Debug
from PyDrill.Objects import Chirp

class Element(Persistent):
	#BASIC CONSTRUCTOR
	"""This class represents a particular element of a frame, such as a header,checkSum,etc"""
	def __init__(self,chirpLength=None,identifier=None,value=None,xml=None,timeStamp=None):
		"""Constructor for the class"""
		
		self.chirpLength = chirpLength
		self.identifier = identifier
		self.value = value
		self.timeStamp = timeStamp
		self.fileKey = 'element'

		#try and load from the XML tag
		if (xml!=None):
			self.loadFromXML(xml)

	def __copy__(self):
		return Element(chirpLength=self.chirpLength,identifier=self.identifier,value=self.value,timeStamp=self.timeStamp)

	def loadFromChirp(self,chirp,identifier=None):
		self.chirpLength = len(chirp)
		self.identifier = identifier
		self.value = chirp.value
		try:
			self.timeStamp = chirp.timeStamp
		except AttributeError:
			pass

	def loadFromXML(self,doc):

		if (doc.nodeName!='Element'):
			raise ValueError(('Exptected Element Tag, recieved: ' + XML.nodeName))
		
		#try and retrieve the identifier tag
		try:
			
			#print "!", doc.xpath('./Identifier')[0].firstChild.nodeValue
			self.identifier = doc.xpath('./Identifier')[0].firstChild.nodeValue

		except:

			pass #we can live without an identifier? i think

		#try and find chirp length
		try:
			self.value = int(doc.xpath('./Value')[0].firstChild.nodeValue)
		except:
			pass #we can live without a value 
		
		try:
			self.chirpLength = int(doc.xpath('./Chirp')[0].firstChild.nodeValue)
		except:
			raise ValueError('Cannot find Chirp Length tag')

	def loadFromXml(self,doc):
		self.loadFromXML(doc)

	#OPERATOR OVERLOADING
	
	def __eq__(self,other):

		#check the chirp lengths
		if not isinstance(other,Element):
			return False

		if self.timeStamp!=other.timeStamp: #check the timeStamp
			return False

		if (self.chirpLength != other.chirpLength): #check the chirpLength
			return False

		if (self.value!=other.value): #check the value
			return False

		if (self.identifier != other.identifier): #check the identifier
			return False

		#if all else fails
		return True
			
	def __ne__(self,other):
		return not(self.__eq__(other))

	def __len__(self):
		return self.chirpLength

	def __val__(self):
		return self.value

	def doesForceValue(self):
		try:
			self.value
			return True
		except:
			raise ValueError('Not Initialized')

	def __repr__(self):

		t = "Frame Element "
		if self.chirpLength!=None:
			t += "Chirp Length: " + repr(self.chirpLength)

		if self.identifier!=None:
			t += " Identifier: " + repr(self.identifier)

		if self.value!=None:
			t += " Value: " + repr(self.value)

		return t

	def __str__(self):
		return self.__repr__()

	def sim(self):
		try:
			value = self.value
		except AttributeError:
			value = None
			
		return Chirp.Chirp(value=value,chirpLength=self.chirpLength)
		
		

	def writeToXml(self,writer):

		writer.startElement(u'Element')
		
		if (self.identifier != None):
			writer.simpleElement(u"Identifier",content=unicode(self.identifier))
		if (self.chirpLength!=None):
			writer.simpleElement(u"Chirp",content=unicode(self.chirpLength))
		if self.value!=None:
			writer.simpleElement(u"Value",content=unicode(self.value))
		if self.timeStamp!=None:
			writer.simpleElement(u"TimeStamp",content=unicode(self.timeStamp))

		writer.endElement(u'Element')



if __name__ == '__main__':
    import unittest
    
    class ElementObjectTests(unittest.TestCase):
        def setup(self):
            self.testElement = Element(chirpLength=5,identifier='Test',value=5)
            
        def testEQ(self):
            self.setup()
            self.failUnlessEqual(self.testElement,self.testElement)
            
        def testNE(self):
            self.setup()
            self.failIfEqual(self.testElement,None)
		
        def testPersistence(self):
            self.setup()
            Debug.writeToFS(self.testElement)
            self.failUnlessEqual(self.testElement,Debug.readFromFS())
			
        def testCopy(self):
            self.setup()
            from copy import copy,deepcopy
            self.failUnlessEqual(self.testElement,copy(self.testElement))

    unittest.main()
