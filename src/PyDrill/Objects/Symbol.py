from persistent import Persistent
import persistent.list
from PyDrill import Debug
import mx.DateTime
from PyDrill.Objects.PyDrillObject import PyDrillObject

class Symbol(Persistent,PyDrillObject):
    """This class represents a basic chirp"""
    #constructor
    def __init__(self,value=None,bars=None,timeStamp=None,pulses=None):
        """Takes the place of a default constructor. Arguments must either be the value of the chirp and the associated deltas, or an 4Suite XML Element"""

        self.value = value
        self.timeStamp = timeStamp
        
        self.bars = persistent.list.PersistentList()
        if bars:
            self.bars.extend(bars) #take them if we've got them
            
        self.pulses = persistent.list.PersistentList()
        if pulses:
            self.pulses.extend(pulses)
		 
        self.fileKey = 'symbol'

        self.wide_mod_count = 2.0
        self.narrow_mod_count = 1.0
        
			 
    def __copy__(self):
        return Symbol(value=self.value,bars=self.bars,timeStamp=self.timeStamp,pulses=self.pulses)
	 
	 #functions

# 	 def writeToXml(self,writer):
# 		 writer.startElement(u'Symbol')
# 		 if self.value is not None:
# 			 writer.simpleElement(u'Value',content=unicode(self.value))

# 		 if self.timeStamp!=None:
# 			 writer.simpleElement(u'TimeStamp',content=unicode(self.timeStamp))
		 
# 		 if self.bars is not None:
			 
		 

    def __len__(self):
        """Retruns the length of the symbol in modulus"""
        if self.bars is not None:
            modCount = 0
            for b in self.bars:
                if b.wide:
                    modCount += 2
                else:
                    modCount += 1
                    
            return modCount
			 
    def __val__(self):
        return self.value

    def symbolStart(self):
        """Returns the theoretical time that the symbol started based on the peaks present in the symbol."""
        rolling = 0.0
        for bar in self.bars:
            if bar.peak:
                if bar.wide:
                    rolling += self.wide_mod_count/2.0
                else:
                    rolling += self.narrow_mod_count/2.0
            else:
                if bar.wide:
                    rolling += self.wide_mod_count
                else:
                    rolling += self.narrow_mod_count

        return self.pulses[-1].timeStamp - mx.DateTime.DateTimeDeltaFrom(self.calcModulusTimeBase()*rolling)

    def firstPossiblePeakAfter(self,debug=False):
        """Returns the count in modulus from the last peak of a symbol until the time where a new peak can occur."""
        if debug:
            print

        myErr = ValueError('All elements required not defined.')
        if self.bars is None:
            raise myErr
        if self.pulses is None:
            raise myErr
        try:
            if len(self.pulses) == 0:
                raise myErr
        except TypeError:
            pass

		 #finding the last pulse in the symbol
        index = 0
        for b in range(len(self.bars)):
            if self.bars[b].peak:
                index = b
		 
        sum = 0
        if debug:
            print "Units after bar"
        if self.bars[index].wide:
            sum += 2.0/2.0
        else:
            sum += 1.0/2.0
			 
        for b in self.bars[index+1:]:
            if debug:
                print b
            if b.wide:
                sum += 2.0
            else:
                sum += 1.0

		 #since the quickest a pulse can occur is a narrow peak
		 #sum += 1.0/2.0
        narrow_start = sum + 1.0/2.0
        wide_start = sum + 2.0/2.0
        
        if debug:
            print sum

        symbol_start = sum

        return narrow_start,wide_start,symbol_start
				 
				 
			 
    def calcModulus(self):
        if self.bars is None: raise ValueError("Bars are not defined")
		 #print self.calcDeltas(cap=False)
		 #print self.numPeaks()
        return float(sum(self.calcDeltas(cap=False)))/float(self.numPeaks()-1)/2

    def calcModulusTimeBase(self):
        """Calculates the actual timebase based upon the bars and attached pulse times."""
        
        #if we don't have pulses or bars
        if len(self.pulses)==0 or len(self.bars) == 0:
            raise ValueError("Bars and/or Pulses are not defined")

        #if the number of pulses we have doesn't equal the number we should have
        if self.numPeaks() != len(self.pulses):
            raise ValueError("Symbol does not have as many pulses as peaks")
        
        #calculate the modulus from the beginning of the symbol to the end for each peak
        mods = []
        rolling = 0
        for b in self.bars:
            if b.wide:
                rolling += 2.0
            else:
                rolling += 1.0
				 
            if b.peak:
                if b.wide:
                    mods.append(rolling - 1.0)
                else:
                    mods.append(rolling - 0.5)

		 #calculate the differences between those modulus
        modsBetween = []
        
        last = None
        for m in mods:
            if last is not None:
                modsBetween.append(m-last)
            last = m

        #and calculate the difference between those deltas
        deltas = []
        last = None
        for d in self.pulses:
            if last is not None:
                deltas.append(float(d.timeStamp-last.timeStamp))
            last = d

        bases = []
		 
        #calculate the time base by delta/#mods
        for i in range(len(modsBetween)):
            bases.append(deltas[i]/modsBetween[i])
            
		 
        return sum(bases)/len(bases) #return the average of the mods

		 
		 
		 

	 
    def numPeaks(self):
        """Calculats the number of peaks in a symbol"""
        if self.bars is None:
            raise ValueError("Bars are not defined")
        count = 0
        for b in self.bars:
            if b.peak:
                count +=1
				 
        return count

    def calcDeltas(self,cap=True):
        from PyDrill.Objects.Bar import Bar
        from copy import copy

        if self.bars is None:
			 return []
		 
        modulus = 0.5

        last = None
        sum = 0.0
        deltas = []
		 
        newBars = []
        for b in self.bars:
            newBars.append(b)
		 
        if cap:
            newBars.append(Bar(True))
            
        for b in newBars:
            if last is None:
                if b.peak:
                    last = b
                    if b.wide:
                        sum += modulus
                    else:
                        sum += modulus/2.0
            else:
                if b.peak:
                    last = b
                    if b.wide:
                        deltas.append(sum+modulus)
                        osum = modulus
                    else:
                        deltas.append(sum+modulus/2.0)
                        sum = modulus/2.0
					 
					 
				 
                else:
                    if b.wide:
                        sum += modulus*2.0
                    else:
                        sum += modulus

        return deltas
			 
			 


	 #OPERATOR OVERLOADING

    def __eq__(self, other, debug=False):
        """This function overloads the == operator and allows comparison of chirps"""
		 
        if not isinstance(other,Symbol):
            return NotImplemented

		 
        if self.bars != other.bars:
            return False

        if self.value and other.value: #if the values are defined
            if (self.value!=other.value):
                return False
            
        if self.timeStamp and other.timeStamp: #if the timeStamps exist
            if self.timeStamp!=other.timeStamp: #check
                return False
            
        if self.pulses and other.pulses: #if the pulses exist
            if debug:
                print "Test Pulses"
        
            if self.pulses!=other.pulses: #check
                return False

        return True #if we've made it this far they're equal

	 #printing
	 #called by the repr(obj) function
    def __repr__(self):
        t =  "Symbol"
        
        if self.value is not None:
            t += " val: " + unicode(self.value)
            t += ' '
		 
        if self.bars is not None:
            t += " Length: " + unicode(self.__len__())
            t += ' '

        if self.timeStamp is not None:
            t += "TimeStamp: " + str(self.timeStamp)

        return t

	 #called by the str(obj) function
    def __str__(self):
        return self.__repr__() #simply call this methods __repr__ function which does the same thing



