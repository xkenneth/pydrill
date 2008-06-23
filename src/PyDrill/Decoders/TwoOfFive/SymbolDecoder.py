import sys
import math
import pdb
from PyDrill.Decoders import Decoder
#from PyDrill.Simulation import LinearSimulator
from PyDrill.Simulation import TwoOfFiveSimulator
from PyDrill.Objects.Pulse import Pulse
from PyDrill.Objects.Bar import Bar
from copy import deepcopy,copy
from Ft.Xml import Parse
import mx
from BTrees import OOBTree

def contract(func):
    def inner_func(*args,**kwargs):
        res = func(*args,**kwargs)
        if res is True or res is False:
            return res
        else:
            raise ValueError("Contract did not specify a correct result!")
			
    return inner_func



class SymbolDecoder(Decoder.Decoder):
    def __init__(self,jitter_magnitude=5.0):
        try:
            #see if this is the first time we've called init
            self.initialized
            
        except AttributeError:
            #if it is, mark it as so
            self.initialized = True
            self.work = OOBTree.OOBTree()
            #and call it's parent's init as well
            Decoder.Decoder.__init__(self)
			
        self.narrow_start = None
        self.wide_start = None
        self.symbol_start = None
        
        self.modulus = 0.5
        self.jitter_magnitude = jitter_magnitude
        self.narrow_mod_count = 1
        self.wide_mod_count = 2
        self.last_pulse = None
	
    @property
    def jitter(self):
        return mx.DateTime.DateTimeDeltaFrom(self.modulus/self.jitter_magnitude)

	#verify pulse output?
    
    def verify_decode_input(func):
        def inner_func(*args,**kwargs):
            pulse = args[1]
            try:
                pulse.timeStamp
            except AttributeError:
                print "Pulse must have timeStamp!"
                return
            
            data = func(*args,**kwargs)
            return data
        return inner_func

    def verify_basics(func):
        def inner_func(*args,**kwargs):
            #define the contracts we wish to check before exuting the method
            my_self = args[0]
            pre_contracts = [my_self.identifiers_contract,
                             my_self.symbols_contract,
                             my_self.start_contract,
                             ]
			
            #check if the contracts are honored
            honored = my_self.honor_contracts(pre_contracts)
			
            #if not we can simply return
            if not honored:
                print "Pre Contracts not Honored!"
                return
			
            #if so we can call the function
            data = func(*args,**kwargs)
			
            #define the contracts we wish to enforce on the
            data_contracts = []
			
            #run the post contracts
            post_contracts = [my_self.start_contract,
                              ]
			
            post_honored = my_self.honor_contracts(post_contracts)
			
            if not post_honored:
                print "Post Contracts not Honored!"
                return
            
            return data
			
        return inner_func


    @verify_decode_input
    @verify_basics
    def decode(self,pulse):
        #verify the input
        #if not isinstance(pulse,Pulse):
        #    return

        #print pulse
        #else let's put it in our working buffer

        if self.last_pulse is not None:
            #if the difference between the two pulses is bigger than 5  modulus - jitter - this is defined in the spec
            if float( pulse.timeStamp - self.last_pulse.timeStamp ) >= self.modulus*5.0 - self.jitter:
                self.__init__() #reset
                
        self.last = pulse
        self.work[pulse.timeStamp] = pulse
        
        #now we can begin to decode
        #if we don't have the min and max values, we need to find an identifier
        symbol = None
        if self.narrow_start is None:
            symbol = self.find_sync()

        else:

            test_pulse = self.work.minKey()

            if test_pulse <= self.narrow_start + self.jitter and test_pulse >= self.narrow_start - self.jitter or test_pulse <= self.wide_start + self.jitter and test_pulse >= self.wide_start - self.jitter:
                pass
            else:
                #we must reset
                self.__init__()
                return
            
            
            symbol = self.find_symbol()


        #if we've found a symbol, either a sync or a data symbol
        if symbol is not None:
            #print "Symbol",symbol
            #calculate the actual decoded modulus
            new_modulus = symbol.calcModulusTimeBase()
            #print new_modulus
            #average in the old modulus with the new one
            #print new_modulus
            self.modulus = (new_modulus + self.modulus)/2.0 
            
            #calculate the modulus counts for the next possible wide or skinny pulse, and the time at which the symbol should start
            narrow_start_mod_count,wide_start_mod_count,symbol_start_mod_count = symbol.firstPossiblePeakAfter()
            
            #calculate the literal timings for the above mentioned boundaries
            last_pulse_timestamp = symbol.pulses[-1].timeStamp
            
            diff = mx.DateTime.DateTimeDeltaFrom(0.0)
            if self.wide_start is not None:
                bar_wide = False
                for bar in symbol.bars:
                    if bar.peak:
                        bar_wide = bar.wide
                        break

                if bar_wide:
                    diff = self.wide_start - symbol.pulses[0].timeStamp
                else:
                    diff = self.narrow_start - symbol.pulses[0].timeStamp
            
                #print diff
                        
            self.narrow_start = last_pulse_timestamp + mx.DateTime.DateTimeDeltaFrom(narrow_start_mod_count * self.modulus) - diff
            self.wide_start = last_pulse_timestamp + mx.DateTime.DateTimeDeltaFrom(wide_start_mod_count * self.modulus) - diff
            self.symbol_start = last_pulse_timestamp + mx.DateTime.DateTimeDeltaFrom(symbol_start_mod_count * self.modulus) - diff

            #print self.narrow_start
            #print self.wide_start
            #print self.symbol_start
            return symbol

    def verify_find_symbol(func):
        def inner_func(*args,**kwargs):
            my_self = args[0]
            
            #record the length of self.work before we call the function
            pre_work_length = len(my_self.work)

            res = func(*args,**kwargs)

            if res is not None:
                bars = res[0]
                pulses = res[1]
                
            #we need to make sure the decoded symbol is 14 modulus
                modulus_count = 0
                for b in bars:
                    if b.wide:
                        modulus_count += my_self.wide_mod_count
                    else:
                        modulus_count += my_self.narrow_mod_count
                if modulus_count != 14:
                    print "Bars are invalid! It is not 14 modulus!"
                #the symbol is invalid, and therefore we can't deal with it, we need to reset
                    my_self.__init__()
                    
                #a particular symbol must have exactly two wide peaks and two wide valleys
                wide_bar_count = 0
                wide_space_count = 0
                for b in bars:
                    if b.wide:
                        if b.peak:
                            wide_bar_count += 1
                        else:
                            wide_space_count += 1

                if wide_bar_count != 2 or wide_space_count != 2:
                    print "Symbol does is not valid! It does not have the proper number of bars or spaces."
                    my_self.__init__()

                keys_popped = 0
                keys_to_pop = my_self.work.keys(max=pulses[-1])
                for k in range(len(keys_to_pop)-1):
                    keys_popped += 1
                    my_self.work.pop(my_self.work.minKey())

                if ( pre_work_length - keys_popped ) != len(my_self.work):
                    print "What!!?"

                #now we need to find the actual symbol and return it
                decoded_symbol = None
                for sym in my_self.symbols:
                    if sym.bars == bars:
                        decoded_symbol = copy(sym)

                if decoded_symbol is None:
                    print "Holy crap!"
                else:
                    decoded_symbol.pulses = pulses
                    #print my_self.wide_start
                    #print my_self.narrow_start
                    decoded_symbol.timeStamp = my_self.symbol_start
                    
                #return the decoded symbol
                return decoded_symbol
            
        return inner_func

    @verify_find_symbol
    def find_symbol(self):
        """Decodes a data symbol from a series of pulses"""
        #to check that we have can properly decode a symbol we must know that we have a pulse after the latest possible time the last peak can occur
        #if len(self.work) < 5:
            #print "We don't yet have enough pulses"
        #    return

        #print "!!",self.symbol_start
        #print "!!",self.narrow_start
        #print "!!",self.wide_start

        #print "!",len(self.work.keys(min=(self.symbol_start + mx.DateTime.DateTimeDeltaFrom(14.0*self.modulus))))
        
        
        #make sure pulses exist after the symbol we're trying to decode
        if len(self.work.keys(min=(self.symbol_start + mx.DateTime.DateTimeDeltaFrom(14.0*self.modulus)))) == 0:
            return

        #if len(self.work.keys)

        #print len(self.work)
        #for key in self.work.keys():
        #    print key
        #to hold the decoded bars as we find them
        bars = []
        #to hold all of the optimum pulses
        pulses = []
        #get all of the keys that fall within the start boundary of a narrow pulse
        start_max = self.narrow_start + self.jitter
        start_min = self.narrow_start - self.jitter

        narrow_start_keys = self.work.keys(min=start_min,max=start_max)

        
        start_max = self.wide_start + self.jitter
        start_min = self.wide_start - self.jitter

        wide_start_keys = self.work.keys(min=start_min,max=start_max)
        

        if len(narrow_start_keys) > 0 and len(wide_start_keys) > 0:
            print "Reset, we have pulses for both a possible narrow and wide first pulse."
            self.__init__()
            return
            
        if len(narrow_start_keys) > 0:
            bars.append(Bar(True))
            start_keys = narrow_start_keys
            optimum_start = self.narrow_start
        else:
            bars.append(Bar(True,wide=True))
            start_keys = wide_start_keys
            optimum_start = self.wide_start
            
        temp_keys = []
        diffs = []
        for key in start_keys:
            temp_keys.append(key)
            diffs.append(abs(float(optimum_start-key)))
            
        #print "Found start:",self.work[temp_keys[diffs.index(min(diffs))]]
        pulses.append(self.work[temp_keys[diffs.index(min(diffs))]])

        #now that we have identified the first peak, we can continue throughout the rest of the peaks
        wide_space = mx.DateTime.DateTimeDeltaFrom(self.modulus*self.wide_mod_count)
        wide_pulse = mx.DateTime.DateTimeDeltaFrom((self.modulus*self.wide_mod_count)/2.0)
        narrow_space = mx.DateTime.DateTimeDeltaFrom(self.modulus*self.narrow_mod_count)
        narrow_pulse = mx.DateTime.DateTimeDeltaFrom((self.modulus*self.narrow_mod_count)/2.0)
        
        #we have four remaining pulses
        for i in range(4):
            #print "Searching for combination:",i
            #ERROR CHECKING HERE
            if bars[-1].wide:
                last_bar = wide_pulse
            else:
                last_bar = narrow_pulse
            
            wide_wide_opt = pulses[-1].timeStamp + last_bar + wide_space + wide_pulse
            wide_narrow_opt = pulses[-1].timeStamp + last_bar + wide_space + narrow_pulse
            narrow_narrow_opt = pulses[-1].timeStamp + last_bar + narrow_space + narrow_pulse
            narrow_wide_opt = pulses[-1].timeStamp + last_bar + narrow_space + wide_pulse

            possible = [wide_wide_opt,wide_narrow_opt,narrow_narrow_opt,narrow_wide_opt]
            new_bars = [[Bar(False,wide=True),
                         Bar(True,wide=True)],
                        [Bar(False,wide=True),
                         Bar(True)],
                        [Bar(False),
                         Bar(True)],
                        [Bar(False),
                         Bar(True,wide=True)]]
                        
                         
            best_match = []
            quality = []
            for p in possible:
                #print "Optimum:",p
                start_max = p + self.jitter
                start_min = p - self.jitter
            
                keys = self.work.keys(min=start_min,max=start_max)
                
                if len(keys) == 0:
                    best_match.append(None)
                    quality.append(None)
                elif len(keys) == 1:
                    best_match.append(self.work[keys[0]])
                    quality.append(float(abs(p-keys[0])))
                else:
                    best_pulse = None
                    best_quality = None

                    for k in keys:
                        if best_pulse is None:
                            best_pulse = keys[k]
                            best_quality = float(abs(p-k))
                        else:
                            qual = float(abs(p-k))
                            if qual < best_quality:
                                best_pulse = keys[k]
                                best_quality = qual
                    if best_quality is not None:
                        quality.append(best_quality)
                        best_match.append(best_pulse)

            #print best_match
            #print quality

            qual = None
            for q in quality:
                if q is not None:
                    if qual is None:
                        qual = q
                        
                    else:
                        if q < qual:
                            qual = q
                            
            if qual is not None:
                pulses.append(best_match[quality.index(qual)])
                bars.extend(new_bars[quality.index(qual)])
            else:
                #we reset cause we couldn't find a good pulse
                print "Resetting"
                self.__init__()
                return
            
            #finding the last space
        #print "Finding the last space!"
        symbol_boundary = self.symbol_start + mx.DateTime.DateTimeDeltaFrom(14.0 * self.modulus)
        diff = symbol_boundary - pulses[-1].timeStamp
        #print "!!!",diff
        
        if bars[-1].wide:
            wide_space_diff = wide_pulse + wide_space
            narrow_space_diff = wide_pulse + narrow_space
        else:
            wide_space_diff = narrow_pulse + wide_space
            narrow_space_diff = narrow_pulse + narrow_space
            
        if diff < wide_space_diff + self.jitter and diff > wide_space_diff - self.jitter:
            bars.append(Bar(False,wide=True))
        if diff < narrow_space_diff + self.jitter and diff > narrow_space_diff - self.jitter:
            bars.append(Bar(False))
        else:
            pass #ERROR CHECKING CODE

        #print bars
        #now we can check out the bars
        
        #a symbol must end up as 14.0 modulus

        #ERROR CHECKING CODE HERE
        #print "!",decoded_symbol

        #return decoded_symbol
        return bars, pulses
                
            
            
            
