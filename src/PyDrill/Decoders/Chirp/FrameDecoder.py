from PyDrill.Decoders import Decoder
from PyDrill.Objects import Chirp,Element,SubFrame,Frame
from PyDrill.Simulation import LinearSimulator

class FrameDecoder(Decoder.Decoder):
	def __init__(self,clear=False,**kw):

            if not clear:
                Decoder.Decoder.__init__(self,**kw)
                
            self.header = None
            self.count = 0
            self.subFramesFound = False
            self.decodedSubFrames = []
            self.checkSum = None

	def decode(self,object,debug=False):
		if isinstance(object,Chirp.Chirp): #if it's a chirp

			if len(object)==6: #if it's of length 6 #THIS NEEDS TO BE DYNAMIC
				if debug:
					print "Got the header!"
				element = Element.Element()
				element.loadFromChirp(object,identifier='Header')
				self.header = element #assign it as the header

			if self.subFramesFound:
				if (len(object)==4): #this needs to be dynamic!
					element = Element.Element()
					element.loadFromChirp(object,identifier='CheckSum')
					self.checkSum = element #assign it as the checkSum
				    
				        #once we have the checkSum, assemble the data frame
					dataFrame = Frame.Frame(header=self.header,subFrames=self.decodedSubFrames,checkSum=self.checkSum) 
					dataFrame.timeStamp = self.header.timeStamp

					for isF in range(len(self.frames[self.header.value].subFrames)):
						for ib in range(len(self.frames[self.header.value].subFrames[isF].blocks)):
							dataFrame.subFrames[isF].blocks[ib].name = self.frames[self.header.value].subFrames[isF].blocks[ib].name
							
					
					self.__init__(clear=True) #clear the decoder for the next run
					
					return dataFrame #return the dataFrame
				else:
					self.__init__(clear=True) #if the next chirp isn't a checksum sized chirp, frame is invalid!
					
				
		if ((self.header!=None) and not(self.subFramesFound)): #if the header exists

			if (isinstance(object,SubFrame.SubFrame)): #if it's a subFrame
				
				try:
					#print "!!!!",self.header
					#print "!!!!!",self.header.value
					if (object==self.frames[self.header.value].subFrames[self.count]): #if the two subFrames match
						
						object.assimilate(self.frames[self.header.value].subFrames[self.count])
						self.decodedSubFrames.append(object) #save it
						self.count +=1 #increment to the next count
					else: 
						for i in range(len(object.blocks)):
							all = True
							all = all and object.blocks[i] == self.frames[self.header.value].subFrames[self.count].blocks[i]
								
						if all:
							return
							
						self.__init__(clear=True) #clear it out! #if it's the wrong subFrame, the frame is invalid
						
				except IndexError:
					self.__init__(clear=True)

				if self.count==len(self.frames[self.header.value].subFrames): #if we've found all the subFrames

					self.subFramesFound = True #mark them as done so we can search for the checksum

	


if __name__ ==  '__main__':
    import unittest

    class FrameDecoderTests(unittest.TestCase):
        def setup(self):
            sim = LinearSimulator.LinearSimulator()
	    sim.addChirps(file='chirps.xml')
	    sim.addSubFrames(file='subframes.xml')
	    sim.addFrames(file='frames.xml')
	    self.sim = sim
	    
	    fd = FrameDecoder()
	    fd.addChirps(file='chirps.xml')
	    fd.addSubFrames(file='subframes.xml')
	    fd.addFrames(file='frames.xml')
	    self.fd = fd
        
        def testInst(self):
            t = FrameDecoder()

	def testFrames(self):
		self.setup()
		cap = Chirp.Chirp(chirpLength=6,value=0)
		for frame in self.fd.frames.frames:
            #get a new fd
			fd = FrameDecoder()
			fd.addChirps(file='chirps.xml')
			fd.addSubFrames(file='subframes.xml')
			fd.addFrames(file='frames.xml')
			
			objects = frame.sim(recursive=False)
			
			value = None
			for o in objects:
				value = fd.decode(o)
			if value!=frame:
				self.fail()

	def testFramesSequential(self):
		self.setup()
		cap = Chirp.Chirp(chirpLength=6,value=0)
		
		fd = FrameDecoder()
		fd.addChirps(file='chirps.xml')
		fd.addSubFrames(file='subframes.xml')
		fd.addFrames(file='frames.xml')        
		
		objects = []

		for frame in self.fd.frames.frames:
			objects.extend(frame.sim(recursive=False))
            
		decodedFrames = []
		for o in objects:
			value = fd.decode(o)
			if isinstance(value,Frame.Frame):
				decodedFrames.append(value)
        
		self.failUnlessEqual(decodedFrames,self.fd.frames.frames)

	def testFrameDecomposition(self):
		self.setup()


    unittest.main()
