from Ft.Xml import Parse, MarkupWriter
from Ft.Xml.Domlette import NonvalidatingReader, EntityReader
from Ft.Lib import Uri
import Ft
import copy
from copy import deepcopy
import cStringIO

def StringToFileLike(string):
	"""Create a file-like "memory file buffer" from a string"""
	return cStringIO.StringIO(string)

def xmlStr(pyDrillObject):
	"""Returns the XML String representation of a PyDrill Object"""
	buffer = cStringIO.StringIO()
	writer = MarkupWriter(buffer,indent=u'yes')
	writer.startDocument()
	try:
		pyDrillObject.writeToXml(writer)
		
	except AttributeError, e:
		print e
		raise TypeError()

	writer.endDocument()

	this = str(buffer.getvalue())
	return this

def xmls(object):
	return xmlStr(object)

	
