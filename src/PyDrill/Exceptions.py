import pdb

class PyDrillException(Exception):
    """A basic PyDrill Exception."""
    def __init__(self,data=None):
        self.message = self.__doc__
        self.data = data

    def __str__(self):
        return str(self.message) + ' ' + str(self.data)

        
    