#             wide_wide_keys = self.work.keys(min=wide_wide_start_min,max=wide_wide_start_max)
#             print len(wide_wide_keys)
#             wide_narrow_keys = self.work.keys(min=wide_narrow_start_min,max=wide_narrow_start_max)
#             print len(wide_narrow_keys)
#             narrow_narrow_keys = self.work.keys(min=narrow_narrow_start_min,max=narrow_narrow_start_max)
#             print len(narrow_narrow_keys)
#             narrow_wide_keys = self.work.keys(min=narrow_wide_start_min,max=narrow_wide_start_max)
#             print len(narrow_wide_keys)

#             wide_wide_best_match = None
#             wide_wide_match_quality = None
#             if len(wide_wide_keys) > 1:

#             elif len(wide_wide_keys) == 1:
#                 wide_wide_best_match = self.work[wide_wide_keys.minkey()]
#                 wide_wide_best_match_quality = abs(wide_wide_opt-wide_wide_best_match)
            
            
                                            

        
            

            

        
        
        
    
        #for i in start_keys:
            
        #    pass
			
    def find_sync(self):
        #check to make sure we've got as many pulses as the maximum amount of pulses in any identifier as well as the post of the first symbol
        if len(self.work)-1 < self.maxIdentifierPeaks:
            return

        pulse_deltas = []
        last = None
        for pulses in self.work:
            if last is not None:
                pulse_deltas.append(float(pulses-last))
            last = pulses

        match = False

        for identifier in self.identifiers:
            identifier_deltas = identifier.calcDeltas()

            match = True
            for i in range(len(identifier_deltas)-1):
                match = match and identifier_deltas[i] + self.jitter >= pulse_deltas[i]
                match = match and identifier_deltas[i] - self.jitter <= pulse_deltas[i]

            match = match and float(pulse_deltas[len(identifier_deltas)-1]) >= float(identifier_deltas[-1]) - float(self.jitter)

            if match:
                save_pulses = []
                for j in range(identifier.numPeaks()):
                    save_pulses.append(self.work.pop(self.work.minKey()))
                identifier = copy(identifier)
                identifier.pulses = save_pulses
                identifier.timeStamp = identifier.symbolStart()
                return identifier
            
        if not match:
            self.work.pop(self.work.minKey())

    def honor_contracts(self,contracts):
        honored = True
        for c in contracts:
            honored = honored and c()
        return honored

    @contract
    def pulse_contract(self,obj):
        pass
	
    @contract
    def identifiers_contract(self):
        """Checks to make sure that this decoder has the proper identifers attached"""
        err = ValueError("Identifiers have not been defined for this decoder, and hence we cannot decode.")
        try:
            #make sure that identifiers
            if len(self.identifiers) == 0:
                raise err
        except TypeError:
            raise err

        #else we're good
        return True
	
    @contract
    def symbols_contract(self):
        """CHecks to make sure that this decoder has the proper symbols attached"""
        err = ValueError("Symbols have not been defined for this decoder and hence we cannot decode.")
        try:
            if len(self.symbols) == 0:
                raise err
        except TypeError:
            raise err
        
        return True

    @contract
    def start_contract(self):
        if self.narrow_start is None or self.wide_start is None or self.symbol_start is None:
            if self.narrow_start is not None:
                #we need to call a reset
                #self.__init__()
                return False
            if self.wide_start is not None:
                #self.__init__()
                return False
            if self.symbol_start is not None:
                return False
            
		
        if self.narrow_start is not None or self.wide_start is not None or self.symbol_start is not None:
            if self.narrow_start is None:
                #self.__init__()
                return False
            if self.wide_start is None:
                #self.__init__()
                return False
            if self.symbol_start is None:
                return False

        return True
			

