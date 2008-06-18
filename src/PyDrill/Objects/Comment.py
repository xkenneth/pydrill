from persistent import Persistent

class Comment(Persistent):
    def __init__(self,comment,timeStamp=None):
        self.comment = comment
        self.timeStamp = timeStamp
        self.fileKey = 'comment'

    def __copy__(self):
        return Comment(self.comment,timeStamp=self.timeStamp)

    def __eq__(self,other):
        if not isinstance(other,Comment): #check to make sure it's one of us
            return NotImplemented
        
        return self.comment == other.comment and self.timeStamp == other.timeStamp

    def __ne__(self,other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result


if __name__ == "__main__":

    import unittest,mx.DateTime
    from PyDrill import Debug,Globals
    from copy import copy
    

    class CommentTests(unittest.TestCase):
        def setup(self):
            self.comment1 = Comment('This is a comment!',mx.DateTime.now())

        def testEQ(self):
            self.setup()
            self.failUnlessEqual(self.comment1,self.comment1)
            self.failIfEqual(self.comment1,10)
            

        def testCP(self):
            self.setup()
            self.failUnlessEqual(self.comment1,copy(self.comment1))

        def testPersistence(self):
            self.setup()
            Debug.writeToFS()
            if Debug.readFromFS()!=None:
                self.fail()
            
            Debug.writeToFS(self.comment1)
            self.failUnlessEqual(Debug.readFromFS(),self.comment1)
                

    unittest.main()
