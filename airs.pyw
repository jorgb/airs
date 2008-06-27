#!/usr/bin/python

# work around for wxPython since our sys.path[0] is adjusted after
# importing wx and using wxversion to determine the proper wxWidgets version
import sys, os.path
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
import traceback, wx
from data import appcfg

appcfg.appdir = execpath
if options.dbpath is not None:
    appcfg.dbpath = options.dbpath

def excepthook(type, value, trace):
    if wx and sys and traceback:
        exc = traceback.format_exception(type, value, trace)
        for e in exc: wx.LogError(e)
        wx.LogError('Unhandled Error: %s: %s'%(str(type), str(value)))
        sys.__excepthook__(type, value, trace)

sys.excepthook = excepthook
airs = app.AirsApp(redirect = True)
airs.MainLoop()
