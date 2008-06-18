from persistent import Persistent
from PyDrill.Objects.PyDrillObject import PyDrillObject

class Bar(Persistent,PyDrillObject):
    def __init__(self,peak,wide=False):
        self.peak,self.wide = peak,wide
        self.fileKey = 'modulus'

    def __eq__(self,other):
        if not isinstance(other,Symbol):
            return NotImplemented

        return self.peak == other.peak and self.wide == other.wide

    def __copy__(self):
        return Symbol(self.peak,wide=self.wide)

    
    
