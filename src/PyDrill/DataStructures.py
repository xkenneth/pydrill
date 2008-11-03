import Globals

from objects import pulse

from Generics import *

from helper import smart_datetime as datetime
from helper import smart_timedelta as timedelta


class FrameList(list):
    
    def __getitem__(self,key):
        for frame in self:
            
            try:
                if (val(frame.header)==key):
                    return frame
            except AttributeError:
                if frame.header==key:
                    return frame

        raise IndexError('Frame does not exist!',key)

class ChirpList(list):

    def indexChirp(self,length,value):
        length = int(length)
        value = int(value)

        for i in range(self.__len__()):
            
            #print len(self.__getitem__(i)),val(self.__getitem__(i))
            if ((len(self.__getitem__(i))==length)
                and
                (val(self.__getitem__(i))==value)):
                return self.__getitem__(i)            
            
        raise IndexError('Chirp does not exist!')
