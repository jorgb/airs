import os
import libxml2
import libxslt

import synccmd
from data import viewmgr
from data import series_list
from data import appcfg
from data import db_conv_xml


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
    
    try:
        styleDoc = libxml2.parseFile(_getXSLTpath("episodelist.xsl"))
    except libxml2.parserError, msg:
        raise WebDispatchError, "Parser error occured: %s" % str(msg)
    
    style = libxslt.parseStylesheetDoc(styleDoc)

    result = style.applyStylesheet(xml, None)
    cmd.html = style.saveResultToString(result)
      
    
#------------------------------------------------------------------------------
_cmd_dispatcher = { "get_index": seriesIndex,
                    "get_episodes": episodeList }

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

