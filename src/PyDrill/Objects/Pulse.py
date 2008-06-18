from persistent import Persistent
import mx.DateTime
from PyDrill.Objects.PyDrillObject import PyDrillObject
from PyDrill import Debug,Globals

class Pulse(Persistent,PyDrillObject):
	"""A Pulse Object"""

	def __init__(self,timeStamp=None,amplitude=None,d2x=None,xml=None,debug=False):
		
		self.timeStamp = timeStamp
		self.amplitude = amplitude
		self.d2x = d2x
		self.debug = debug
		
		#if unpickling from xml
		if (xml!=None):
			self.__loadFromXml__(xml)
			
		self.fileKey = 'pulse'
			

		
	def __copy__(self):
		return Pulse(timeStamp=self.timeStamp,amplitude=self.amplitude,d2x=self.d2x)
	
	#OPERATOR OVERLOADING

	def __eq__(self,other):

		if not isinstance(other,Pulse):
			return NotImplemented
		
		if other is None:
			return False

		if not isinstance(other,Pulse): #if it's a pulse
			return False
		
		if((mx.DateTime.cmp(self.timeStamp,other.timeStamp,Globals.AvgTimePrec)!=0)): #check the tS
			return False
		
		if(self.amplitude!=other.amplitude): #check the amp
			return False
		
		if(self.d2x!=other.d2x): #check the d2x
			return False
		#if all else fails
		return True

	def xmlPickle(self):
		root = objectify.Element(str(self.__class__.__name__))
		root.timeStamp = self.timeStamp
		root.amplitude = self.amplitude
		root.d2x = self.d2x

		return root

	def xmlPickleStr(self):
		return etree.tostring(self.xmlPickle())
		
	def xmlUnpickle(self,xml):
		if isinstance(xml,str):
			self.xmlUnpickle(objectify.fromstring(xml))
		if isinstance(xml,etree._Element) or isinstance(xml,objectify.ObjectifiedElement):
			self.timeStamp = mx.DateTime.DateTimeFrom(xml.timeStamp.text)
			self.amplitude = float(xml.amplitude.text)
			self.d2x = float(xml.d2x.text)
			
	def __loadFromXml__(self,doc):
		"""For loading Pulse Objects in the form:
		<Pulse>
		    <TimeStamp>XXXXXXXX</TimeStamp>
		    <Amplitude>XXXXX.XXX</TimeStamp>
		    <d2x>XXXX</d2x>
		</Pulse>
		"""
		try:
			self.timeStamp = mx.DateTime.DateTimeFrom(str(doc.xpath('./TimeStamp')[0].firstChild.nodeValue))
		except IndexError:
			pass

		try:
			self.amplitude = float(doc.xpath('./Amplitude')[0].firstChild.nodeValue)
		except IndexError:
			pass
		
		try:
			self.d2x = float(doc.xpath('./d2x')[0].firstChild.nodeValue)
		except IndexError:
			pass

		

	def __repr__(self):
		t = "Pulse "

		if self.timeStamp is not None:
			t += " TimeStamp " + str(self.timeStamp) + " "
			
		if self.amplitude!=None:
			t += " Amp: " + str(self.amplitude) + " "
		
		if self.d2x!=None:
			t += " D2X: " + str(self.d2x) + " "

		t += " End Pulse"

		return t

	def __str__(self):
		return self.__repr__()

	def writeToXml(self,writer):
		writer.startElement(u'Pulse')
		if self.timeStamp!=None:
			writer.simpleElement(u"TimeStamp",content=unicode(self.timeStamp))
		if self.amplitude!=None:
			writer.simpleElement(u"Amplitude",content=unicode(self.amplitude))
		if self.d2x!=None:
			writer.simpleElement(u"d2x",content=unicode(self.d2x))
		writer.endElement(u'Pulse')

	def __xml__(self,writer):
		self.writeToXml(writer)


if __name__ == '__main__':
    import unittest
    
    class PulseObjectTests(unittest.TestCase):
        def setup(self):
		rightNow = mx.DateTime.now()
		later = rightNow + mx.DateTime.DateTimeDeltaFrom(1)
		self.beforePulse = Pulse(timeStamp=rightNow)
		self.afterPulse = Pulse(timeStamp=later)
		self.testPulse = Pulse(timeStamp=rightNow,amplitude=100,d2x=50)
        def testEquals(self):
		self.setup()
		self.failUnlessEqual(self.beforePulse,self.beforePulse)
        def testEqualNone(self):
		self.setup()
		self.failIfEqual(self.beforePulse,None)
        def testNotEqual(self):
		self.setup()
		self.failIfEqual(self.beforePulse,self.afterPulse)
        def testGreaterThan(self):
		self.setup()
		if self.beforePulse>self.afterPulse:
			self.fail()
        def testLessThan(self):
		self.setup()
		if self.afterPulse<self.beforePulse:
			self.fail()
        def testGE(self):
		self.setup()
		if not(self.beforePulse>=self.beforePulse):
			self.fail()
		if not(self.afterPulse>=self.beforePulse):
			self.fail()
	def testLE(self):
		self.setup()
		if not(self.beforePulse<=self.beforePulse):
			self.fail()
		if not(self.beforePulse<=self.afterPulse):
			self.fail()
            
        def testPersistence(self):
		self.setup()
		Debug.writeToFS(self.beforePulse)
		t = Debug.readFromFS()
		self.failUnlessEqual(self.beforePulse,t)

	def testXml(self):
		from Ft.Xml import MarkupWriter,Parse
		self.setup()
		
		t = file('/tmp/testPulse','w') #open a tmp file
		writer = MarkupWriter(t) #start the writer
		writer.startDocument() #start the doc
		writer.startElement(u'Pulses') #start the root element
		
		self.testPulse.writeToXml(writer) #write the pulse

		writer.endElement(u'Pulses') #end the root element
		writer.endDocument() #end the doc

		t.close() #close the file

		t = file('/tmp/testPulse','r') #open it back up
		
		doc = Parse(t) #parse the XML
		
		tag = doc.xpath('//Pulse')[0] #find the pulse tag
		
		p = Pulse(xml=tag) #create the Pulse from the XML

		self.failUnlessEqual(p,self.testPulse) #fail unless they're equal
		
		
		
		
		
		
	
    unittest.main()

