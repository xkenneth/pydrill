from persistent import Persistent
import persistent.list
from PyDrill import Debug
import mx.DateTime

class Chirp(Persistent):
	 """This class represents a basic chirp"""
	 #constructor
	 def __init__(self,value=None,deltas=None,xml=None,chirpLength=None,timeStamp=None,pulses=None,peaks=None,valleys=None):
		 """Takes the place of a default constructor. Arguments must either be the value of the chirp and the associated deltas, or an 4Suite XML Element"""

		 self.value = value
		 self.chirpLength = chirpLength
		 self.timeStamp = timeStamp
		 self.pulses = pulses
		 self.deltas = deltas
		 self.peaks = None
		 self.valleys = None
		 try:
			 if peaks is not None:
				 self.peaks = persistent.list.PersistentList()
				 self.peaks.extend(peaks)
		 except AttributeError:
			 pass

		 try:
			 if valleys is not None:
				 self.valleys = persistent.list.PersistentList()
				 self.valleys.extend(peaks)
		 except AttributeError:
			 pass
		 
		 if deltas is not None:
			 self.deltas = persistent.list.PersistentList()
			 self.deltas.extend(deltas) #take them if we've got them
			 
		 if pulses is not None:
			 self.pulses = persistent.list.PersistentList()
			 self.pulses.extend(pulses)
		 
		 if (xml): #else let's try xml
			 self.loadFromXML(xml)

		 self.fileKey = 'chirp'
			 
	 def __copy__(self):
		 return Chirp(value=self.value,deltas=self.deltas,chirpLength=self.chirpLength,timeStamp=self.timeStamp,pulses=self.pulses)
	 
	 def loadFromXML(self,doc):

		 value = doc.xpath('.//Value')


		 if (len(value) != 1):
			 raise ValueError('Invalid values found for a chirp!')

		 self.value = int(value.pop().firstChild.nodeValue)

		 self.deltas = persistent.list.PersistentList()
		 
		 deltas = doc.xpath('.//Delta')

		 for d in deltas:
			 self.deltas.append(float(d.firstChild.nodeValue))

	 #functions

	 def __len__(self):

		 if self.deltas:
			 return len(self.deltas)
		 
		 if self.chirpLength:
			 return self.chirpLength

		 raise ValueError('Chirp length is not defined!')

	 def __val__(self):
		 return self.value

	 #OPERATOR OVERLOADING

	 def __eq__(self, other, debug=False):
		 """This function overloads the == operator and allows comparison of chirps"""

		 if not isinstance(other,Chirp):
			 return NotImplemented
		 
		 if self.deltas != other.deltas:
			 return False

		 if (self.value!=other.value):
			 return False
			 
		 if self.chirpLength!=other.chirpLength: #check them
			 return False

		 if self.timeStamp!=other.timeStamp: #check
			 return False
			 
		 if self.pulses!=other.pulses: #check
			 return False

		 return True #if we've made it this far they're equal

	 def __ne__(self, other):
		 """This function overloads the != operator"""
		 result = self.__eq__(other)
		 if result is NotImplemented:
			 return result
		 return not result 


	 #printing
	 #called by the repr(obj) function
	 def __repr__(self):
		 t =  "Chirp"

		 if self.chirpLength!=None:
			 t += " len(cl): " + unicode(self.chirpLength)
			 t += ' '

		 if self.deltas!=None and len(self.deltas)>0:
			 t += " len(d): " + str(len(self.deltas))
			 t += ' '
		 		
		 if self.timeStamp!=None:
			 t += "time: " + str(self.timeStamp)

		 if self.value!=None:
			 t += " val: " + unicode(self.value)
			 t += ' '

		 if self.pulses != None:
			 t += " " + str(len(self.pulses)) + " Pulses Attached "

		 if self.peaks is not None:
			 t += " Peaks: "
			 for p in self.peaks: t += " " + p + " "

		 if self.valleys is not None:
			 t += " Valleys: "
			 for v in self.valleys: t += " " + v + " "

		 return t

	 #called by the str(obj) function
	 def __str__(self):
		 return self.__repr__() #simply call this methods __repr__ function which does the same thing


	 #file IO
	 def writeToXml(self,writer): #create an XML tag for this tag

		 #start writing the tags

		 writer.startElement(u'Chirp')
		 writer.simpleElement(u'Value',content=unicode(self.value))
		 
		 if self.timeStamp!=None:
			 writer.simpleElement(u'TimeStamp',content=unicode(self.timeStamp))

		 #create the delta tags
		 for i in self.deltas:
			 writer.startElement(u'Delta') #start delta tag
			 writer.text(unicode(str(i))) #delta value
			 writer.endElement(u'Delta') #end delta tag

		 #end the Chirp tag
		 writer.endElement(u'Chirp')


if __name__ == '__main__':
    import unittest

    class ChirpObjectTests(unittest.TestCase):
        def setup(self):
            self.testChirp1 = Chirp(value=4,deltas=[1,2,3,4])
            self.testChirp2 = Chirp(value=5,chirpLength=5,timeStamp=mx.DateTime.now(),pulses=[1,2,3],valleys=['w','n','w'],peaks=['w','n','w'])

	def testRepr(self):
            self.setup()
	    #print self.testChirp2

        def testCopy(self):
            self.setup()
            from copy import copy,deepcopy
            self.failUnlessEqual(self.testChirp1,copy(self.testChirp1))

        def loadXml(self):
            from Ft.Xml import Parse

            xmlFile = file('chirps.xml','r')
            doc = Parse(xmlFile)
            self.chirpTags = doc.xpath('//Chirp')


	def loadChirps(self):
            from PyDrill.Generation.TwoOfFive import Symbols
	    self.chirps = Symbols.generate()
	    
        def testEQ(self):
            self.setup()
            self.failUnlessEqual(self.testChirp1,self.testChirp1)
            self.failUnlessEqual(self.testChirp2,self.testChirp2)
            self.failIfEqual(self.testChirp1,self.testChirp2)

        def testPersistence(self):
            self.setup()
            Debug.writeToFS(self.testChirp1)
            self.failUnlessEqual(self.testChirp1,Debug.readFromFS())
	    Debug.writeToFS(self.testChirp2)
	    self.failUnlessEqual(self.testChirp2,Debug.readFromFS())
			
        def testXML(self):
            self.loadXml()
            chirps = []
            for ct in self.chirpTags:
                chirps.append(Chirp(xml=ct))

        def testXMLPersistence(self):
            self.loadXml()
            chirps = []
            for ct in self.chirpTags:
                chirps.append(Chirp(xml=ct))
            for c in chirps:
                Debug.writeToFS(c)
                self.failUnlessEqual(Debug.readFromFS(),c)

        def testEqualNone(self):
		self.failIfEqual(Chirp(chirpLength=6,value=0),None)
            
    unittest.main()
