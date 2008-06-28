from threading import Thread
import os

from twisted.web import resource, static, server, twcgi
from twisted.internet import reactor
from Queue import Queue
import synccmd

from data import appcfg

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
        pass
        
    def render_GET(self, request):
        if not request.args:
            cmd = send_command("get_index", args = {})
            request.write(cmd.html)
        
        elif "cmd_get_series" in request.args:
            id = int(request.args["cmd_get_series"][0])
            cmd = send_command("get_episodes", args={"id": id})   
            request.write(cmd.html)
            
        elif "cmd_mark_seen" in request.args:
            id = int(request.args["cmd_mark_seen"][0])
            cmd = send_command("mark_seen", args={"id": id})
            request.write(cmd.html)
                        
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

        webdir = os.path.join(appcfg.appdir, "www")
        
        root.putChild("series", series_http_handler())
        root.putChild("www", static.File(webdir))
        
        port = 8000
        succes = False
        report("Webserver bound to port %i ..." % port)
        report("Web public directory is at '%s'" % webdir) 

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
        