if __name__ == '__main__':
    import unittest
    import mx.DateTime
    import sys
    from PyDrill.Generation.TwoOfFive import Symbols
    
    class SymbolObjectTests(unittest.TestCase):
        def setUp(self):
            from PyDrill.Objects.Bar import Bar
            
            t = mx.DateTime.now()
            ts = []
            for i in range(3):
                ts.append(t+mx.DateTime.DateTimeDeltaFrom(i))

            self.testSymbol1 = Symbol(value=4,bars=[Bar(False),Bar(True),Bar(False),Bar(True,wide=True),Bar(False),Bar(True),Bar(False),Bar(False)],pulses=ts)
            self.symbols = Symbols.generateSymbols()

        def testCopy(self):
            from copy import copy,deepcopy
            self.failUnlessEqual(self.testSymbol1,copy(self.testSymbol1))

#        def loadXML(self):
#            from Ft.Xml import Parse
#
#            xmlFile = file('chirps.xml','r')
#            doc = Parse(xmlFile)
#            self.chirpTags = doc.xpath('//Symbol')

        def testFirstPossiblePeakAfter(self):
            self.testSymbol1.firstPossiblePeakAfter(debug=False)

        def testEQ(self):
            self.failUnlessEqual(self.testSymbol1,self.testSymbol1)
            

        def testPersistence(self):
            Debug.writeToFS(self.testSymbol1)
            self.failUnlessEqual(self.testSymbol1,Debug.readFromFS())
			
#        def testXML(self):
#            self.loadXML()
#            chirps = []
#            for ct in self.chirpTags:
#                chirps.append(Symbol(xml=ct))

#        def testXMLPersistence(self):
#            self.loadXML()
#            chirps = []
#            for ct in self.chirpTags:
#                chirps.append(Symbol(xml=ct))
#            for c in chirps:
#                Debug.writeToFS(c)
#                self.failUnlessEqual(Debug.readFromFS(),c)

        def testEqualNone(self):
            self.failIfEqual(self.testSymbol1,None)
		
	def testCalcDeltas(self):
            self.testSymbol1.calcDeltas()
                
        def testLen(self):
            for symbol in self.symbols:
                self.failUnlessEqual(len(symbol),14.0)
            
            
    unittest.main()
