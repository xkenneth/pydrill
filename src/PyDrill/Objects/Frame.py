from persistent import Persistent
import persistent.list
from PyDrill.Objects import Element,Block,SubFrame
from PyDrill.Objects.Chirp import Chirp
from PyDrill.Objects.Block import Block
from PyDrill import Debug
import mx.DateTime

class Frame(Persistent):
    #basic initialization of the frame
    def __init__(self,header=None,subFrames=None,checkSum=None,xml=None,debug=False,timeStamp=None):
        """Basic constructor for the Frame Class"""        
	
	self.header = header
        
	self.subFrames = persistent.list.PersistentList()
        if subFrames!=None:
            self.subFrames.extend(subFrames)
	self.checkSum = checkSum
	self.timeStamp = timeStamp
	
	self.debug = debug

        self.fileKey = 'frame'



        if (xml!=None):
            #initialize off of an XML tag
            self.loadFromXML(xml)   

    #def __len__(self):
    #    pass
    
    def __copy__(self):
	    from copy import copy

	    newSubFrames = []
            if self.subFrames != None:
                for sF in self.subFrames:
		    newSubFrames.append(copy(sF))
            if newSubFrames==[]:
                newSubFrames=None

                    
            
	    return Frame(header=copy(self.header),subFrames=newSubFrames,checkSum=copy(self.checkSum),timeStamp=self.timeStamp)

    #INITIALIZATION SUB METHODS

    #IF LOADING FROM AN XML TAG
    def loadFromXML(self,doc):
        
	    if (doc.nodeName!='Frame'):
		    raise ValueError(('Expected Element Tag, recieved: ' + XML.nodeName))
                               
	    elements = doc.xpath('.//Element')
	    
	    elementObjects = []

	    for element in elements: #for all of the element tags

		    elementObjects.append(Element.Element(xml=element)) #initialize an element from the XML tag
		    
	    for object in elementObjects: 
		    if (object.identifier=='Header'): #if we find the header
			    self.header = object #if it's not our error, it doesn't exist, assign it
				    
		    if (object.identifier=='CheckSum'):
			    self.checkSum = object

            #searching for the header
            try:
                elements = doc.xpath('.//Header')
                self.header = int(elements[0].firstChild.nodeValue)
            except IndexError:
                pass #if we didn't find anything

            
            
                
	#find all of the subFrame tags
	    
	    self.subFrames = persistent.list.PersistentList()
	    
            subFrames = doc.xpath('./SubFrame')

	    for subFrame in subFrames:
		    self.subFrames.append(SubFrame.SubFrame(xml=subFrame))

            try:
                elements = doc.xpath('./Block')
                for e in elements:
                    self.subFrames.append(Block(xml=e))
            except IndexError:
                pass
	
		


    #FUNCTIONS

    def decompose(self):
	    data = []

	    finalData = []

	    dataDict = {}
            
	    for subFrame in self.subFrames:
		    newData = subFrame.decompose()
		    
		    data.extend(newData)

	    for d in data:
		    if len(d.value)==2:
			    finalData.append(d)
		    elif len(d.value)==1:
			    try:
				    dataDict[d.name].value = dataDict[d.name].value + d.value
				    dataDict[d.name].slowData = True
			    except KeyError:
				    dataDict[d.name] = d

	    for key in dataDict:
		    finalData.append(dataDict[key])

	    return finalData
			    
		    
		    
	    return data

    def sim(self,recursive=True):
	    data = [] #data to be returned

            if self.header!=None:
                try:
                    data.append(self.header.sim()) #create a chirp for the header
                except AttributeError:
                    #data.append(Chirp(value=-1))
                    data.append(Chirp(value=self.header))
                    
	    
            if self.subFrames!=None:
                for s in self.subFrames: #for all of the subFrames
		    try:
                        if recursive: #if recursive
                            data.extend(s.sim()) #return chirps for each subFrame
                        else:
                            data.append(s) #else just return the subFrame
		    except TypeError:
                        pass       

            if self.checkSum!=None:
                data.append(self.checkSum.sim()) #create a chirp for the checkSum
		
	    return data
			    
	    

    #OPERATOR OVERLOADING
    def __ne__(self,other):
	    return not(self.__eq__(other))

    def __eq__(self,other,debug=False):

            if other==None:
                return False

            if self.header is not None:
                try:
                    other.header
                except AttributeError:
                    return False
                if self.header != other.header:
                    return False

	    #first test the header
	    if (self.header!=other.header):
		    if debug:
			    print "Header does not match!"
		    return False

	    #then test the subFrames
            if self.subFrames!=None:
                if (len(self.subFrames)!=len(other.subFrames)):
		    if debug:
                        print "SubFrame length does not match"
                    return False

	    #then test the individual subFrames
            if self.subFrames!=None:
                for i in range(len(self.subFrames)):
		    if (self.subFrames[i]!=other.subFrames[i]):
                        if debug:
                            print "SubFrames do not match"
                        return False

	    #check the checkSum

	    if (self.checkSum!=other.checkSum):
		    if debug:
			    print "Checksum does not match!"
		    return False

	    #if all else fails return true
	    return True
	    

    def value(self):
	    return self.header.value

        #ACCESSORS

    def __repr__(self):
	    #if not(self.isValid()):
	    #raise Exception('Frame is not valid')
	    
	    t =  "Frame "
	    
	    if self.timeStamp!=None:
		    t += 'TimeStamp: ' + str(self.timeStamp) + ' '
		
            if self.header!=None:
                t += "Header: " + str(self.header) + " "
	    
	    t += "SubFrames: "
	    for subFrame in self.subFrames:
		    t += str(subFrame) + " "

            if self.checkSum != None:
                t += "CheckSum: "
                t += str(self.checkSum)
                t += " End Frame"

	    return t

    def __str__(self):
	    return self.__repr__()
            

    def writeToXml(self,writer):
        writer.startElement(u'Frame')
        

        try:
            self.header.writeToXml(writer)
        except AttributeError:
            #in case it's an int
            if self.header!=None:
                writer.simpleElement(u'Header',content=unicode(self.header))
        
        
        if self.subFrames!=None:
            for i in self.subFrames:
                i.writeToXml(writer)
        
        try:
            self.checkSum.writeToXml(writer)
        except AttributeError:
            pass

        writer.endElement(u'Frame')

