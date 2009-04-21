from PyDrill.Decoders.Decoder import Decoder
from PyDrill.Decorators import contract
from copy import copy
import mx.DateTime

class FrameDecoder(Decoder):
    def __init__(self,*args,**kwargs):
        try:
            self.initialized
        except AttributeError:
            Decoder.__init__(self,*args,**kwargs)
            self.initialized = True

        self.sync = None
        self.identifier = None
        self.last_time_stamp = None
        self.last_symbol = None
        self.modulus = 0.5
        self.work = []
        


    def verify_decode_input(func):
        def inner_func(*args,**kwargs):
            my_self = args[0]
            new_symbol = args[1]
            
            mod_diff = None
            if my_self.sync is not None:
                mod_diff = len(my_self.sync)
                last_ts = my_self.sync.timeStamp
            if my_self.identifier is not None:
                mod_diff = len(my_self.identifier)
                last_ts = my_self.identifier.timeStamp
            if my_self.last_symbol is not None:
                mod_diff = len(my_self.last_symbol)
                last_ts = my_self.last_symbol.timeStamp
                
            if mod_diff is not None:
                diff = mx.DateTime.DateTimeDeltaFrom(mod_diff*my_self.modulus)
                range = mx.DateTime.DateTimeDeltaFrom(my_self.modulus)

                if new_symbol.timeStamp > last_ts + diff + range or new_symbol.timeStamp < last_ts + diff - range:
                    
                    print "Timing violation!"
                    my_self.__init__()
                    return
            
            data = func(*args,**kwargs)
            return data
        return inner_func
    
    def verify(func):
        def inner_func(*args,**kwargs):
            my_self = args[0]
            data = func(*args,**kwargs)
            return data
        return inner_func
    
    #@verify_decode_input
    def decode(self,symbol,debug=False):

        if self.sync is None:
            if symbol.value < 0:
                if debug:
                    print "Got Sync",symbol
                self.sync = symbol
            return

        else:
            if symbol.value < 0:
                self.__init__()
                if debug:
                    print "Resetting, new sync",symbol
                self.sync = symbol
                return

        if self.identifier is None:
            try:
                self.frames[symbol.value] #make sure we have a frame that pertains to the frame id
                #check to make sure the it's within the timing constraints                
                if debug:                
                    print "Got identifier",symbol
                self.identifier = symbol
            except KeyError:
                if debug:
                    print "Resetting, invalid identifier",symbol
                self.__init__()
                return

            #self.identifier = symbol
            return

        if debug:
            print "New Work",symbol
        self.work.append(symbol)
        self.last_symbol = symbol
        
        if len(self.work) == len(self.frames[self.identifier.value]) - 1:
            decoded_frame = copy(self.frames[self.identifier.value])
            decoded_frame.symbols = self.work
            return decoded_frame
            
            
            

    
            
    def verify(func):
        def inner_func(*args,**kwargs):
            my_self = args[0]
            data = inner_func(*args,**kwargs)
            return data
        return inner_func
        



    

    
#     def decode(self,symbol,init=False,debug=False):
#         #initialization
#         print "Start"
#         try:
#             self.last
#             self.identifier
#             self.work
#         except AttributeError:
#             self.reset()
            
#         if self.last is None:
#             print "Got last"
#             self.reset(last=symbol)
#             return

#         if self.last is not None and self.identifier is None:
#             if debug: 
#                 print "Possible identifier"

#             #check to see if this symbol meets the timing requirements
#             print "!",self.last
#             print "!!",symbol
#             print "!!",symbol.timeStamp - self.last.timeStamp - mx.DateTime.DateTimeDeltaFrom(sum(self.last.deltas))
#             if symbol.timeStamp - self.last.timeStamp - mx.DateTime.DateTimeDeltaFrom(sum(self.last.deltas)) < 2.0:
#                 print "Resetting due to timing"
#                 self.reset(last=symbol)
                
#             #check if the frame identifier is valid
#             try:
#                 self.frames[symbol.value]
#             except IndexError:
#                 self.reset() # if there's an error, that frame doesn't exist
#                 return
#             #if no error, we're alright
#             self.identifier = symbol
#             return

#         if self.last is not None and self.identifier is not None and symbol.value>0:
#             print "Found data chirp: ", symbol
#             self.work.append(symbol)



#         if self.identifier is not None:
#             #calculate the length of the frame
#             l = 0
#             for subFrame in self.frames[self.identifier.value].subFrames:
#                 l += subFrame.symbolLength

