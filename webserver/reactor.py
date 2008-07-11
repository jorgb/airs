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
        cmd = synccmd.waitForResponse(callID, 15000)
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
        cmd = None
        if not request.args:
            cmd = send_command("get_index", args = {})

        elif "cmd_get_series" in request.args:
            id = int(request.args["cmd_get_series"][0])
            cmd = send_command("get_episodes", args={"id": id})

        elif "cmd_mark_seen" in request.args:
            id = int(request.args["cmd_mark_seen"][0])
            cmd = send_command("mark_seen", args={"id": id})

        elif "cmd_play_file" in request.args and "return" in request.args:
            thefile = request.args["cmd_play_file"][0]
            return_id = request.args["return"][0]
            cmd = send_command("play_file", args={"id": int(return_id), "file": thefile})

        elif "cmd_archive_file" in request.args and "return" in request.args:
            thefile = request.args["cmd_archive_file"][0]
            return_id = request.args["return"][0]
            cmd = send_command("archive_file", args={"id": int(return_id), "file": thefile})

        elif "cmd_open_airs" in request.args:
            cmd = send_command("show_airs", args={})
                        
        if cmd is not None:
            if cmd.redirect:
                # redirect goes before html display
                request.redirect(cmd.redirect)
            else:
                request.write(cmd.html)
        else:
            request.write("<h1>ERROR, last request did not produce a valid command!</h1>")

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

        succes = False
        port = appcfg.options[appcfg.CFG_WEB_PORT]
        url = appcfg.options[appcfg.CFG_WEB_URL]
        report("Webserver bound to %s:%i ..." % (url, port))
        report("Web public directory is at '%s'" % webdir)

        try:
            reactor.listenTCP(port, server.Site(root), interface=url)
            succes = True
        except Exception, e:
            report("ERROR: Could not start listening!\nWebserver is stopped.")

        if succes:
            self.running = True
            reactor.run(installSignalHandlers=0)
            self.running = False

        report("Stopping web server thread")