if __name__ == '__main__':
    import unittest

    class FrameObjectTests(unittest.TestCase):
        def setup(self):
            self.testHeader = Element.Element(chirpLength=5,identifier='Header',value=5)
            self.testSubFrames = []
            self.testBlock = Block(chirpLengths=[5,4],name='Test',value='1A')
            self.testBlock2 = Block(chirpLengths=[4],name='Test2',value='5')
            self.testSubFrame = SubFrame.SubFrame(blocks=[self.testBlock,self.testBlock2],name='SubFrame1',timeStamp=mx.DateTime.now())
            self.testCheckSum = Element.Element(chirpLength=5,identifier='CheckSum',value=5)
            self.testFrame = Frame(header=self.testHeader,subFrames=[self.testSubFrame],checkSum=self.testCheckSum)
            
            import PyDrill.Generation.TwoOfFive.Frames

            self.TwoOfFiveFrames = PyDrill.Generation.TwoOfFive.Frames.generate()
            
        def testSetup(self):
            self.setup()
            
        def testEQ(self):
            self.setup()
            self.failUnlessEqual(self.testFrame,self.testFrame)
            
        def testEQNone(self):
            self.setup()
            self.failIfEqual(self.testFrame,None)
            
            for frame in self.TwoOfFiveFrames:
                self.failIfEqual(frame,None)

        def testNE(self):
            self.setup()
            self.failIfEqual(self.testFrame,self.testSubFrame)
                
        def testPersistence(self):
            self.setup()
            Debug.writeToFS(self.testFrame)
            self.failUnlessEqual(self.testFrame,Debug.readFromFS())
            
            for frame in self.TwoOfFiveFrames:
                Debug.writeToFS(frame)
                self.failUnlessEqual(frame,Debug.readFromFS())

        def testXmlPersistence(self):
            self.setup()
            Debug.writeToXml(self.testFrame)
            self.failUnlessEqual(self.testFrame,Frame(xml=(Debug.readFromXml())))
            
            for frame in self.TwoOfFiveFrames:
                Debug.writeToXml(frame)
                self.failUnlessEqual(frame,Frame(xml=Debug.readFromXml()))

        def testCopy(self):
            self.setup()
            from copy import copy,deepcopy
            self.failUnlessEqual(self.testFrame,copy(self.testFrame))

            for frame in self.TwoOfFiveFrames:
                self.failUnlessEqual(frame,copy(frame))
                
        def testDecompose(self):
            self.setup()

            self.testFrame.decompose()
            #self.testFrame2.decompose()

        def testSim(self):
            self.setup()
            
            self.testFrame.sim()
            #print self.testFrame2.sim()
            for frame in self.TwoOfFiveFrames:
                print frame.sim()
            

    unittest.main()
