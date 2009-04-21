from PyDrill.Decoders import Decoder
from PyDrill.Objects import Pulse, Chirp, Frame, SubFrame
import mx.DateTime
from copy import deepcopy
from PyDrill.Simulation import NonLinearSimulator

class NonLinearChirpDecoder(Decoder.Decoder):
	def __init__(self,debug=False):
		"""Pulse Decoder Revison 0v04 - KCM"""
		
		Decoder.Decoder.__init__(self,debug=debug) #call the parent class's init as well

	def calculateDeltas(self,pulses):
		deltas = []
		for i in range(len(pulses)-1):
			deltas.append(float(pulses[i+1].timeStamp-pulses[i].timeStamp))
		return deltas

	def runningDeltas(self,times):
		deltas = []
		running = 0.0
		for i in range(len(times)-1):
			deltas.append(float(times[i+1]-times[i])+running)
			running = running + float(times[i+1]-times[i])

		return deltas
	
	def chirpSum(self,chirps):
		deltas = []
		sum = 0 
		for c in chirps:
			deltas.append(sum + float(c))
			sum = sum + c

		return deltas
			

	def decode(self,pulses,trash,jitter,debug=False):
		
		
		#initialization
		jitter = float(jitter) #initialize the jitter
		timeBase = float(1)
		
		#
		lastChirp = None #the finalChirp
		lastAverage = None
		lastAverages = None
		lastLength = None
		lastPulses = None

		if debug:
			print "Here"

		#make sure it's possible to decode
		for chirp in self.chirps:
			p = Pulse.Pulse(pulses[0].timeStamp+mx.DateTime.DateTimeDeltaFromSeconds(sum(chirp.deltas)))
			
			try:
				#print "!"
				temp,exists = pulses.getPulsesBefore(p)
			except Exception, e:
				#print "!",e
				pass

			if not exists:
				if debug:
					print "Premature Exit!"
				return [None,pulses,trash]
				#raise ValueError('No pulses exist past the last possible pulse time, cannot decode.')

		#for every chirp available

		if debug:
			print "Init run."
			
		for chirp in self.chirps:

			p = Pulse.Pulse(pulses[0].timeStamp+mx.DateTime.DateTimeDeltaFromSeconds(sum(chirp.deltas)))

			testPulses,exists = pulses.getPulsesBefore(p)
			
			saveLength = len(testPulses)



			deltas = self.runningDeltas(testPulses)
			saveDeltas = deepcopy(deltas)

			testPulses = deepcopy(testPulses)
			savePulses = deepcopy(testPulses)
			
			averages = []
			
			for i in range(len(chirp.deltas)-1): #CORRECT
			#for i in range(len(chirp.deltas)):
				averages.append([]) #create an array for every pulse

			#if debug:
			#	print "len(tp): ",len(testPulses)

			#chirpDeltas = self.chirpSum(chirp.deltas)
			#chirpDeltas = self.chirpSum(chirp.deltas)
			chirpDeltas = self.chirpSum(chirp.deltas[0:-1]) #CORRECT
				
			for d in deltas:
				#if debug:
				#	print "delta:", d
				quality = []
				for cd in chirpDeltas:
					#if debug:
					#	print "CD:",cd
					#	print "d:",abs(cd-d)
					quality.append(abs(cd-d))
				#if debug:
				#	print "Q:",quality
				averages[quality.index(min(quality))].append(min(quality))
				#if debug:
				#	print "A:",averages

			saveAverages = deepcopy(averages)
			if debug:
				print saveAverages

			for i in range(len(averages)):
				try:
					averages[i] = min(averages[i])
				except:
					averages[i] = None
						     

			for i in range(len(averages)):
				if (averages[i]>(timeBase/jitter)):
					averages[i] = None

			numberMissing = averages.count(None)

			#if debug:
			#	print averages
			

			if numberMissing<1:
				#if numberMissing==1:

				average = sum(averages)/len(averages)
				
				if debug:
					print chirp
					print chirp.deltas
					print averages

				if debug:
					for t in range(len(savePulses)-1):
						print savePulses[t+1] - savePulses[t]

				if lastAverage:
					if len(chirp.deltas)==len(lastChirp.deltas):
						if average<lastAverage:
							lastAverage = average
							lastAverages = averages
							lastChirp = chirp
							lastPulses = savePulses
							lastLength = saveLength
					if len(chirp.deltas)>len(lastChirp.deltas):
						if debug:
							print "rewriting"
							print "!",lastChirp
							print "!!",chirp
							print "!",lastAverage
							print "!!",average
							print "!",lastAverages
							print "!!",averages
						lastAverage = average
						lastAverages = averages
						lastChirp = chirp
						lastPulses = savePulses
						lastLength = saveLength
					  
				else:
					lastAverage = average
					lastAverages = averages
					lastChirp = chirp
					lastPulses = savePulses
					lastLength = saveLength
			
		if lastChirp:
			for z in range(lastLength):
				trash.append(pulses.pop(0))
		else:
			if debug:
				print "Popping since no decode!"
			trash.append(pulses.pop(0))
			
		return [lastChirp,pulses,trash]
	

		
	def olddecode(self,pulses,trash,jitter,debug=False,printDeltas=False,printHeader=False,printAverages=False,printTiming=False,timer=None):		
		
		timeBase = float(1)

		jitterFactor = float(20)

		lastPulsesDecoded = None

		lastChirpDecoded = None
		
		lastChirpAverage = None

		lastNumMissing = 1
		
		if (timer==None):
			timer = now()

		#for every chirp
		instanceTime = now()

		chirpNum = 0
		for chirp in self.chirps:
			
			chirpTime = now()
			if printHeader:
				print "Attempting to decode: ", chirp
			#create a pulse that represents the first possible pulse
			#that can occur after the current chirp
			try:
				p = Pulse.Pulse(pulses[0].timeStamp+mx.DateTime.DateTimeDeltaFromSeconds(sum(chirp.deltas)))
				saveP = p
			except IndexError:
				raise ValueError("The Pulse list is empty! Cannot find first pulse!")

			#get the pulses that exist before this theoretical last pulse
			pulsesBefore,exists = pulses.getPulsesBefore(p)

			if debug:
				print "Pulses Before End-Cap"
				for p in pulsesBefore:
					print p
				
			if not(exists):
				raise ValueError('No pulses exist past the last possible pulse time, this chirp cannot be decoded.')

			save_pulses = deepcopy(pulsesBefore) #make a copy of the pulses we extracted

			pulse_deltas = [] #for holding deltas

			delta = pulsesBefore.pop(0) #take the first pulse
			#firstPulse = delta #it becomes the first pulse #do i need this line? KCM
			
			#finding the deltas between all of the pulses
			for pulse in pulsesBefore:
				pulse_deltas.append(pulse.timeStamp-delta.timeStamp)
				delta = pulse

			#for debugging - KCM
			if printDeltas:
				temp = []
				for p in pulse_deltas:
					temp.append(str(p))
				print temp

			#save the deltas for some later operation
			save_deltas = deepcopy(pulse_deltas)

			#creating the averages array
			averages = []
			save_x = 0
			
			for i in range(len(chirp.deltas)-1):
				averages.append([]) #create an array for every chirp
				save_x += 1
				
			chirp_deltas = deepcopy(chirp.deltas)
			new_chirp_deltas = []
			new_chirp_deltas.append(chirp_deltas.pop(0))
			chirp_deltas.pop()

			x = 0

			for delta in chirp_deltas:
				new_chirp_deltas.append(delta+new_chirp_deltas[x])
				x+=1

			save_new_chirp_deltas = deepcopy(new_chirp_deltas)

			for pulse_delta in pulse_deltas:
				quality = []
				
				for i in range(len(chirp.deltas)-1):
					quality.append(abs(chirp.deltas[i]-float(pulse_delta)))
				
				averages[quality.index(min(quality))].append(min(quality))


			
			#if ((int(chirp.value)==15) and (len(chirp.deltas)==4)):
			#	print "START DEBUG"
			#	print chirp
			#	print " "
			#	for d in chirp.deltas:
			#		print d
			#	print " "
			#	for p in save_pulses:
			#		print p
			#	print " "
			#	for d in save_deltas:
			#		print d
			#	print " "
			#	for d in save_new_chirp_deltas:
			#		print d
			#	print " "
			#	print save_x
			#	print " "
			#	print averages
			#	print "END DEBUG"
			#	print " "

			save_averages = deepcopy(averages)
			
			for i in range(len(averages)):
				
				try:
					averages[i] = min(averages[i])
				except:
					averages[i] = None

			#for debug
			if printAverages:
				print chirp, averages


			for i in range(len(averages)):
				if (averages[i]>(timeBase/jitterFactor)):
					averages[i] = None

			save_averages = deepcopy(averages)	
			
			n = averages.count(None) #count the number of averages missing

			if (n < 1): #if we've got all pulses to a certain extent

				#if (n!=0):
				#	averages.pop(averages.index(None))

				average = sum(averages)/len(averages)

				if (lastChirpAverage != None):
					if(average<lastChirpAverage):
						if(len(chirp.deltas)>=len(lastChirpDecoded.deltas)):
							#if(n<lastNumMissing):
							lastChirpAverage = average
							lastChirpDecoded = chirp
							lastPulsesDecoded = save_pulses
							lastAverages = save_averages
							lastNumMissing = n
							lastInitialPulse = saveP
				else:
					lastChirpAverage = average
					lastChirpDecoded = chirp
					lastPulsesDecoded = save_pulses
					lastAverages = save_averages
					lastNumMissing = n
					lastInitialPulse = saveP

			if printTiming:
				print "This chirp(",chirpNum,") : ",now()-chirpTime
				chirpNum+=1


					
		#once we're done with all of the chirps
		if (lastChirpDecoded!=None): #if we've got decoded chirps
			
			self.lastChirpAverage = lastChirpAverage
			self.lastAverages = lastAverages
			sliceTime = now()
			removed = False
			
			#for all of the pulses decoded
			#for pulse in lastPulsesDecoded:
			#	trash.insertP(pulses.pop(0))
			#	result = pulses.pop(0)
			trash = UPQueue()
			for p in pulses[0:len(lastPulsesDecoded)]:
				trash.insertP(p)
				
			swap = UPQueue()
			for p in pulses[len(lastPulsesDecoded):]:
				swap.insertP(p)

			pulses = swap

			
				#if (result!=True):
				#	print "Ahhh"
			if printTiming:
				print "Slice Time: ", now()-sliceTime
			if printTiming:
				print "Total Recursion time: ", now()-timer

			lastChirpDecoded.pulses = lastPulsesDecoded #saving the actual pulses for the chirp
			lastChirpDecoded.timeStamp = lastPulsesDecoded[0].timeStamp #saving the timestamp for the chirp
			
			return [lastChirpDecoded,pulses,trash]
		else:
			try:
				if(pulses.pop(0)):
					#print "Ahhhhhhh2!"
					#print "Moving On!"
					if printTiming:
						print "This Instance: ",now()-instanceTime
					return self.decode(pulses,trash,jitter,timer=timer)

			except IndexError:
				return None

