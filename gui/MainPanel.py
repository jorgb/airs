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
        
        self._log_window = xrc.XRCCTRL(self, "ID_LOG_WINDOW")
        self._update_all = xrc.XRCCTRL(self, "ID_BUTTON1")

        self.Bind(wx.EVT_BUTTON, self._onUpdateAll, self._update_all)
        Publisher().subscribe(self._onSignalLogMessage, viewmgr.SIGNAL_APP_LOG)


    def _onUpdateAll(self, event):
        """
        Update all event, will send all series to the receive thread, where they 
        will be updated as they come back in 
        """
        viewmgr.get_all_series()


    def _onSignalLogMessage(self, msg):
        """
        Received a message, log it to the window
        """

        self._log_window.AppendText(msg.data + "\n")