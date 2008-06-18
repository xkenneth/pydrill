from persistent import Persistent
import persistent.list
from PyDrill.Objects.PyDrillObject import PyDrillObject
from PyDrill.Objects.ToolData import ToolData

class SymbolFrame(Persistent,PyDrillObject):
    def __init__(self,
                 identifier=None,
                 blocks=None,
                 symbols=None,
                 ):
        """Initialize a frame
        identifier - a symbol that acts as an identifier for the frame
        blocks - the individual data blocks
        """
        self.identifier = identifier
        
        self.set_blocks(blocks)
        self.set_symbols(symbols)
        
        self.fileKey = 'frame'

    #getters and setters - for those that need it

    def set_blocks(self,blocks):
        """To set the blocks"""
        self._blocks = persistent.list.PersistentList()
        if blocks is not None:
            for block in blocks:
                self._blocks.append(block)

    def get_blocks(self):
        return self._blocks

    def set_symbols(self,symbols):
        """Used to make sure the symbols are of the right type of list"""
        self._symbols = persistent.list.PersistentList()

        if symbols is not None:
            for symbol in symbols:
                self._symbols.append(symbol)
                
    def get_symbols(self):
        return self._symbols

    blocks = property(get_blocks,get_symbols)
    symbols = property(get_symbols,set_symbols)
    
        
    def __copy__(self):
        """Returns a fresh copy of the object"""
        return SymbolFrame(identifier=self.identifier,
                           blocks=self.blocks,
                           symbols=self.symbols,
                           )
                           

    def sim(self):
        """Decompose a frame into it's smaller elements"""
        
        data = [self.identifier]
        #for all the blocks
        for block in self.blocks:
            data.extend(block.sim())

        return data

    def decompose(self):
        """Decompose a completed frame into tooldata"""
        data = {}

        count = 0
        for block in self.blocks:
            for i in range(len(block)):
                try:
                    #data[block.name] = ( data[block.name] * 100 ) + self.symbols[count].value
                    data[block.name].value = ( data[block.name].value * 100 ) + self.symbols[count].value
                except KeyError:
                    data[block.name] = ToolData(block.name,value=self.symbols[count].value,timeStamp=self.symbols[count].timeStamp)
                count += 1

        #print data

        tool_data = []

        for d in data:
            tool_data.append(data[d])

        return tool_data

    def __eq__(self,other):
        if not isinstance(other,SymbolFrame):
            return NotImplemented
        
        if self.identifier != other.identifier:
            return False

        if len(self.blocks) != len(other.blocks):
            return False
        
        for i in range(len(self.blocks)):
            if self.blocks[i] != other.blocks[i]:
                return False

        return True

    def __len__(self):
        """Return the length of the frame in symbols"""
        count = 1
        for block in self.blocks:
            count += len(block)

        return count

if __name__ == '__main__':
    from PyDrill.Objects.Symbol import Symbol
    from PyDrill.Generation.TwoOfFive import Symbols,Frames
    from copy import copy

    import unittest
    
    class SymbolFrameTestCases(unittest.TestCase):
        def setUp(self):
            self.symbols = Symbols.generateSymbols()
            self.identifiers = Symbols.generateIdentifiers()
            self.frames = Frames.generate()
            
        def tearDown(self):
            pass
        
        def testEQ(self):
            for frame in self.frames:
                self.failIfEqual(frame,None)
                self.failIfEqual(frame,1)
                self.failUnlessEqual(frame,frame)

        def testLen(self):
            for frame in self.frames:
                len(frame)
            #self.failIfEqual(None
        
        def testCP(self):
            for frame in self.frames:
                self.failUnlessEqual(frame,copy(frame))
        

    unittest.main()
