from persistent import Persistent
import persistent.list
from PyDrill.Objects import Block
from PyDrill import Debug
import mx.DateTime

class SubFrame(Persistent):
	"""The class represents a sub-frame."""
	
     #CONSTRUCTOR
	def __init__(self,blocks=None,chirps=None,name=None,xml=None,timeStamp=None):
		"""blocks - a list of blocks"""
			 #switch for initialization

		self.blocks = persistent.list.PersistentList()
		if blocks!=None:
			self.blocks.extend(blocks)
		self.name = name
		self.timeStamp = timeStamp

		if (xml!=None):
			self.loadFromXML(xml)

		self.fileKey = 'subframe'

			
			
	def __copy__(self):
		from copy import copy
		newBlocks = []
		for b in self.blocks:
			newBlocks.append(copy(b))
		return SubFrame(blocks=newBlocks,name=self.name,timeStamp=self.timeStamp)

     #INITIALIZATION METHODS	
	def loadFromXML(self,doc):

		if(doc.nodeName!='SubFrame'):
			raise ValueError(('Exptected SubFrame Tag, recieved: ' + doc.nodeName))

	     #check for a name tag
		try:
			self.name = doc.xpath('./Name')[0].firstChild.nodeValue
		except:
			#print 'No Name Tag Found!'
			pass
			
		self.blocks = persistent.list.PersistentList()

		bTags = []
		bTags.extend(doc.xpath('.//Block'))
		
		for b in bTags:
			self.blocks.append(Block.Block(xml=b))
			
			
    #OPERATOR OVERLOADING

	def __len__(self):
		return len(self.blocks)
	def __eq__(self,other):
	    
	    #test the blocks first
	    #test block length
		if not isinstance(other,SubFrame):
			return False
		try:
			if (len(self.blocks)!=(len(other.blocks))):
				print "BLOCK SIZE IS NOT EQUAL!"
				return False
		except AttributeError: #if it's not a subframe class...
			return False
		
	    #if the length is equal, check the individual blocks
		for i in range(len(self.blocks)):
			if (self.blocks[i]!=other.blocks[i]):
				print "BLOCK IS NOT EQUAL!"
				return False
			
	    #if the blocks are equal, check the name
		#try:
		#	self.name
		#	other.name
		#	if (self.name!=other.name):
		#		print "NAMES ARE NOT EQUAL!"
		#		return False
		#	
		#except:
		#	pass
	    
	    #all else fails return true
		return True
    
	def __ne__(self,other):
		return not(self.__eq__(other))

	def __repr__(self):
		t = "SubFrame\n"

		try:
			t += repr(self.name)
			t += "\n"
		except AttributeError:
			pass
		
		try:
			self.timeStamp
			t += "time: "
			t += str(self.timeStamp)
			t += "\n"

		except AttributeError:
			pass

		t += "Blocks\n"

		for i in self.blocks:
			t += repr(i) + "\n"
		
		t += "End Blocks\n"

		t += "End SubFrame"
		
		return t

	def __str__(self):
		return self.__repr__()

	def sim(self):
		chirps = []
		for block in self.blocks:
			chirps.extend(block.sim())

		return chirps
	
	def decompose(self):

		#data = {}
		data = []
		for block in self.blocks:
			blockData = block.decompose()
			if blockData:
				data.append(blockData)
			
			
		for d in data:
			d.timeStamp = self.timeStamp
		return data
		
	def assimilate(self,other):
		for i in range(len(self.blocks)):
			try:
				self.blocks[i].name
			except AttributeError:
				self.blocks[i].name = other.blocks[i].name
		
		
	def writeToXml(self,writer):
		writer.startElement(u'SubFrame')
        
		try:
			writeXMLTag(writer,"Name",self.name)
		except:
			pass
		
		for i in self.blocks:
			i.writeToXml(writer)
			
		writer.endElement(u'SubFrame')



if __name__ == '__main__':
    import unittest

    class SubFrameObjectTests(unittest.TestCase):
        def setup(self):
            self.testBlock = Block.Block(chirpLengths=[5,4,4],name='Test')
            self.testSubFrame = SubFrame(blocks=[self.testBlock],name='SubFrame1',timeStamp=mx.DateTime.now())
            
        def testSetup(self):
            self.setup()
            
        def testCopy(self):
            self.setup()
            from copy import copy,deepcopy
            self.failUnlessEqual(self.testBlock,copy(self.testBlock))
            
        def loadXML(self):
            from Ft.Xml import Parse

            xmlFile = file('subframes.xml','r')
            doc = Parse(xmlFile)
            self.subFrameTags = doc.xpath('//SubFrame')

        def testLoadXML(self):
            self.loadXML()
            
        
        def testEQ(self):
            self.setup()
            self.failUnlessEqual(self.testSubFrame,self.testSubFrame)
        def testNE(self):
            self.setup()
            self.failIfEqual(self.testSubFrame,None)

        def testPersistence(self):
            self.setup()
            Debug.writeToFS(self.testSubFrame)
            self.failUnlessEqual(self.testSubFrame,Debug.readFromFS())

        def testXML(self):
            self.loadXML()
            for sf in self.subFrameTags:
                SubFrame(xml=sf)
            
        def testXMLPersistence(self):
            self.loadXML()
            for sf in self.subFrameTags:
                t = SubFrame(xml=sf)
                Debug.writeToFS(t)
                self.failUnlessEqual(Debug.readFromFS(),t)

    unittest.main()
