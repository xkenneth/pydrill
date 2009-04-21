from DataStructures import ChirpList,FrameList

from objects import chirp, frame, sub_frame

class decoder:
	"""Base decoder class - doesn't actually decode anything!"""
	def __init__(self, debug=False):
		
		self.chirps = None
		self.frames = None
		self.subframes = None
		self.symbols = None

		self.debug = debug
		if self.debug:
			print "Initializing Decoder"

	def addChirps(self,chirps=None,file=None): 
		"""Add chirps to the decoder for decoding
		Arguments:
		chirps -> An array or single chirp
		file -> An XML file containing the chirps"""
		
		self.chirps = ChirpList()   #if not create it 
			
		#if we have a file
		if (file!=None):
			chirps = self.loadChirpsFromXML(file)


		#if we don't have a file, check to see if we have chirps
		if chirps is not None:
			for c in chirps:
				self.chirps.append(c)
				
		self._maxChirp = 0
		self._maxChirpLength = 0
		for c in self.chirps:
			if sum(c.deltas) > self._maxChirp:
				self._maxChirp = sum(c.deltas[0:-1])
				self._maxChirpWithEndPulse = sum(c.deltas)
			if len(c.deltas) > self._maxChirpLength:
				self._maxChirpLength = len(c.deltas[0:-1])
				self._macChirpLengthWithEndPulse = sum(c.deltas)

	def addSymbols(self,symbols=None,identifiers=None,file=None):
		self.symbols, self.identifiers = symbols,identifiers

		if identifiers is not None:
			numPeaks = []
			for i in identifiers:
				numPeaks.append(i.numPeaks())

			self.maxIdentifierPeaks = max(numPeaks)
				
		
		
				

	def addFrames(self,frames=None,file=None):
		
		self.frames = {}
		
		if frames is not None:
			for frame in frames:
				self.frames[frame.identifier.value] = frame

		if file is not None:
			self.loadFramesFromXML(file)

	def addSubFrames(self,file):
		self.subFrames = []

		doc = Parse(file)
		elements = doc.xpath('//SubFrame')
		

		for element in elements:
			self.subFrames.append(SubFrame.SubFrame(xml=element))


if __name__ == '__main__':
    import unittest

    class DecoderTests(unittest.TestCase):
        def setup(self):
            pass

        def testInst(self):
            t = decoder()

    unittest.main()
