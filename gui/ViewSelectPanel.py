import os, wx, sys
import wx.xrc as xrc
from wx.lib.pubsub import Publisher
import xmlres
from data import appcfg, viewmgr
from data import series_filter, signals

from images import whats_new, whats_on, to_download, \
                   downloading, all_series, progess_log

class ViewSelectPanel(wx.Panel):

    def __init__(self, parent, id = -1):

        pre = wx.PrePanel()

        res = xmlres.loadGuiResource('ViewSelectPanel.xrc')
        res.LoadOnPanel(pre, parent, "ID_VIEWSELECTPANEL")
        self.PostCreate(pre)
        
        self._view_select = xrc.XRCCTRL(self, "ID_VIEW_SELECT")

        # temp var for delayed selection of view
        self._the_view = -1
                
        self._initViewSelect()
        
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._onViewSelected, self._view_select)
        Publisher.subscribe(self._onViewChanged, signals.SET_VIEW)
        
        
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
        
