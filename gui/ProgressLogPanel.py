import os, wx
import wx.xrc as xrc
from wx.lib.pubsub import Publisher
import xmlres
from data import appcfg, signals

class ProgressLogPanel(wx.Panel):

    def __init__(self, parent, id = -1):

        pre = wx.PrePanel()

        res = xmlres.loadGuiResource('ProgressLogPanel.xrc')
        res.LoadOnPanel(pre, parent, "ID_PROGRESSLOGPANEL")
        self.PostCreate(pre)

        self._log_window = xrc.XRCCTRL(self, "ID_LOG_WINDOW")

        Publisher().subscribe(self._onSignalLogMessage, signals.APP_LOG)

        
    def _onSignalLogMessage(self, msg):
        """
        Received a message, log it to the window
        """

        self._log_window.AppendText(msg.data + "\n")
