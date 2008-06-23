import sys
sys.path.append("/Teledrill/Libraries/Python")

import SimpleXMLRPCServer
import xmlrpclib

from SimpleXMLRPCServer import *

from Ft.Xml import Parse
from Objects import *
import XMLUtils
from DataStructures import *
import Globals
import mx.DateTime
import mx
from mx.DateTime import *

#ALL CLASS Functions MUST RETURN AN XML-RPC TYPE (THEY CANNOT RETURN NONE)


class PyDrillServer:
    
    def __init__(self,configFile=None):

        print 'Init!'

        #self.parseConfig(configFile)


    def parseConfig(self,configFile):
	
	if(configFile):

            try:
                doc = Parse(configFile)
                
            except Exception, e:
                print e
                raise FileIOError('Config file DNE or could not be parsed!')

            self.config = {}
            
            for child in doc.firstChild.childNodes: #for all of the children of the parent node
                if (child.nodeName!='#text'): #take only the first level
                    self.config[child.nodeName] = child.firstChild.nodeValue
                    
        

                
        
class PyDrillDecoderServer: #this thing will probably get complicated
    def __init__(self,log=False,chirpFile=None,**kw):
        pass

    def alive(self):
        return True

    def exit(self):
        sys.exit()

class PyDrillSimpleXMLRPCServer(SimpleXMLRPCServer):
    def serve_forever(self):
        self.quit = 0
        while not self.quit:

            self.handle_request()
            
                
class PyDrillXMLRPCServer:
	def __init__(self,host,server_messages=True,configFile='config.xml',**kw):

            
            #self.configFile = configFile

            #self.readConfigFile()

            self.server_messages = server_messages
            
            host = 'localhost'
            self.host = host
            self.port = 8055
            if self.server_messages:
                print "Attempting to start the PyDrill XML RPC Server on host: " , host , ':' , self.port
		
            self.server = PyDrillSimpleXMLRPCServer((host,self.port),logRequests=True)
            
            if self.server_messages:	
                print 'Server started Successfuly'

            self.server.register_instance(PyDrillDecoderServer(log=True,**kw))
            self.server.register_function(self.kill)

        def kill(self):
                self.server.quit = 1
                return 1

        def readConfigFile(self):
            doc = Parse(self.configFile)
            for node in doc.firstChild.childNodes:
                if (node.nodeName=='Port'):
                    self.port = int(node.firstChild.nodeValue)
	
        def start(self):
            
            #self.server.register_instance(PyDrillDecoderServer(log=True,**kw))
            #self.server.register_function(self.kill)
            #self.server.register_introspection_functions()
            self.server.serve_forever()

        def kill(self):
            self.server.quit = 1
            return 1
            
        def stop(self):
            print "Stopping Server"
            self.server.quit = 1
            

                
class PyDrillXMLRPCClient:
    def __init__(self,host,port=None,client_messages=True,configFile=None):
        """A simple XML-RPC client to provide a higher level interface to the PyDrill simple XML-RPC server"""
        self.client_messages = client_messages
    
        
        if port:
            self.port = port

        #if configFile:
        #    self.configFile = configFile
        #    try:
        #        self.readConfigFile()
        #    except Exception, e:
        #        print e

        if self.client_messages:
            print "Attempting to start client connection to host: " , host, " port: ", self.port

        self.server = xmlrpclib.Server(('http://' + str(host) + ':' + str(self.port)))

        if self.client_messages:
            print "Connection to server successful"

    def ServerAlive(self):
        
        return self.server.alive()

