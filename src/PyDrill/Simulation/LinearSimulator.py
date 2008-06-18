from PyDrill.Decoders import Decoder
from PyDrill.Objects import Pulse
from PyDrill import DataStructures
from mx.DateTime import *
import random
from copy import deepcopy

import mx

class LinearSimulator(Decoder.Decoder):
    def __init__(self,**kw):
        Decoder.Decoder.__init__(self,**kw)

    def make(self,chirps,timeStamp,debug=False):
        
        try:
            self.chirps
        except AttributeError:
            raise AttributeError("Chirps have not been loaded for this decoder!")

        realChirps = []

        
        #for every chirp
        for chirp in chirps:
            if chirp.value!=None:
                value = chirp.value #if it has a value
            else: 
                value = random.randint(0,15) #if not, create a random one
                
            for realChirp in self.chirps: #find the corresponding real chirp
                
                if (len(realChirp)==len(chirp)): #the the len
                    if (value==realChirp.value): #and the val match
                        realChirps.append(realChirp) #keep the real chirp
                        break #quit when you're done

        #once we've found all of the real chirps
        #we need to generate all of the pulses
        if debug:
            for rc in realChirps:
                print rc
        pulses = DataStructures.UPQueue()

        #pulses.append(Pulse(timeStamp=timeStamp))
        
        for chirp in realChirps:
            saveTimeStamp = timeStamp
            for d in chirp.deltas:
                pulses.append(Pulse.Pulse(timeStamp=timeStamp))
                timeStamp += DateTimeDeltaFrom(d)
            #timeStamp += DateTimeDeltaFrom(10)
        pulses.append(Pulse.Pulse(timeStamp=timeStamp))
                

            #NO LONGER NEEDED NOW THAT CHIRPS ARE BACK TO BACK
            # if sum(chirp.deltas)<=7:
#                 diff = (saveTimeStamp + DateTimeDeltaFrom(7)) - timeStamp
#                 timeStamp += diff
#             elif sum(chirp.deltas)>7 and sum(chirp.deltas)<=9:
#                 diff = (saveTimeStamp + DateTimeDeltaFrom(9)) - timeStamp
#                 timeStamp += diff
#             elif sum(chirp.deltas)>9 and sum(chirp.deltas)<=15:
#                 diff = (saveTimeStamp + DateTimeDeltaFrom(15)) - timeStamp
#                timeStamp += diff

            #if len(chirp)==4:
            #    diff = (saveTimeStamp + DateTimeDeltaFrom(9)) - timeStamp
            #    timeStamp += diff
            #elif len(chirp)==5:
            #    diff = (saveTimeStamp + DateTimeDeltaFrom(15)) - timeStamp
            #    timeStamp += diff
            #elif len(chirp)==6:
            #    diff = (saveTimeStamp + DateTimeDeltaFrom(15)) - timeStamp
            #    timeStamp += diff
                
        newPulses = deepcopy(pulses)

        #first = newPulses.pop(0)

        #for r in newPulses:
            #print r.timeStamp-first.timeStamp
        #    first = r

        return [pulses,timeStamp]

    def makec(self,chirps):

        realChirps = []

        #for every chirp
        for chirp in chirps:
            if chirp.value!=None:
                value = chirp.value
            else:
                value = random.randint(0,15) #if not, create a random one
                
            for realChirp in self.chirps: #find the corresponding real chirp
                
                if (len(realChirp)==len(chirp)): #the the len
                    if (value==realChirp.value): #and the val match
                        realChirps.append(realChirp) #keep the real chirp
                        break #quit when you're done

        return realChirps
    
if __name__ == '__main__':
    import unittest
    class SimulationTests(unittest.TestCase):
        def setup():
            pass
        
        def testInst(self):
            t = Simulator()

    unittest.main()
    
