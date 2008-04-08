import os.path, wx
import wx.xrc as xrc
from wx.lib.pubsub import Publisher
from data import appcfg, viewmgr, signals
import xmlres
from SeriesListCtrl import SeriesListCtrl
from data import db, series_list

class MainPanel(wx.Panel):

    def __init__(self, parent, id = -1):

        pre = wx.PrePanel()

        res = xmlres.loadGuiResource('MainPanel.xrc')
        res.LoadOnPanel(pre, parent, "ID_MAIN_PANEL")
        self.PostCreate(pre)

        #self.SetBackgroundColour(wx.WHITE)
        
        self._log_window = xrc.XRCCTRL(self, "ID_LOG_WINDOW")
        self._update_all = xrc.XRCCTRL(self, "ID_UPDATE_ALL")
        self._update_one = xrc.XRCCTRL(self, "ID_UPDATE_ONE")
        self._show_unseen = xrc.XRCCTRL(self, "ID_SHOW_UNSEEN")
        self._reset_updated = xrc.XRCCTRL(self, "ID_RESET_UPDATED")

        # put the mixin control in place and initialize the
        # columns and styles
        self._list_panel = xrc.XRCCTRL(self, "ID_LIST_MIXIN")
        self._series_selection = xrc.XRCCTRL(self, "ID_SERIES_LIST")
        self._series_list = SeriesListCtrl(self._list_panel)

        #self._series_selection.Append("[All Series]", clientData = None)
        
        sizer = wx.BoxSizer()
        sizer.Add(self._series_list, 1, wx.EXPAND)
        self._list_panel.SetSizer(sizer)        
        
        self.tmr = wx.Timer(self)
        self.tmr.Start(300)
        
        self.Bind(wx.EVT_TIMER, self._onTimer, self.tmr)
        self.Bind(wx.EVT_BUTTON, self._onUpdateAll, self._update_all)
        self.Bind(wx.EVT_BUTTON, self._onUpdateOne, self._update_one)
        self.Bind(wx.EVT_CHOICE, self._onSelectSeries, self._series_selection)
        self.Bind(wx.EVT_CHECKBOX, self._onShowOnlyUnseen, self._show_unseen)
        self.Bind(wx.EVT_BUTTON, self._onResetUpdated, self._reset_updated) 
        Publisher().subscribe(self._onSignalLogMessage, signals.APP_LOG)
        Publisher().subscribe(self._onSignalRestoreSeries, signals.DATA_SERIES_RESTORED)
        Publisher().subscribe(self._onAppInitialized, signals.APP_INITIALIZED)
        Publisher().subscribe(self._onDeleteSeries, signals.SERIES_DELETED)
        Publisher().subscribe(self._onAddSeries, signals.SERIES_ADDED)
        Publisher().subscribe(self._onSerieSelected, signals.SERIES_SELECT)
        Publisher().subscribe(self._onSerieUpdated, signals.SERIES_UPDATED)
        
        
    def _onUpdateAll(self, event):
        """
        Update all event, will send all series to the receive thread, where they 
        will be updated as they come back in 
        """
        viewmgr.get_all_series()

        
    def _onUpdateOne(self, event):
        """
        Update the selected series only
        """
        viewmgr.get_selected_series()
        

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

        # enable / disable some button
        self._reset_updated.Enable(self._series_list.GetFirstSelected() != wx.NOT_FOUND)
            
        # kick view manager to probe for new series
        # this will result in signals being emitted to update lists
        viewmgr.probe_series()        
        
        
    def _onSignalRestoreSeries(self, msg):
        """
        Perform adding of a restored item to the 
        list of series to select
        """
        series = msg.data
        self._series_selection.Append(series._serie_name, series)

        
    def _onAppInitialized(self, msg):
        """
        Everything is initialized, set the GUI to default
        """
        
        # show only updated
        sel = self._series_selection
        sel.Append("[Updated Series]", -1)
        
        # get a list of series, and show them
        result = db.store.find(series_list.Series)
        for series in result.order_by(series_list.Series.name):
            idx = self._series_selection.Append(series.name, series.id)
        
        self._show_unseen.SetValue(appcfg.options[appcfg.CFG_SHOW_UNSEEN])
        
        
    def _onSelectSeries(self, event):
        """ 
        Select a series, or all
        """
        busy = wx.BusyInfo("This can take a while, please wait ...", self)
        self._series_list.Freeze()
        
        sel = self._series_selection
        series_id = sel.GetClientData(sel.GetSelection())
        if series_id != -1:
            series = db.store.get(series_list.Series, series_id)
        else:
            series = None
        viewmgr.set_selection(series)
       
        busy.Destroy()
        self._series_list.Thaw()

        
    def _onDeleteSeries(self, msg):
        """
        Respond to series removal
        """
        curr_id = -1
        sel = self._series_selection
        series = msg.data

        if sel.GetSelection() != wx.NOT_FOUND:
            curr_id = sel.GetClientData(sel.GetSelection()) 
        
        # first remove
        for i in xrange(0, sel.GetCount()):
            if sel.GetClientData(i) == series.id:
                sel.Delete(i)
                break

        # then reset (some platforms do not retain old sel)
        for i in xrange(0, sel.GetCount()):
            if sel.GetClientData(i) == curr_id:
                sel.SetSelection(i)
                break
        

    def _onSerieUpdated(self, msg):
        """
        Series is updated, we must re-sync our view
        """
        sel = self._series_selection
        series = msg.data
        
        for i in xrange(0, sel.GetCount()):
            if sel.GetClientData(i) == series.id:
                sel.SetString(i, series.name)
                sel.SetSelection(i)
                break
        
            
    def _onAddSeries(self, msg):
        """
        Series added, update lists
        """
        sel = self._series_selection
        series = msg.data
        idx = 0
        for i in xrange(0, sel.GetCount()):
            if sel.GetStringSelection() < series.name :
                idx += 1
        sel.Insert(series.name, idx, series.id)
                
                
    def _onSerieSelected(self, msg):
        """
        A new serie is selected, update list index if needed
        """
        sel = self._series_selection
        series = msg.data
       
        if series:
            id = series.id
        else:
            id = -1
        
        if series:
            for i in xrange(0, sel.GetCount()):
                series_id = sel.GetClientData(i)
                if series_id == series.id:
                    sel.SetSelection(i)
                    return
          

    def _onResetUpdated(self, event):
        """
        Reset the updated flag of the selected series
        """
        
        episodes = list()
        
        idx = self._series_list.GetFirstSelected()
        while idx != wx.NOT_FOUND:
            id = self._series_list.GetItemData(idx)
            episode = db.store.get(series_list.Episode, id)
            if episode:
                episodes.append(episode)
            idx = self._series_list.GetNextSelected(idx)
        
        # we do it in two steps, not to disturb the selections
        if episodes:
            for episode in episodes:
                episode.last_in = 0
                db.store.flush()
                viewmgr.episode_updated(episode)
    
            db.store.commit()
                

    def _onShowOnlyUnseen(self, event):
        """
        Toggle filter for seen / unseen events. Also save this in 
        the settings.
        """
        
        show_unseen = self._show_unseen.GetValue()
        appcfg.options[appcfg.CFG_SHOW_UNSEEN] = show_unseen
        
        viewmgr.app_settings_changed()