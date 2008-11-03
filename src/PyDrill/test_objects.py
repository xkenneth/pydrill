#Stuff!

if __name__ == '__main__':
    import unittest

    from helper import smart_datetime as datetime
    from helper import smart_timedelta as timedelta

    from symbol_generation import generateSymbols, generateIdentifiers
    from frame_generation import generate
    
    from objects import pulse, symbol, bar, element, frame, block, sub_frame, chirp

    class SymbolObjectTests(unittest.TestCase):
        def setUp(self):

            t = datetime.now()
            ts = []
            for i in range(3):
                ts.append(t+timedelta(0,i))

            self.testSymbol1 = symbol(value=4,bars=[bar(False),bar(True),bar(False),bar(True,wide=True),bar(False),bar(True),bar(False),bar(False)],pulses=ts)
            self.symbols = generateSymbols()

        def testCopy(self):
            pass
            #self.failUnlessEqual(self.testSymbol1,copy(self.testSymbol1))

        def testFirstPossiblePeakAfter(self):
            self.testSymbol1.firstPossiblePeakAfter(debug=False)

	def testCalcDeltas(self):
            self.testSymbol1.calcDeltas()
                
        def testLen(self):
            for symbol in self.symbols:
                self.failUnlessEqual(len(symbol),14.0)

    class pulseObjectTests(unittest.TestCase):
        def setup(self):
		rightNow = datetime.now()
                later = rightNow + timedelta(0,1)
		self.beforePulse = pulse(timeStamp=rightNow)
		self.afterPulse = pulse(timeStamp=later)
		self.testPulse = pulse(timeStamp=rightNow,amplitude=100,d2x=50)

    class BarTests(unittest.TestCase):
        def setUp(self):
            self.testBar1 = bar(True,wide=True,timeStamp=datetime.now())

        def testCP(self):
            pass
            #self.failUnlessEqual(self.testBar1,copy(self.testBar1))

    class SubFrameObjectTests(unittest.TestCase):
        def setup(self):
            self.testBlock = block(chirpLengths=[5,4,4],name='Test')
            self.testSubFrame = sub_frame(blocks=[self.testBlock],name='SubFrame1',timeStamp=datetime.now())
            
        def testCopy(self):
            pass

    class FrameObjectTests(unittest.TestCase):
        def setup(self):
            self.testHeader = element(chirpLength=5,identifier='Header',value=5)
            self.testSubFrames = []
            self.testBlock = block(chirpLengths=[5,4],name='Test',value='1A')
            self.testBlock2 = block(chirpLengths=[4],name='Test2',value='5')
            self.testSubFrame = sub_frame(blocks=[self.testBlock,self.testBlock2],name='SubFrame1',timeStamp=datetime.now())
            self.testCheckSum = element(chirpLength=5,identifier='CheckSum',value=5)
            self.testFrame = frame(header=self.testHeader,subFrames=[self.testSubFrame],checkSum=self.testCheckSum)
            
            import frame_generation

            self.TwoOfFiveFrames = frame_generation.generate()
            
        def testSetup(self):
            self.setup()
            

        def testCopy(self):
            pass
                
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
            
    class ChirpObjectTests(unittest.TestCase):
        def setup(self):
            self.testChirp1 = chirp(value=4,deltas=[1,2,3,4])
            self.testChirp2 = chirp(value=5,chirpLength=5,timeStamp=datetime.now(),pulses=[1,2,3],valleys=['w','n','w'],peaks=['w','n','w'])

	def testRepr(self):
            self.setup()
	    self.testChirp2.__repr__()

    class ElementObjectTests(unittest.TestCase):
        def setup(self):
            self.testElement = Element(chirpLength=5,identifier='Test',value=5)

    class BlockObjectTests(unittest.TestCase):
        def setup(self):
            self.testBlock = Block(chirpLengths=[5,4,4],name='Test',symbolLength=7)
            
	def testSim(self):
            pass

    class SymbolFrameTestCases(unittest.TestCase):
        def setUp(self):
            self.symbols = generateSymbols()
            self.identifiers = generateIdentifiers()
            self.frames = generate()
            
        def tearDown(self):
            pass
        
        def testLen(self):
            for frame in self.frames:
                len(frame)
            #self.failIfEqual(None

    class ToolDataObjectTests(unittest.TestCase):
        def setup(self):
            self.testTD = ToolData('Test',5,datetime.now(),False)
        
            
    unittest.main()
