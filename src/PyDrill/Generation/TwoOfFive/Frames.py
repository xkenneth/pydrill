#frame defitions
#frameNumber = {'data':length]
from PyDrill.Objects.Block import Block
from PyDrill.Objects.SymbolFrame import SymbolFrame
from copy import copy
import Symbols

frame0 = ['toolstatus','toolstatus']
frame1 = ['azimuth','azimuth']
frame2 = ['inclination','inclination']
frame3 = ['gz','gz','gz']
frame4 = ['hz','hz','hz']
frame5 = ['gx','gx','gx','gy','gy','gy']
frame6 = ['hx','hx','hx','hy','hy','hy']
frame7 = ['temperature','temperature']
frame8 = ['pressure','pressure']
frame9 = ['toolface','toolface']
frame10 = ['gammaray','gammaray']
frame11 = ['gx','gx','gy','gy']
frame12 = ['hx','hx','hy','hy']
frame13 = ['toolface']
frame14 = ['gammaray']
frame15 = ['toolface','gammaray']

badFrame1 = ['baddata']
badFrame2 = ['baddata1','baddata2']

frames = [frame0,frame1,frame2,frame3,frame4,frame5,frame6,frame7,frame8,frame9,frame10,frame11,frame12,frame13,frame14,frame15] #frames take their ID from the order they're placed in here!!!
badFrames = [badFrame1,badFrame2]



def generate():
    frameObjects = [] #for holding the frame objects
    symbol_objects = Symbols.generateSymbols()
    
    id = 0
    for frame in frames: #for all of the frames
        lastData = None
        newData = []
        save_id = None
        for symbol in symbol_objects:
            if symbol.value == id:
                save_id = symbol
                break

        for data in frame: #for the data in each frame
            
            if lastData!=None: 
                if lastData.name == data:
                    lastData.symbolLength += 1
                else:
                    newData.append(lastData)
                    lastData = Block(name=data,symbolLength=1)
            else:
                lastData = Block(name=data,symbolLength=1)
                
        newData.append(lastData)
        
        frameObjects.append(SymbolFrame(identifier=save_id,blocks=newData))

        id += 1

    return frameObjects

def generateErrors():
    frameObjects = [] #for holding the frame objects
    id = 0
    for frame in badFrames: #for all of the frames
        lastData = None
        newData = []
        for data in frame: #for the data in each frame
            
            if lastData!=None: 
                if lastData.name == data:
                    lastData.symbolLength += 1
                else:
                    newData.append(lastData)
                    lastData = Block(name=data,symbolLength=1)
            else:
                lastData = Block(name=data,symbolLength=1)
                
        newData.append(lastData)

        frameObjects.append(Frame(header=id+63,subFrames=newData))

        id += 1

    return frameObjects

def write(frames,path='./',fileName='frames.xml'):
    import os

    path = os.path.join(path,fileName)
    
    if not os.path.isdir(os.path.dirname(path)):
        raise IOError('Path is not valid')

    f = file(path,'w')

    from Ft.Xml import MarkupWriter
    
    writer = MarkupWriter(f,indent=u'yes')
    writer.startDocument()
    writer.xmlFragment('<?xml-stylesheet type="text/xsl" href="teledrill.xsl"?>\n')
    
    writer.startElement(u'Frames')

    for fO in frameObjects:
        fO.writeToXml(writer)

    writer.endElement(u'Frames')
    writer.endDocument()

    f.close()
    
    return path

if __name__ == '__main__':
    

    write(generate())
        
    


                                  
                
                    
            
            
            
        
    #generate and save the frame defitions
