#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import sys, os.path, wx
import wx.xrc as xrc
from wx.lib.pubsub import Publisher
from data import appcfg, viewmgr, signals
import xmlres
from EpisodeListCtrl import EpisodeListCtrl
from data import db, series_list, series_filter
import EpisodeEditDlg

class MainPanel(wx.Panel):

    def __init__(self, parent, id = -1):

        pre = wx.PrePanel()

        # two count values displaying number of
        # episodes that are reported new / updated
        
        res = xmlres.loadGuiResource('MainPanel.xrc')
        res.LoadOnPanel(pre, parent, "ID_MAIN_PANEL")
        self.PostCreate(pre)

        self._update_all = xrc.XRCCTRL(self, "ID_UPDATE_ALL")
        self._update_one = xrc.XRCCTRL(self, "ID_UPDATE_ONE")

        self._show_unseen = xrc.XRCCTRL(self, "ID_SHOW_UNSEEN")

        self._queue = xrc.XRCCTRL(self, "ID_QUEUE")

        self._episodeFilter = xrc.XRCCTRL(self, "ID_EPISODE_FILTER")
        
        self._episodeFilter.Append("View episodes from last week", clientData = 1)
        self._episodeFilter.Append("View episodes from last two weeks", clientData = 2)
        self._episodeFilter.Append("View episodes from last month", clientData = 4)
        self._episodeFilter.Append("View episodes from last two months", clientData = 8)
        
        idx = appcfg.options[appcfg.CFG_EPISODE_DELTA]
        self._episodeFilter.SetSelection(idx)
        viewmgr._series_sel._weeks_delta = self._episodeFilter.GetClientData(idx)

        # put the mixin control in place and initialize the
        # columns and styles
        self._list_panel = xrc.XRCCTRL(self, "ID_EPISODE_VIEW")
        self._series_selection = xrc.XRCCTRL(self, "ID_SERIES_LIST")
        self._series_list = EpisodeListCtrl(self._list_panel)

        # create main view (for now)
        sizer = wx.BoxSizer()
        sizer.Add(self._series_list, 1, wx.EXPAND)
        self._list_panel.SetSizer(sizer)        
                
        self.tmr = wx.Timer(self)
        self.tmr.Start(300)
        
        self.Bind(wx.EVT_TIMER, self._onTimer, self.tmr)
        self.Bind(wx.EVT_BUTTON, self._onUpdateAll, self._update_all)
        self.Bind(wx.EVT_BUTTON, self._onUpdateOne, self._update_one)
        self.Bind(wx.EVT_CHOICE, self._onSelectSeries, self._series_selection)
        self.Bind(wx.EVT_CHOICE, self._onEpisodeFilter, self._episodeFilter)
        self.Bind(wx.EVT_CHECKBOX, self._onShowOnlyUnseen, self._show_unseen)
        self.Bind(wx.EVT_UPDATE_UI, self._onGuiUpdated)
        
        Publisher().subscribe(self._onSignalRestoreSeries, signals.DATA_SERIES_RESTORED)
        Publisher().subscribe(self._onAppInitialized, signals.APP_INITIALIZED)
        Publisher().subscribe(self._onDeleteSeries, signals.SERIES_DELETED)
        Publisher().subscribe(self._onAddSeries, signals.SERIES_ADDED)
        Publisher().subscribe(self._onSerieSelected, signals.SERIES_SELECT)
        Publisher().subscribe(self._onSerieUpdated, signals.SERIES_UPDATED)
        Publisher().subscribe(self._onViewChanged, signals.SET_VIEW)
        Publisher().subscribe(self._onEditEpisode, signals.EPISODE_EDIT)
                              
        
    def _onEditEpisode(self, msg):
        episode_id = msg.data
        episode = db.store.find(series_list.Episode, series_list.Episode.id == episode_id).one()
        if episode is not None:
            dlg = EpisodeEditDlg.EpisodeEditDlg(self)
            dlg.ObjectToGui(episode)            
            if dlg.ShowModal() == wx.ID_OK:
                dlg.GuiToObject(episode)
                db.store.commit()
                viewmgr.episode_updated(episode)
            dlg.Destroy()
            
            
    def _onViewChanged(self, msg):
        view = msg.data
        if view != series_filter.VIEW_SERIES:
            self._series_selection.SetSelection(-1)
        else:
            for i in xrange(0, self._series_selection.GetCount()):
                if self._series_selection.GetClientData(i) == viewmgr._series_sel._selected_series_id:
                    self._series_selection.SetSelection(i)
                    break
        
            
    def _onEpisodeFilter(self, event):
        """
        Toggle the filter for the date span 
        """
        idx = self._episodeFilter.GetSelection()
        appcfg.options[appcfg.CFG_EPISODE_DELTA] = idx
        
        viewmgr._series_sel._weeks_delta = self._episodeFilter.GetClientData(idx)
        viewmgr._series_sel.syncEpisodes()
        
        
    def _onGuiUpdated(self, event):
        """
        Called after every GUI update
        """
        
        view_enabled = viewmgr._series_sel._view_type != -1

        self._update_all.Enable(not viewmgr.is_busy())
        self._update_one.Enable(view_enabled and viewmgr.series_active())
        self._show_unseen.Enable(viewmgr._series_sel._view_type == series_filter.VIEW_SERIES)
        self._episodeFilter.Enable(viewmgr._series_sel._view_type == series_filter.VIEW_WHATS_ON)
        #self._series_selection.Enable(viewmgr._series_sel._view_type == series_filter.VIEW_SERIES)
        

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
        
        
    def _onTimer(self, event):
        """
        Periodic update event to control the throbber and
        other menu elements
        """
    
        # send messages from thread queue to log window
        q = viewmgr.retriever.msg_queue
        msgs = 30
        while not q.empty() and msgs > 0:
            viewmgr.app_log(q.get())
            msgs -= 1

        # show queue progress
        bs, cs = viewmgr.retriever.getProgress()
        self._queue.SetRange(bs)
        self._queue.SetValue(cs)
            
        # kick view manager to probe for new series        
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

        # get a list of series, and show them
        result = db.store.find(series_list.Series)
        for series in result.order_by(series_list.Series.name):
            idx = self._series_selection.Append(series.name, series.id)
        
        self._show_unseen.SetValue(appcfg.options[appcfg.CFG_SHOW_UNSEEN])
        

    def _onSelectSeries(self, event):
        """ 
        Select a series, or all
        """
        self._series_list.Freeze()
        busy = wx.BusyInfo("This can take a while, please wait ...", wx.GetApp()._frame)
        
        sel = self._series_selection
        series_id = sel.GetClientData(sel.GetSelection())
        if series_id >= 0:
            series = db.store.get(series_list.Series, series_id)
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
            if sel.GetString(i) < series.name :
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
          

    def _onShowOnlyUnseen(self, event):
        """
        Toggle filter for seen / unseen events. Also save this in 
        the settings.
        """
        
        show_unseen = self._show_unseen.GetValue()
        appcfg.options[appcfg.CFG_SHOW_UNSEEN] = show_unseen
        
        viewmgr.app_settings_changed()