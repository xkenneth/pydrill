from PyDrill.Decoders import Decoder
from PyDrill.Objects.Pulse import Pulse
from PyDrill import DataStructures
import mx.DateTime
import random
from copy import deepcopy,copy

import mx

class TwoOfFiveSimulator(Decoder.Decoder):
    def __init__(self,**kw):
        self.modulus = 0.5
        Decoder.Decoder.__init__(self,**kw)

    def make(self,symbols,timeStamp,modulus=0.5,ratio=2.0,debug=False):
        newSymbols = [] 

        for s in symbols: #create random symbols if their values aren't defined
            if s.value is not None:
                newSymbols.append(s)
            else:
                newSymbols.append(self.symbols[math.randint(0,99)])
                
        bars = []
        for nS in newSymbols: #accumulate all of the bars
                bars.extend(nS.bars)

        pulses = []
        #print bars
        for b in bars: #iterate through the bars, creating pulses where needed
            time = modulus
            if b.wide:
                time = modulus*2.0

            if b.peak:
                pulses.append(Pulse(timeStamp=timeStamp+mx.DateTime.DateTimeDeltaFrom(time/ratio)))
            
            timeStamp += mx.DateTime.DateTimeDeltaFrom(time)

        return pulses,timeStamp
                
                
        

    def makec(self,symbols,time):

        real_symbols = []

        #for every symbol
        for symbol in symbols:
            if symbol.value!=None:
                value = symbol.value
            else:
                value = random.randint(0,99) #if not, create a random one
                
            for realSymbol in self.symbols: #find the corresponding real symbol
                appended = False
                if (value==realSymbol.value): #and the val match
                    real_symbols.append(realSymbol) #keep the real symbol
                    appended = True
                    break #quit when you're done
                
            if not appended:
                for identifier in self.identifiers: #find the corresponding real symbol
                    appended = False
                    if (value==identifier.value): #and the val match
                        real_symbols.append(identifier) #keep the real symbol
                        appended = True
                        break #quit when you're done
                    
            

            if not appended:
                raise ValueError('Could not find a defined symbol with value,',value)
            
                

        #now let's take care of the timeStamps
        final_symbols = []
        new_time = time
        for c in range(len(real_symbols)):
            new_time
            new_symbol = copy(real_symbols[c])
            new_symbol.timeStamp = copy(new_time)
                              
            final_symbols.append(new_symbol)

            new_time = new_time + mx.DateTime.DateTimeDeltaFrom(len(real_symbols[c])*self.modulus)
            
        #for real_symbol in real_symbols:
        #    print "!!",real_symbol

        return final_symbols
    
if __name__ == '__main__':
    import unittest
    from PyDrill.Generation.TwoOfFive import Symbols
    import mx.DateTime

    class SimulationTests(unittest.TestCase):
        def setup(self):
            self.sim = TwoOfFiveSimulator()
            self.sim.addSymbols(symbols=Symbols.generateSymbols(),identifiers=Symbols.generateIdentifiers())

        def testSetup(self):
            self.setup()
        
        def testInst(self):
            t = TwoOfFiveSimulator()

            

        def test1(self):
            self.setup()
            t = [self.sim.symbols[-1],self.sim.identifiers[0],self.sim.symbols[0]]

            print t

            print self.sim.make(t,mx.DateTime.now(),debug=True)
            
        

#        def testMakeChirp(self):
#             self.setup()
#             allChirps = Symbols.generate()
#             t = mx.DateTime.now()
#             print " "
#             print "Start Time:",t
#             data = self.sim.makec(allChirps[0:min(10,len(allChirps))],t)
#             for d in data:
#                 print d

        

    unittest.main()
    