#             if l==len(self.work):
#                 #code for returning a frame here
#                 frame = copy(self.frames[self.identifier.value])
#                 x = 0
#                 for i in range(len(frame.subFrames)):
#                     for j in range(frame.subFrames[i].symbolLength):
#                         if frame.subFrames[i].value is None:
#                             frame.subFrames[i].value = self.work[x].value
#                         elif frame.subFrames[i].value is not None:
#                             frame.subFrames[i].value = frame.subFrames[i].value*100.0 + self.work[x].value
#                         x += 1

#                 self.reset()

#                 return frame

#     def reset(self,last=None,identifier=None,work=None):
#         print "Resetting"
#         self.last = last
#         self.identifier = identifier
#         if work is None:
#             self.work = []
        
            
            
if __name__ == '__main__':
    import unittest
    from PyDrill.Simulation.TwoOfFiveSimulator import TwoOfFiveSimulator
    from PyDrill.Generation.TwoOfFive import Symbols,Frames
    from PyDrill.Objects.Chirp import Chirp

    class TestCases(unittest.TestCase):
        def setUp(self):
            self.symbols = Symbols.generateSymbols()
            self.identifiers = Symbols.generateIdentifiers()
            self.frames = Frames.generate()
            
            simulator = TwoOfFiveSimulator()
            simulator.addSymbols(symbols=Symbols.generateSymbols(),identifiers=Symbols.generateIdentifiers())
            simulator.addFrames(frames=Frames.generate())
            self.simulator = simulator
                               
                                

        def testSetup(self):
            pass
            
        def testAllFrames(self):
            
            import mx.DateTime
            
            for identifier in self.identifiers:
                for frame in self.frames:
                    symbols = []
                    print "!",frame
                    for s in frame.sim():
                        symbols.append(s)
                                
                    t = mx.DateTime.now()
                    #c = Chirp(pulses=[copy(t)])
                    
                    #chirps.insert(0,c)
                    
                    #t += mx.DateTime.DateTimeDeltaFrom(10)
                    data = self.simulator.makec(symbols,t)
                    #for d in data:
                    #    print "!",d
                    new_time_stamp = t - mx.DateTime.DateTimeDeltaFrom(len(identifier)*0.5)
                    
                    #data[0].timeStamp = data[0].timeStamp - mx.DateTime.DateTimeDeltaFrom(2)
                    
                    real_identifier = copy(identifier)
                    real_identifier.timeStamp = new_time_stamp
                    data.insert(0,real_identifier)




                    decoder = FrameDecoder()
                    decoder.addFrames(frames=Frames.generate())
                    
                    for d in data:
                        print "Adding ",d,"to the decoder"
                        new_data = decoder.decode(d)
                        if new_data is not None:
                            #print "!",new_data
                            break

                    if new_data is None:
                        self.fail()
                        
                    self.failUnlessEqual(frame.identifier,new_data.identifier)

        def testFramesSequentially(self):
            
             import mx.DateTime

             symbols = []
             for identifier in self.identifiers:
                 for frame in self.frames:
                     print frame.identifier
                     symbols.append(identifier)
                     for c in frame.sim():
                         symbols.append(c)
                     
                         
            #chirps.append(self.simulator.chirps[0])
             
                 data = self.simulator.makec(symbols,mx.DateTime.now())
                 for d in data:
                     print "!",d
             
                 decoder = FrameDecoder()
                 decoder.addFrames(frames=Frames.generate())
                 decodedFrames = []
                 
                 for d in data:
                     decoded = decoder.decode(d)
                     if decoded is not None:
                         decodedFrames.append(decoded)
                         
                 #for d in decodedFrames: print d.identifier
                 #for f in self.frames: print f.identifier
                 for i in range(len(decodedFrames)):
                     self.failUnlessEqual(decodedFrames[i].identifier,decoder.frames[i].identifier)
                             

#         def testErrorFrames(self):
#             import mx.DateTime

#             from PyDrill.Generation.TwoOfFive import Frames
            
#             frames = Frames.generateErrors()
            
            

#             for frame in frames:
#                 print "!",frame
#                 chirps = []
#                 for c in frame.sim():
#                     print "?",c
#                     chirps.append(c)
#                 chirps.append(self.simulator.chirps[0])
                

#                 data = self.simulator.makec(chirps,mx.DateTime.now())
                
#                 print "!!",data

#                 decoder = FrameDecoder()
#                 decoder.addFrames(frames=Frames.generate())
#                 for d in data:
#                     decoded = decoder.decode(d)
#                     if decoded is not None:
#                         self.fail()
                
            

    
    unittest.main()
