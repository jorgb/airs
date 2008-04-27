import os, wx, sys
import wx.xrc as xrc
from wx.lib.pubsub import Publisher
import xmlres
from data import appcfg, viewmgr, db
from data import series_filter, signals, series_list

from images import whats_new, whats_on, to_download, \
                   downloading, all_series, progess_log

class ViewSelectPanel(wx.Panel):

    def __init__(self, parent, id = -1):

        pre = wx.PrePanel()

        res = xmlres.loadGuiResource('ViewSelectPanel.xrc')
        res.LoadOnPanel(pre, parent, "ID_VIEWSELECTPANEL")
        self.PostCreate(pre)
        
        self._view_select = xrc.XRCCTRL(self, "ID_VIEW_SELECT")
        self._new_count = xrc.XRCCTRL(self, "ID_COUNT_NEW")
        self._upd_count = xrc.XRCCTRL(self, "ID_COUNT_UPDATED")
        self._new_text = xrc.XRCCTRL(self, "ID_NEW_TEXT")
        self._updated_text = xrc.XRCCTRL(self, "ID_UPDATED_TEXT")
        self._total_count = xrc.XRCCTRL(self, "ID_COUNT_TOTAL")
        self._clear_new = xrc.XRCCTRL(self, "ID_CLEAR_NEW")
        self._clear_updated = xrc.XRCCTRL(self, "ID_CLEAR_UPDATED")
        
        self._count_new = 0
        self._count_updated = 0 
        self._first_count = True

        # temp var for delayed selection of view
        self._the_view = -1
                
        self._initViewSelect()
        
        self._timer = wx.Timer(self)
        self._timer.Start(2000)
        self.Bind(wx.EVT_TIMER, self._onUpdateStats)        
        self._syncStats()
      
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._onViewSelected, self._view_select)
        self.Bind(wx.EVT_BUTTON, self._onClearNew, self._clear_new)
        self.Bind(wx.EVT_BUTTON, self._onClearUpdated, self._clear_updated)
        Publisher.subscribe(self._onViewChanged, signals.SET_VIEW)
      
        
    def _onClearNew(self, event):
        viewmgr.clear_new_episodes()
        
    def _onClearUpdated(self, event):
        viewmgr.clear_updated_episodes()
        
    def _onUpdateStats(self, event):
        self._syncStats()
        
    
    def _syncStats(self):
        ep = series_list.Episode()
        c = db.store.execute("select count(*) from episode where status = 0")
        c = c.get_one()[0]

        if not self._first_count:
            if c > self._count_new:
                self._setHighlight(self._new_text)
            elif c < self._count_new:
                self._clearHighlight(self._new_text)
                
        self._new_count.SetLabel("%i" % c)
        self._count_new = c
        
        c = db.store.execute("select count(*) from episode where changed != 0 and status != 0")
        c = c.get_one()[0]

        if not self._first_count:
            if c > self._count_updated:
                self._setHighlight(self._updated_text)
            elif c < self._count_updated:
                self._clearHighlight(self._updated_text)
                
        self._upd_count.SetLabel("%i" % c)
        self._count_updated = c
        
        c = db.store.execute("select count(*) from episode")
        c = c.get_one()[0]
        self._total_count.SetLabel("%i" % c)
        
        self._clear_new.Enable(self._count_new != 0)
        self._clear_updated.Enable(self._count_updated != 0)
        
        self._first_count = False
    
        
    def _setHighlight(self, label):
        label.SetForegroundColour(appcfg.highlightColor)
        fnt = label.GetFont()
        fnt.SetWeight(wx.FONTWEIGHT_BOLD)
        label.SetFont(fnt)
        self.Layout()
        self.Refresh()        
        
        
    def _clearHighlight(self, label):
        label.SetForegroundColour(self.GetForegroundColour())
        fnt = label.GetFont()
        fnt.SetWeight(wx.FONTWEIGHT_NORMAL)
        label.SetFont(fnt)
        self.Layout()
        label.Refresh()        
        
        
    def _onViewChanged(self, msg):
        """
        Change the view
        """
        view = msg.data
        if view == -1:
            idx = self._view_select.GetFirstSelected()
            if idx != wx.NOT_FOUND:
                self._view_select.Select(idx, on = 0)
        else:
            idx = self._view_select.FindItemData(start = 0, data = view)
            if idx != wx.NOT_FOUND:
                self._view_select.Select(idx, on = 1)

        
    def _afterViewSelect(self):
        """
        After call to finish the selection event first
        """
        if self._the_view != -1:
            viewmgr.set_view(self._the_view)
            self._the_view = -1
        
        
    def _onViewSelected(self, event):
        """
        Set the view to the proper selected item
        """
        idx = self._view_select.GetFirstSelected()
        if idx != wx.NOT_FOUND:
            self._the_view = self._view_select.GetItemData(idx)
            wx.CallAfter(self._afterViewSelect)
               

    def _initViewSelect(self):
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
        
