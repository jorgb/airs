import os, wx, sys
import wx.xrc as xrc
from wx.lib.pubsub import Publisher
import xmlres
from data import appcfg, viewmgr, db
from data import series_filter, signals, series_list

from images import whats_new, whats_on, to_download, \
                   downloading, all_series, \
                   where_queue

class ViewSelectPanel(wx.Panel):

    def __init__(self, parent, id = -1):

        pre = wx.PrePanel()

        res = xmlres.loadGuiResource('ViewSelectPanel.xrc')
        res.LoadOnPanel(pre, parent, "ID_VIEWSELECTPANEL")
        self.PostCreate(pre)
        
        self._view_select = xrc.XRCCTRL(self, "ID_VIEW_SELECT")
        
        self._find_text = xrc.XRCCTRL(self, "ID_REFRESH_FIND")
        self._clear_filter = xrc.XRCCTRL(self, "ID_CLEAR_FIND")
        self._filter_text = xrc.XRCCTRL(self, "ID_TEXT_FILTER")
                
        # temp var for delayed selection of view
        self._the_view = -1

        self._our_problem = False
        
        self._initViewSelect()
              
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._onViewSelected, self._view_select)
        self.Bind(wx.EVT_TEXT, self._onFilterText, self._filter_text)
        self.Bind(wx.EVT_BUTTON, self._onRefreshFilter, self._find_text)
        self.Bind(wx.EVT_BUTTON, self._onClearFilter, self._clear_filter)
        self.Bind(wx.EVT_TEXT_ENTER, self._onRefreshFilter, self._filter_text)
        self.Bind(wx.EVT_UPDATE_UI, self._onUpdateUI)
        Publisher.subscribe(self._onViewChanged, signals.SET_VIEW)
        
        
    def _onUpdateUI(self, event):
        view_enabled = viewmgr._series_sel._view_type != -1        
        self._find_text.Enable(view_enabled)
        self._clear_filter.Enable(view_enabled)
        self._filter_text.Enable(view_enabled)        
        
        
    def _onFilterText(self, event):
        viewmgr._series_sel._filter_text = self._filter_text.GetValue()
         
        
    def _onRefreshFilter(self, event):
        busy = wx.BusyInfo("Please wait while searching ...", wx.GetApp()._frame)
        viewmgr._series_sel._filter_text = self._filter_text.GetValue()
        viewmgr._series_sel.syncEpisodes()
        busy.Destroy()
        

    def _onClearFilter(self, event):
        viewmgr._series_sel._filter_text = ''
        self._filter_text.SetValue('')
        viewmgr._series_sel.syncEpisodes()
        
        
    def _onViewChanged(self, msg):
        """
        Change the view
        """
        viewmgr._series_sel._filter_text = ''
        self._filter_text.SetValue('')            

        if not self._our_problem:
            view = msg.data
            if view == -1:
                idx = self._view_select.GetFirstSelected()
                if idx != wx.NOT_FOUND:
                    self._view_select.Select(idx, on = 0)
            else:
                idx = self._view_select.FindItemData(start = -1, data = view)
                if idx != wx.NOT_FOUND:
                    self._view_select.Select(idx, on = 1)

        
    def _afterViewSelect(self):
        """
        After call to finish the selection event first
        """
        if self._the_view != -1:
            self._our_problem = True            

            viewmgr._series_sel._filter_text = ''
            self._filter_text.SetValue('')            

            if self._the_view != series_filter.VIEW_SERIES:
                viewmgr._series_sel._selected_series_id = -1
            viewmgr.set_view(self._the_view)
            self._the_view = -1

            self._our_problem = False
        
        
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
        self._icons.Add(where_queue.getBitmap())     #5
        sel.SetImageList(self._icons, wx.IMAGE_LIST_SMALL)

        lst = [ ("All Series", 4, series_filter.VIEW_SERIES),
                ("What's Changed", 0, series_filter.VIEW_WHATS_NEW),
                ("What's Aired", 1, series_filter.VIEW_WHATS_ON),
                ("To Download ...", 2, series_filter.VIEW_TO_DOWNLOAD),
                ("Downloading ...", 3, series_filter.VIEW_DOWNLOADING),
                ("Find Episode(s) ...", 5, series_filter.VIEW_QUEUES)
                            
            ]
                
        for l in lst:
            index = sel.InsertStringItem(sys.maxint, l[0])
            sel.SetItemData(index, l[2])
            sel.SetItemImage(index, l[1], l[1])        
        
