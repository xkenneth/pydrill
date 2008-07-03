import math
from PyDrill.Objects.Symbol import Symbol
from PyDrill.Objects.Bar import Bar
from Ft.Xml import MarkupWriter


narrow = .5
wide = 1.0

#defining the integer symbols
symbol0 = ['n','n','w','w','n']
symbol1 = ['w','n','n','n','w']
symbol2 = ['n','w','n','n','w']
symbol3 = ['w','w','n','n','n']
symbol4 = ['n','n','w','n','w']
symbol5 = ['w','n','w','n','n']
symbol6 = ['n','w','w','n','n']
symbol7 = ['n','n','n','w','w']
symbol8 = ['w','n','n','w','n']
symbol9 = ['n','w','n','w','n']

#appending the integer symbols
symbols = [symbol0,symbol1,symbol2,symbol3,symbol4,symbol5,symbol6,symbol7,symbol8,symbol9]

#special symbols
frameIdentifier1 = Symbol(value=-1,bars=[
        Bar(False),
        Bar(False),
        Bar(True),
        Bar(False),
        Bar(False),
        Bar(False),
        Bar(False),
        Bar(True),
        Bar(False),
        Bar(True),
        Bar(False),
        Bar(True),
        Bar(False),
        Bar(False),
        Bar(False),
        Bar(False)])

#frameIdentifier2 = Symbol(value=-2,bars=[Bar(False),Bar(False),Bar(True),Bar(False),Bar(True),Bar(False),Bar(True),Bar(False),Bar(False),Bar(False),Bar(False),Bar(False)])
#frameIdentifier3 = Symbol(value=-3,bars=[Bar(False),Bar(False),Bar(True),Bar(False),Bar(True),Bar(False),Bar(True),Bar(False),Bar(False),Bar(False),Bar(False),Bar(False),Bar(False)])
identifiers = [frameIdentifier1]

def generateIdentifiers():
    return identifiers

def generateSymbols():
    
    newSymbols = []

    for i in range(100): #for all of the possible symbols
        #print int(math.floor(i/10)),i % 10
        
        peaks = symbols[int(math.floor(i/10))]
        valleys = symbols[i % 10]
        
        bars = []
        for j in range(len(peaks)):
            wide = False
            if peaks[j] == 'w':
                wide = True
            bars.append(Bar(True,wide=wide))
            wide = False
            if valleys[j] == 'w':
                wide = True
            bars.append(Bar(False,wide=wide))

        
        newSymbols.append(Symbol(value=i,bars=bars))

    return newSymbols
    
    

def write(chirps,path='./',fileName='symbols.xml'):
    import os

    path = os.path.join(path,fileName)
    
    if not os.path.isdir(os.path.dirname(path)):
        raise IOError('Path is not valid')
    
    
        
    myFile = file(path,'w')
    writer = MarkupWriter(myFile,indent=u'yes')
    writer.startDocument()
    writer.xmlFragment('<?xml-stylesheet type="text/xsl" href="teledrill.xsl"?>\n')
    writer.startElement(u'Symbols')
    
    for c in chirps:
        
        c.writeToXml(writer)
    
    writer.endElement(u'Symbols')
    writer.endDocument()
    myFile.close()

    return path
    

if __name__ == '__main__':
    
    print generateSymbols()
    print generateIdentifiers()

    
    

