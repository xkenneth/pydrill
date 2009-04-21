from PyDrill.Decoders import Decoder
from PyDrill.Simulation import LinearSimulator
from PyDrill.Objects import Chirp
from copy import deepcopy
class SubFrameDecoder(Decoder.Decoder):
	def __init__(self,**kw):
		
		self.newChirps = []
		Decoder.Decoder.__init__(self,**kw)

	def decode(self,chirps,debug=False):
		
		decodedSubFrame = None
		
		try:
			for c in chirps:
				if len(c)!=6:
					self.newChirps.append(c)
		except TypeError:
			if len(chirps)!=6:
				self.newChirps.append(chirps)

		newChirpLengths = []
		for c in self.newChirps:
			newChirpLengths.append(len(c))

		maxLength = 0
		for sf in self.subFrames:
			subFrameChirpLengths = []
			for block in sf.blocks:
				subFrameChirpLengths.extend(block.chirpLengths)
				
			if len(subFrameChirpLengths)>maxLength:
				maxLength = len(subFrameChirpLengths)

			if newChirpLengths==subFrameChirpLengths:
				decodedSubFrame = deepcopy(sf)
				count = 0
				for block in range(len(decodedSubFrame.blocks)):
					data = ''
					for i in range(len(decodedSubFrame.blocks[block].chirpLengths)):
						#myHex = "%X" % int(chirps[i].value)
						data += "%X" % int(self.newChirps[count].value)
						count += 1
					decodedSubFrame.blocks[block].value = data

				decodedSubFrame.timeStamp = self.newChirps[0].timeStamp
												
		if decodedSubFrame is not None:
			if len(decodedSubFrame)==maxLength:
				self.newChirps = []
				

		return decodedSubFrame
				
				
if __name__ ==  '__main__':
    import unittest

    class SubFrameDecoderTests(unittest.TestCase):
	    def setup(self):
		    """This function sets up common variables for the following tests"""
		    sim = LinearSimulator.LinearSimulator()   #get a simulator instance and populate it
		    sim.addChirps(file='chirps.xml')
		    sim.addFrames(file='frames.xml')
		    sim.addSubFrames(file='subframes.xml')
		    self.sim = sim

		    sfd = SubFrameDecoder()
		    sfd.addChirps(file='chirps.xml')
		    sfd.addSubFrames(file='subframes.xml')
		    sfd.addFrames(file='frames.xml')
		    self.sfd = sfd
        
	    def testSetup(self):
		    self.setup()

	    def testInst(self):
		    t = SubFrameDecoder()

	    def testSubFrames(self):
		    self.setup()

		    for sf in self.sfd.subFrames:
			    chirps = self.sim.makec(sf.sim())
			    chirps.append(self.sim.makec([Chirp.Chirp(value=0,chirpLength=6)])[0])
			    newSF = None
			    for c in chirps:
				    data = self.sfd.decode(c)
				    if data:
					    newSF = data
					    print newSF
					    
					    
			    #self.failUnlessEqual(val,sf)

    unittest.main()
