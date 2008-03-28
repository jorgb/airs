#!/usr/bin/python

# work around for wxPython since our sys.path[0] is adjusted after
# importing wx and using wxversion to determine the proper wxWidgets version
import sys
if sys.path:
    execpath = sys.path[0]
    # make sure when py2exe compiled this, that our path is a valid one on disk
    if execpath.endswith('library.zip'): 
        execpath = os.path.split(execpath)[0]     
else:
    sys.stderr.write("Error: Cannot find execution path for Airs\n")
    sys.exit(1)

# continue with application initialisation
import gui.airsApp as app
from data import appcfg

appcfg.appdir = execpath

airs = app.AirsApp(0)
airs.MainLoop()
