def writeToFS(obj=None):
    """Write's an object to a ZODB filesystem"""
    from ZODB import DB, FileStorage
    import transaction
    storage = FileStorage.FileStorage('/tmp/test.fs')
    db = DB(storage)
    conn = db.open()
    root = conn.root()
    if obj!=None:
        root['test'] = obj
    else:
        root['test'] = None
    transaction.commit()
    conn.close()
    db.close()
    storage.close()

def readFromFS():
    """Read's an object from a ZODB filesystem"""
    from ZODB import DB, FileStorage
    from copy import deepcopy
    storage = FileStorage.FileStorage('/tmp/test.fs')
    db = DB(storage)
    conn = db.open()
    root = conn.root()
    this = deepcopy(root['test'])
    conn.close()
    db.close()
    storage.close()
    return this

def writeToXml(obj):
    """Pickles an obj to XML"""
    from Ft.Xml import MarkupWriter
    outputFile = file('/tmp/test.xml','w')
    writer = MarkupWriter(outputFile, indent=u'yes')
    writer.startDocument()
    writer.startElement(u'Test')
    obj.writeToXml(writer)
    writer.endElement(u'Test')
    writer.endDocument()
    outputFile.close()

def readFromXml():
    """Returns an object written to an XML file"""
    from Ft.Xml import Parse
    doc = Parse(file('/tmp/test.xml'))
    return doc.childNodes[0].childNodes[1]


if __name__ == '__main__':
    import unittest
    class FSTests(unittest.TestCase):
        """A unittest.TestCase to test out all of the functionality of the debug module."""
        def testFSClear(self):
            """Make sure that if we write nothing to a ZODB filesystem, that it's actually written"""
            writeToFS()
            temp = readFromFS()
            if temp != None:
                self.fail()

        def testFSWrite(self):
            """Test writing and reading froma  temporary ZODB."""
            obj = 5
            writeToFS(obj)
            temp = readFromFS()
            self.failUnlessEqual(obj, temp)
            
    unittest.main()

