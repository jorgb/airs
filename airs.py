#!/usr/bin/python
#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

# work around for wxPython since our sys.path[0] is adjusted after
# importing wx and using wxversion to determine the proper wxWidgets version
import sys, os
from data import argparse

if sys.path:
    execpath = sys.path[0]
    # make sure when py2exe compiled this, that our path is a valid one on disk
    if execpath.endswith('library.zip'): 
        execpath = os.path.split(execpath)[0]     
else:
    sys.stderr.write("Error: Cannot find execution path for Airs\n")
    sys.exit(1)

options = argparse.argparse()
        
# continue with application initialisation
import gui.airsApp as app
from data import appcfg

appcfg.appdir = execpath
if options.dbpath is not None:
    appcfg.dbpath = options.dbpath

airs = app.AirsApp(0)
airs.MainLoop()
