import os.path, wx
import wx.xrc as xrc
from wx.lib.pubsub import Publisher
import appcfg, xmlres, viewmgr
from SeriesListCtrl import SeriesListCtrl

class MainPanel(wx.Panel):

    def __init__(self, parent, id = -1):

        pre = wx.PrePanel()

        res = xmlres.loadGuiResource('MainPanel.xrc')
        res.LoadOnPanel(pre, parent, "ID_MAIN_PANEL")
        self.PostCreate(pre)

        self.SetBackgroundColour(wx.WHITE)
        
        self._log_window = xrc.XRCCTRL(self, "ID_LOG_WINDOW")
        self._update_all = xrc.XRCCTRL(self, "ID_BUTTON1")

        # put the mixin control in place and initialize the
        # columns and styles
        self._list_panel = xrc.XRCCTRL(self, "ID_LIST_MIXIN")
        self._series_list = SeriesListCtrl(self._list_panel)

        sizer = wx.BoxSizer()
        sizer.Add(self._series_list, 1, wx.EXPAND)
        self._list_panel.SetSizer(sizer)        

        self._series_list.InsertColumn(0, "Episode")
        self._series_list.InsertColumn(1, "Title")
        
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