if __name__ == '__main__':
    import unittest
    from PyDrill.Generation.TwoOfFive import Symbols
    import mx.DateTime
    
    class SymbolDecoderTests(unittest.TestCase):
        def setUp(self):
            """This function sets up common variables for the following tests"""
            sim = TwoOfFiveSimulator.TwoOfFiveSimulator()			
            sim.addSymbols(symbols=Symbols.generateSymbols(),identifiers=Symbols.generateIdentifiers())
            
            self.sim = sim
            
            sd = SymbolDecoder() #get a chirp decode instance and populate it
            sd.addSymbols(symbols=Symbols.generateSymbols(),identifiers=Symbols.generateIdentifiers())
            self.sd = sd
            
            self.symbols = Symbols.generateSymbols()
            self.identifiers = Symbols.generateIdentifiers()

        def testSetup(self):
            pass

        def testInst(self):
            t = SymbolDecoder()

# 		def testDebug(self):
# 			self.setup()
# 			symbols = [self.sim.symbols[0],self.sim.identifiers[0],self.sim.symbols[-1]]
# 			print symbols
# 			pulses = self.sim.make(symbols,mx.DateTime.now())
# 			pulses.append(Pulse(timeStamp=pulses[-1].timeStamp + mx.DateTime.DateTimeDeltaFrom(10)))
# 			print "Pulses"
# 			for p in pulses: print p
# 			print "End Pulses"
# 			for p in pulses:
# 				data = self.sd.decode(p)
# 				if data is not None:
# 					print "Algorithm Decoded!: ", data

        def testAllSymbols(self):
            t = mx.DateTime.now()
			
            for identifier in self.identifiers:
                sequence = []
                sequence.append(identifier)
                sequence.extend(self.symbols)
					
			
                pulses,t = self.sim.make(sequence,t)

                pulses.append(Pulse(timeStamp=pulses[-1].timeStamp+mx.DateTime.DateTimeDeltaFrom(10)))
			
                decoded_symbols = []
                for p in pulses:
                    decoded = self.sd.decode(p)
                    if decoded is not None:
                        decoded_symbols.append(decoded)
				

				
                symbolValues = []
                for symbol in sequence: symbolValues.append(symbol.value)
                decodedSymbolValues = []
                for s in decoded_symbols: decodedSymbolValues.append(s.value)
			
					
                self.failUnlessEqual(decodedSymbolValues,symbolValues)

        def testAllSymbolsIndividually(self):
            from BTrees import OOBTree
            t = mx.DateTime.now()
            
            for identifier in self.identifiers:
                for symbol in self.symbols:
                    #print symbol
                    #print symbol.bars
                    testSymbols = [identifier,symbol]
                    
                    pulses,t = self.sim.make(testSymbols,t)
                    
                    pulses.append(Pulse(timeStamp=pulses[-1].timeStamp+mx.DateTime.DateTimeDeltaFrom(10)))
                    
                    #print "Generated ", len(pulses), "pulses"
                    #for p in pulses: print p
                    #print "End Generated Pulses"
                    #print 
                    decoded = False
                    data = []
                    for pulse in pulses:
                        new_data = self.sd.decode(pulse)
                        if new_data is not None:
                            #print new_data
                            data.append(new_data)
                    
                    self.failUnlessEqual(data[1].value,symbol.value)

                    #print data[1].bars
                    #print "!!",len(self.sd.work)
                    if len(self.sd.work)==1:
                        self.sd.work = OOBTree.OOBTree()
							#print data
                    #if not decoded:
                    #    self.fail()

					
					
					
				

        def testRandomChirpSequence(self):
            import random
            
            for iteration in range(random.randint(0,10)):
                self.setUp()
                for identifier in self.identifiers:
                    t = mx.DateTime.now()
                    symbols = [identifier]
                    
					
                    for i in range(random.randint(1,99)):
                        symbols.append(self.symbols[random.randint(0,99)])
					
						       
                    pulses,t = self.sim.make(symbols,t)

                    pulses.append(Pulse(timeStamp=pulses[-1].timeStamp+mx.DateTime.DateTimeDeltaFrom(10)))

                    decodedSymbols = []
                    for p in pulses:
                        newSymbol = self.sd.decode(p)
                        if newSymbol is not None:
                            decodedSymbols.append(newSymbol)
					
                    decodedSymbolValues = []
                    for dS in decodedSymbols: decodedSymbolValues.append(dS.value)
                    symbolValues = []
                    for s in symbols: symbolValues.append(s.value)
                    
                    self.failUnlessEqual(decodedSymbolValues,symbolValues)
                                        
        def testElevenChirpSequence(self):
            for identifier in self.identifiers:
                t = mx.DateTime.now()
                symbols = [identifier]
                for i in range(10):
                    symbols.append(self.symbols[i*11])
                    
                pulses,t = self.sim.make(symbols,t)
                pulses.append(Pulse(timeStamp=pulses[-1].timeStamp+mx.DateTime.DateTimeDeltaFrom(10)))
                
                decodedSymbols = []
                for p in pulses:
                    newSymbol = self.sd.decode(p)
                    if newSymbol is not None:
                        decodedSymbols.append(newSymbol)
				
                symbolValues = []
                for s in symbols: symbolValues.append(s.value)
                decodedSymbolValues = []
                for dS in decodedSymbols: decodedSymbolValues.append(dS.value)
                self.failUnlessEqual(decodedSymbolValues,symbolValues)
                
				
			
					 
				
            
    unittest.main()
        
