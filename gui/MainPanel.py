import os.path, wx
import wx.xrc as xrc
from wx.lib.pubsub import Publisher
from data import appcfg, viewmgr, signals
import xmlres
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
        
        self.tmr = wx.Timer(self)
        self.tmr.Start(300)
        
        self.Bind(wx.EVT_TIMER, self._onTimer, self.tmr)
        self.Bind(wx.EVT_BUTTON, self._onUpdateAll, self._update_all)
        Publisher().subscribe(self._onSignalLogMessage, signals.APP_LOG)
        

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
        
    def _onTimer(self, event):
        """
        Periodic update event to control the throbber and
        other menu elements
        """
    
        # update some controls
        self._update_all.Enable(not viewmgr.is_busy())
        
        # send messages from thread queue to log window
        q = viewmgr.retriever.msg_queue
        msgs = 30
        while not q.empty() and msgs > 0:
            viewmgr.app_log(q.get())
            msgs -= 1

        # kick view manager to probe for new series
        # this will result in signals being emitted to update lists
        viewmgr.probe_series()        
        