if __name__ == '__main__':
    import unittest

    class NonLinearChirpDecoderTests(unittest.TestCase):
        def setup(self):
		"""This function sets up common variables for the following tests"""
		sim = NonLinearSimulator.NonLinearSimulator()   #get a simulator instance and populate it
		sim.addChirps(file='nlchirps.xml')
		sim.addFrames(file='frames.xml')
		sim.addSubFrames(file='subframes.xml')
		self.sim = sim
		
		cd = NonLinearChirpDecoder() #get a chirp decode instance and populate it
		cd.addChirps(file='nlchirps.xml')
		self.cd = cd

        def testSetup(self):
            self.setup()
	    
	def loadXml(self):
		from Ft.Xml import Parse
		
		xmlFile = file('nlchirps.xml','r') #load the chirps
		doc = Parse(xmlFile)
		chirpTags = doc.xpath('//Chirp')
		self.chirps = []
		for c in chirpTags:
			self.chirps.append(Chirp.Chirp(xml=c))
	    

        
		xmlFile = file('frames.xml','r') #load the frames
		doc = Parse(xmlFile)
		frameTags = doc.xpath('//Frame')
		self.frames = []
		for frameTag in frameTags:
			self.frames.append(Frame.Frame(xml=frameTag))

		
        
		xmlFile = file('subframes.xml','r') #load the subFrames
		doc = Parse(xmlFile)
		subFrameTags = doc.xpath('//SubFrame')
		self.subFrames = []
		for subFrameTag in subFrameTags:
			self.subFrames.append(SubFrame.SubFrame(xml=subFrameTag))

	def testLoadXml(self):
		self.loadXml()

        def testInst(self):
            t = NonLinearChirpDecoder()
	    
	
	def testAllChirps(self):
		self.setup()
		self.loadXml()
		t = mx.DateTime.now()
		pulses = self.sim.make(self.chirps,t)[0]
		t += mx.DateTime.DateTimeDeltaFrom(100000000000)
		pulses.append(Pulse.Pulse(timeStamp=t))
		decodedChirps = []
		trash = []

		f = file('testPulses.xml','w')
		from Ft.Xml import MarkupWriter
		writer = MarkupWriter(f)
		writer.startDocument()
		writer.startElement(u'Pulses')
		for p in pulses:
			p.writeToXml(writer)
		writer.endElement(u'Pulses')
		writer.endDocument()
		f.close()
		
		while(1):
			try:
				[dC,pulses,trash] = self.cd.decode(pulses,trash,100,debug=False)
				if dC!=None:
					decodedChirps.append(dC)
				else:
					break
			except ValueError, e:
				print "!", e
				break

		#for i in range(len(decodedChirps)):
		#	print decodedChirps[i], self.chirps[i], decodedChirps[i].__eq__(self.chirps[i],debug=True)

		print len(decodedChirps)
		print len(self.chirps)

		self.failUnlessEqual(decodedChirps,self.chirps)

	def testFrameSequence(self):
		self.setup()
		
		frameList = self.sim.frames #get the frames from the simulator
		for frame in frameList.frames: #for all of the frames
			t = mx.DateTime.now() #now 
			simulatedChirps = frame.sim() #turn a frame into a list of chirps
			pulses,t = self.sim.make(simulatedChirps,t) #generate pulses for the frame from now
			t += mx.DateTime.DateTimeDeltaFrom(10) #endcap
			pulses.append(Pulse.Pulse(t)) #append the endcap

			trash = [] #init the trash
			decodedChirps = [] #init the decoded chirps
			
			#decode until done
		while(1):
			try:
				[decodedChirp,pulses,trash] = self.cd.decode(pulses,trash,100,debug=False) #decode
				if decodedChirp!=None: #if we've got a chirp
					decodedChirps.append(decodedChirp) #save it
				else:
					break #break if not
			except ValueError:
				break #break on error

		if len(simulatedChirps)!=len(decodedChirps): #if the lengths don't match, don't bother checking the chirps
			self.fail()
			
		for cc in range(len(decodedChirps)):
			if simulatedChirps[cc]!=decodedChirps[cc]:
				self.fail()			

    unittest.main()
