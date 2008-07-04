import os
import subprocess
import libxml2
import libxslt
import platform

import synccmd
from data import viewmgr
from data import series_list
from data import appcfg
from data import db_conv_xml
from data import db


class WebDispatchError(Exception):
    pass


def _getXSLTpath(xslt_file):
    """ Returns path to XSLT dir """
    return os.path.join(appcfg.appdir, "xslt", xslt_file)


def seriesIndex(cmd, args):
    xml = db_conv_xml.get_series_xml()
    
    try:
        styleDoc = libxml2.parseFile(_getXSLTpath("series.xsl"))
    except libxml2.parserError, msg:
        raise WebDispatchError, "Parser error occured: %s" % str(msg)
    
    style = libxslt.parseStylesheetDoc(styleDoc)

    result = style.applyStylesheet(xml, None)
    cmd.html = style.saveResultToString(result)
    

def episodeList(cmd, args):
    xml = db_conv_xml.get_episode_list(args["id"])

    # DEBUG ONLY!
    #f = open("/home/jorg/personal/src/airs/xslt/test/episodes.xml", "wt")
    #xml.dump(f)
    #f.close()
    
    try:
        styleDoc = libxml2.parseFile(_getXSLTpath("episodelist.xsl"))
    except libxml2.parserError, msg:
        raise WebDispatchError, "Parser error occured: %s" % str(msg)
        
    style = libxslt.parseStylesheetDoc(styleDoc)

    result = style.applyStylesheet(xml, None)
    cmd.html = style.saveResultToString(result)
      

def markSeen(cmd, args):

    episode = db.store.find(series_list.Episode, series_list.Episode.id == args["id"]).one()
    if episode:
        episode.status = series_list.EP_SEEN
        db.store.commit()
    
        # redirect to episode list
        #args["id"] = episode.series_id
        #return episodeList(cmd, args)
        
        cmd.redirect = "http://127.0.0.1:8000/series?cmd_get_series=%i" % episode.series_id
        cmd.html = ''
        

def playFile(cmd, args):
        
    argstr = list()
    for arg in appcfg.options[appcfg.CFG_PLAYER_ARGS].split():
        argstr.append(arg.replace("%file%", args["file"]))
    argstr.insert(0, appcfg.options[appcfg.CFG_PLAYER_PATH])
    
    try:
        subprocess.Popen( argstr )
    except OSError:
        cmd.html = "<h1>Can't play file</h1></br>" + args["file"]
        return

    cmd.redirect = "http://127.0.0.1:8000/series?cmd_get_series=%i" % args["id"]
    cmd.html = ""
 
        
def archiveFile(cmd, args):
        
    thefile = args["file"]
    head, tail = os.path.split(thefile)
    
    head += appcfg.AIRS_ARCHIVED_PATH
    if not os.path.exists(head):
        try:
            os.makedirs(head)
        except OSError:
            cmd.html = "<h1>Error creating archive directory</h1></br>" + head
            return
    
    dstfile = os.path.join(head, tail)
    try:
        os.rename(thefile, dstfile) 
    except OSError:
        cmd.html = "<h1>Error archiving file</h1></br>" + thefile
        return
        
    cmd.redirect = "http://127.0.0.1:8000/series?cmd_get_series=%i" % args["id"]
    cmd.html = ""
 
#------------------------------------------------------------------------------
_cmd_dispatcher = { "get_index": seriesIndex,
                    "get_episodes": episodeList,
                    "mark_seen": markSeen,
                    "play_file": playFile,
                    "archive_file": archiveFile }

def execute(cmd, id, args):
    cb = synccmd.SyncCommand(id)
            
    if cmd in _cmd_dispatcher:
        try:
            _cmd_dispatcher[cmd](cb, args)
        except WebDispatchError, msg:
            viewmgr.app_log("Internal error occured: %s" % str(msg))
            cb.html = "<h1>Internal Error Occured</h1><br>%s" % str(msg)
    else:
        cb.html = "<h1>Command Unknown</h1><br>The command '%s' is unknown" % str(cmd)
        
    synccmd.get().putCmd(cb)

