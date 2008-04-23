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
from SeriesListCtrl import SeriesListCtrl
from EpisodeListCtrl import EpisodeListCtrl
from data import db, series_list, series_filter
from ListViewProxy import ListViewProxy
from images import whats_new, whats_on, to_download, \
                   downloading, all_series, progess_log

class MainPanel(wx.Panel):

    def __init__(self, parent, id = -1):

        pre = wx.PrePanel()

        # two count values displaying number of
        # episodes that are reported new / updated
        
        res = xmlres.loadGuiResource('MainPanel.xrc')
        res.LoadOnPanel(pre, parent, "ID_MAIN_PANEL")
        self.PostCreate(pre)
        
        self._log_window = xrc.XRCCTRL(self, "ID_LOG_WINDOW")
        self._update_all = xrc.XRCCTRL(self, "ID_UPDATE_ALL")
        self._update_one = xrc.XRCCTRL(self, "ID_UPDATE_ONE")
        self._show_unseen = xrc.XRCCTRL(self, "ID_SHOW_UNSEEN")
        self._updated_view = xrc.XRCCTRL(self, "ID_UPDATED_VIEW")
        self._queue = xrc.XRCCTRL(self, "ID_QUEUE")
        self._notifyarea = xrc.XRCCTRL(self, "ID_NOTIFICATION_AREA")
        self._notifytext = xrc.XRCCTRL(self, "ID_NOTIFY_TEXT")
        self._clearNotify = xrc.XRCCTRL(self, "ID_CLEAR_NOTIFICATION")
        self._notebook = xrc.XRCCTRL(self, "ID_VIEW_BOOK")
        self._view_select = xrc.XRCCTRL(self, "ID_VIEW_SELECT")
        
        # put the mixin control in place and initialize the
        # columns and styles
        self._list_panel = xrc.XRCCTRL(self, "ID_SERIES_VIEW")
        self._series_selection = xrc.XRCCTRL(self, "ID_SERIES_LIST")
        self._series_list = SeriesListCtrl(self._list_panel)
        
        # create main view (for now)
        sizer = wx.BoxSizer()
        sizer.Add(self._series_list, 1, wx.EXPAND)
        self._list_panel.SetSizer(sizer)        
        
        self._createViewSelect()
        
        # add lists to all views 
        self._views = dict()
        self._tabToView = dict()
        views = [ ( "ID_NEW_UPDATED_VIEW", series_filter.VIEW_WHATS_NEW), 
                  ( "ID_WHATS_ON_VIEW",    series_filter.VIEW_WHATS_ON ),
                  ( "ID_DOWNLOAD_VIEW",    series_filter.VIEW_TO_DOWNLOAD ),
                  ( "ID_DOWNLOADING_VIEW", series_filter.VIEW_DOWNLOADING) ]
        
        for view in views:
            pnl = xrc.XRCCTRL(self, view[0])
            sizer = wx.BoxSizer()
            el = EpisodeListCtrl(pnl)
            self._views[view[1]] = el
            el.viewID = view[1]
            sizer.Add(el, 1, wx.EXPAND)
            pnl.SetSizer(sizer) 
            # NOTE: This is potentially not working when the panel on which 
            # the list ctrl is not the direct child of the notebook ctrl.
            self._tabToView[pnl.GetParent().GetId()] = el.viewID

        # the proxy class will dynamically assign all the
        # exposed methods to the current view            
        self._proxy = ListViewProxy(self._views)
         
        self.tmr = wx.Timer(self)
        self.tmr.Start(300)
        
        self.Bind(wx.EVT_TIMER, self._onTimer, self.tmr)
        self.Bind(wx.EVT_BUTTON, self._onUpdateAll, self._update_all)
        self.Bind(wx.EVT_BUTTON, self._onUpdateOne, self._update_one)
        self.Bind(wx.EVT_CHOICE, self._onSelectSeries, self._series_selection)
        self.Bind(wx.EVT_CHECKBOX, self._onShowOnlyUnseen, self._show_unseen)
        self.Bind(wx.EVT_CHOICE, self._onUpdatedViewSelect, self._updated_view)
        self.Bind(wx.EVT_BUTTON, self._onClearNotify, self._clearNotify)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._onPageChanged, self._notebook)
        
        Publisher().subscribe(self._onSignalLogMessage, signals.APP_LOG)
        Publisher().subscribe(self._onSignalRestoreSeries, signals.DATA_SERIES_RESTORED)
        Publisher().subscribe(self._onAppInitialized, signals.APP_INITIALIZED)
        Publisher().subscribe(self._onDeleteSeries, signals.SERIES_DELETED)
        Publisher().subscribe(self._onAddSeries, signals.SERIES_ADDED)
        Publisher().subscribe(self._onSerieSelected, signals.SERIES_SELECT)
        Publisher().subscribe(self._onSerieUpdated, signals.SERIES_UPDATED)
        
        self._initNotifyArea()
        
        
    def _createViewSelect(self):
        """
        Creates the view selector window
        """
        sel = self._view_select
        sel.InsertColumn(0, "View Type", width = 130)

        self._icons = wx.ImageList(16, 16)
        self._icons.Add(whats_new.getBitmap())       #0
        self._icons.Add(whats_on.getBitmap())        #1
        self._icons.Add(to_download.getBitmap())     #2
        self._icons.Add(downloading.getBitmap())     #3
        self._icons.Add(all_series.getBitmap())      #4
        self._icons.Add(progess_log.getBitmap())     #5
        sel.SetImageList(self._icons, wx.IMAGE_LIST_SMALL)

        lst = [ ("What's Changed", 0, series_filter.VIEW_WHATS_NEW),
                ("Whats's On TV", 1, series_filter.VIEW_WHATS_ON),
                ("To Download", 2, series_filter.VIEW_TO_DOWNLOAD),
                ("Downloading...", 3, series_filter.VIEW_DOWNLOADING),
                ("All Series", 4, series_filter.VIEW_SERIES) ]
                
        for l in lst:
            index = sel.InsertStringItem(sys.maxint, l[0])
            sel.SetItemData(index, l[2])
            sel.SetItemImage(index, l[1], l[1])        
        
        
    def _onPageChanged(self, event):
        """
        Event happens before notebook is changed
        """
        pnl = self._notebook.GetPage(event.GetSelection())
        if pnl.GetId() in self._tabToView:
            print "Setting: ", self._tabToView[pnl.GetId()]
            self._proxy.setView(self._tabToView[pnl.GetId()])
            viewmgr.set_view(self._tabToView[pnl.GetId()])
            

    def _initNotifyArea(self):
        """
        Clear notification area
        """
        self._notifyarea.SetBackgroundColour(wx.NullColor)
        self._notifyarea.Refresh()  
        self._notifytext.SetLabel("No changes ...")
        self._updcount = 0
        self._newcount = 0        
        
        
    def _onClearNotify(self, event):
        """
        Clear message
        """
        self._initNotifyArea()
                
        
    def _onNewUpdatedEpisodes(self):
        """
        Display a message when we are ready to do so
        """
        
        #if self._newcount > 0 or self._updcount > 0:
        #    self._notifyarea.SetBackgroundColour(wx.Colour(150, 255, 145))
        #else:
        #    self._notifyarea.SetBackgroundColour(wx.NullColor())
        #self._notifyarea.Refresh()
        
        #str = ''
        #if self._newcount > 0 and self._updcount == 0:
        #    str = "You have %i new episodes!" % self._newcount
        #elif self._updcount > 0 and self._newcount == 0:
        #    str = "You have %i updated episodes!" % self._updcount
        #elif self._updcount > 0 and self._newcount > 0:
        #    str = "You have %i new and %i updated episodes!" % (self._newcount, self._updcount)
        #if str:
        #    self._notifytext.SetLabel(str)
        pass
           

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
        self._update_one.Enable(viewmgr.series_active())

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
            
        # enable / disable some button
        self._updated_view.Enable(not viewmgr.series_active())
            
        # kick view manager to probe for new series
        # this will result in signals being emitted to update lists
        
        new_c, upd_c = viewmgr.probe_series()      
        #if new_c > 0 or upd_c > 0:
            #self._newcount += new_c
            #self._updcount += upd_c
            #wx.CallAfter(self._onNewUpdatedEpisodes)
        
           
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
        sel.Append("[Updated Episodes]", -1)
        self._min_idx = sel.Append("[Queued Episodes]", -2)
        
        # populate the criteria filter
        uv = self._updated_view
        lst = [ ("Show all updated episodes (also incompletes)", series_filter.SHOW_ALL), 
                ("Show aired + upcoming episodes", series_filter.SHOW_UPCOMING),
                ("Show only aired episodes", series_filter.SHOW_AIRED) ]
        for str, data in lst:
            uv.Append(str, data)
        
        # look up last selection in list
        lastsel = appcfg.options[appcfg.CFG_UPDATED_VIEW]
        for i in xrange(0, uv.GetCount()):
            if uv.GetClientData(i) == lastsel:
                uv.SetSelection(i)
                break
                        
        # get a list of series, and show them
        result = db.store.find(series_list.Series)
        for series in result.order_by(series_list.Series.name):
            idx = self._series_selection.Append(series.name, series.id)
        
        self._show_unseen.SetValue(appcfg.options[appcfg.CFG_SHOW_UNSEEN])
        
        
    def _onUpdatedViewSelect(self, event):
        """
        Sync the last view
        """
        uv = self._updated_view        
        idx = uv.GetSelection()
        if idx != wx.NOT_FOUND:
            appcfg.options[appcfg.CFG_UPDATED_VIEW] = uv.GetClientData(idx)
            viewmgr.app_settings_changed()
            
        
    def _onSelectSeries(self, event):
        """ 
        Select a series, or all
        """
        busy = wx.BusyInfo("This can take a while, please wait ...", self)
        self._series_list.Freeze()
        
        sel = self._series_selection
        series_id = sel.GetClientData(sel.GetSelection())
        if series_id >= 0:
            series = db.store.get(series_list.Series, series_id)
            print "Selected series with ID: ", series_id
            viewmgr.set_selection(series)
       
        self._series_list.Thaw()
        busy.Destroy()

        
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
        for i in xrange(self._min_idx, sel.GetCount()):
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
        
        for i in xrange(self._min_idx, sel.GetCount()):
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
        for i in xrange(self._min_idx, sel.GetCount()):
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