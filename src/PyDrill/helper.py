import datetime

class smart_datetime(datetime.datetime):
    def __float__(self):
        return float(self.hour*60*60) + float(self.minute*60) + float(self.second) + float(self.microsecond/1000000.0)

class smart_timedelta(datetime.timedelta):
    def __float__(self):
        return float(self.seconds) + float(self.microseconds/1000000.0)

if __name__ == '__main__':
    import unittest

    class SmartTimeDeltaTestCase(unittest.TestCase):
        def setUp(self):
            self.timedelta = timedelta(0,1.5)

        def testFloat(self):
            self.failUnlessEqual(float(self.timedelta),1.5)
    
    class SmartDateTimeTestCase(unittest.TestCase):
        def setUp(self):
            self.datetime = datetime.now()

        def testFloat(self):
            float(self.datetime)

    unittest.main()
