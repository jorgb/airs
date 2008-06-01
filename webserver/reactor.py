#!/usr/bin/python
from threading import Thread

from twisted.web import resource, static, server, twcgi
from twisted.internet import reactor
from Queue import Queue

msg_queue = Queue()

def report(msg):
    msg_queue.put(msg)
        
class series_sel(resource.Resource):
    def __init__(self):
        self.tel = 0

    def render_GET(self, request):
        report("Received: %s" % request)
        self.tel = self.tel + 1
        request.write("hee. tel: " + str(self.tel))
        return ""
    
    
class WebServerThread(Thread):
    def __init__(self):
        Thread.__init__(self)        
        self.running = False
        
    def stop(self):
        if self.running:
            reactor.stop()
        
    def run(self):
        report("Starting up web server thread ...")
        root = resource.Resource()

        #root = static.File("c:\www")
        #root.indexNames=['index.html','index.htm']        
        
        root.putChild("series_sel", series_sel())
        
        port = 8000
        succes = False
        report("Binding to 127.0.0.1:%i ..." % port)

        try:
            reactor.listenTCP(port, server.Site(root))
            succes = True
        except Exception, e:
            report("ERROR: Could not start listening!\nWebserver is stopped.")
            
        if succes:
            self.running = True
            reactor.run(installSignalHandlers=0)
            self.running = False
            
        report("Stopping web server thread")
        