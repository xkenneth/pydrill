from decoder import decoder

from objects import pulse

from helper import smart_datetime as datetime
from helper import smart_timedelta as timedelta

import DataStructures

import random

class TwoOfFiveSimulator(decoder):
    def __init__(self,**kw):
        self.modulus = 0.5
        decoder.__init__(self,**kw)

    def make(self,symbols,timeStamp,modulus=0.5,ratio=2.0,debug=False):
        newSymbols = [] 

        for s in symbols: #create random symbols if their values aren't defined
            if s.value is not None:
                newSymbols.append(s)
            else:
                newSymbols.append(self.symbols[random.randint(0,99)])
                
        bars = []
        for nS in newSymbols: #accumulate all of the bars
                bars.extend(nS.bars)

        pulses = []
        #print bars
        first_found = False
        first = None

        for b in bars: #iterate through the bars, creating pulses where needed
            time = modulus
            if b.wide:
                time = modulus*2.0

            if b.peak:
                if first_found is False and first is not None:
                    first_found = True
                    first += timedelta(0,time/ratio)

                if first is None:
                    first_found = True
                    first = timedelta(0,time/ratio)

                #pdb.set_trace()
                pulses.append(pulse(timeStamp=timeStamp+timedelta(0,time/ratio)))

            if first_found is False and first is not None:
                first += timedelta(0,time)
            if first is None:
                first = timedelta(0,time)
            
                
            timeStamp += timedelta(0,time)

        for i in range(len(pulses)):
            pulses[i].timeStamp = pulses[i].timeStamp - first

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

            new_time = new_time + timedelta(0,len(real_symbols[c])*self.modulus)
            
        #for real_symbol in real_symbols:
        #    print "!!",real_symbol

        return final_symbols
    
if __name__ == '__main__':
    import unittest
    from symbol_generation import generateSymbols, generateIdentifiers

    class SimulationTests(unittest.TestCase):
        def setup(self):
            self.sim = TwoOfFiveSimulator()
            self.sim.addSymbols(symbols=generateSymbols(),identifiers=generateIdentifiers())

        def testSetup(self):
            self.setup()
        
        def testInst(self):
            t = TwoOfFiveSimulator()

            

        def test1(self):
            self.setup()
            t = [self.sim.symbols[-1],self.sim.identifiers[0],self.sim.symbols[0]]

            print t

            print self.sim.make(t,datetime.now(),debug=True)
            
        

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
    
