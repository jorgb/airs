from threading import Thread

from twisted.web import resource, static, server, twcgi
from twisted.internet import reactor
from Queue import Queue
import synccmd

msg_queue = Queue()

parent = None
def send_command(s, args):
    """ Sends a command event to the frame and awaits response with the same id """
    cmd = None
    callID = synccmd.getCallID()
    if parent is not None:
        evt = synccmd.SyncCallbackCommandEvent(callid = callID, cmd = s, args = args)
        parent.AddPendingEvent(evt)
        # now wait for a response (5 secs)
        cmd = synccmd.waitForResponse(callID, 3000)
    if cmd is None:
        cmd = synccmd.SyncCommand(-1)
        cmd.html = "<html><h1>Command '%s' has timed out!</h1>" % s + \
                   "Airs did not respond in a timely matter or could not be reached. Please retry again.</html>" 
    return cmd
        

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
            cmd = send_command("get_index", args = {})
            request.write(cmd.html)
        
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
        