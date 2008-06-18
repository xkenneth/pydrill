from PyDrill.Decoders import Decoder
from PyDrill.Objects.ToolData import ToolData
class InclinationDecoder(Decoder.Decoder):

	def __init__(self,**kw):
		try:
			self.initialized
		except AttributeError:
			Decoder.Decoder.__init__(self,**kw)

		self.last_pulse = None
		self.delta = 2.0
		self.jitter = 0.1
		self.count = 0
		self.initialized = True
		self.timeStamp = None
	def decode(self,pulse):
		
		if self.last_pulse is None:
			self.last_pulse = pulse
			self.count += 1
			self.timeStamp = pulse.timeStamp
			return

		diff = pulse.timeStamp - self.last_pulse.timeStamp

		if (diff>(self.delta-self.jitter)) and (diff<(self.delta+self.jitter)):
			self.count += 1
			self.last_pulse = pulse
			
		else:
			tool_data = ToolData('inclinationcount',value=self.count,timeStamp=self.timeStamp)
			#reset
			self.__init__()
			return tool_data
			

				
if __name__ == '__main__':
	import unittest
	from PyDrill.Objects.Pulse import Pulse
	import mx.DateTime

	class InclinationDecoderTests(unittest.TestCase):
		def setUp(self):
			self.decoder = InclinationDecoder()

		def tearDown(self):
			pass

		def testCount(self):
			
			for i in range(20):

				pulses = []
				t = mx.DateTime.now()
				for j in range(i+5):
					pulses.append(Pulse(timeStamp=t))
					t += mx.DateTime.DateTimeDeltaFrom(2.0)

				t += mx.DateTime.DateTimeDeltaFrom(3.0)
				pulses.append(Pulse(timeStamp=t))
				
				data = None

				for p in pulses:
					data = self.decoder.decode(p)
					if data is not None:
						self.failUnlessEqual(data.value,i+5)

				if data is None:
					self.fail()
					


			t = InclinationDecoder()

	unittest.main()

		
