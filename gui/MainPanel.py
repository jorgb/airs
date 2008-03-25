import os.path, wx
import wx.xrc as xrc
from wx.lib.pubsub import Publisher
import appcfg, xmlres, viewmgr

class MainPanel(wx.Panel):

    def __init__(self, parent, id = -1):

        pre = wx.PrePanel()

        res = xmlres.loadGuiResource('MainPanel.xrc')
        res.LoadOnPanel(pre, parent, "ID_MAIN_PANEL")
        self.PostCreate(pre)

        self.SetBackgroundColour(wx.WHITE)
        
        self.log_window = xrc.XRCCTRL(self, "ID_LOG_WINDOW")
        
        Publisher().subscribe(self._onSignalLogMessage, viewmgr.SIGNAL_APP_LOG)


    def _onSignalLogMessage(self, msg):
        """
        Received a message, log it to the window
        """
        
        self.log_window.AppendText(msg.data + "\n")