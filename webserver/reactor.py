from threading import Thread

from twisted.web import resource, static, server, twcgi
from twisted.internet import reactor
from Queue import Queue
import synccmd

msg_queue = Queue()
in_queue = Queue()

#parent = None
#def send_command(cmd, args):
#    callID = synccmd.getCallID()
#    if parent is not None:
#        evt = synccmd.SyncCallbackCommandEvent(id = callID, cmd = cmd, args = args)
#        parent.AddPendingEvent(evt)
#        
#        # now wait for a response (5 secs)
#        synccmd.waitForResponse(in_queue, 5000)

def report(msg):
    msg_queue.put(msg)
        

class series_http_handler(resource.Resource):
    def __init__(self):
        self.tel = 0

    def render_GET(self, request):
        if not request.args:
            # HIER MOET IK:
            # - De GUI vertellen dat ie data moet gaan verzamelen
            # - Op een of andere manier moet wachten op die data
            # - Als het er is, aan twisted terug geven zodat ik die op het scherm kan tonen
            pass
        
        else:
            if "id" in request.args:
                id = request.args["id"][0]
                request.write("Series ID: %s" % id)
   
        self.tel = self.tel + 1
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
        
        root.putChild("series", series_http_handler())
        
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
        