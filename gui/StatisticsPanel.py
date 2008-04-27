import os, wx, sys
import wx.xrc as xrc
from wx.lib.pubsub import Publisher
import xmlres
from data import appcfg, viewmgr, db
from data import series_filter, signals, series_list

class StatisticsPanel(wx.Panel):

    def __init__(self, parent, id = -1):

        pre = wx.PrePanel()

        res = xmlres.loadGuiResource('StatisticsPanel.xrc')
        res.LoadOnPanel(pre, parent, "ID_STATISTICSPANEL")
        self.PostCreate(pre)
        
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
                        
        self._timer = wx.Timer(self)
        self._timer.Start(2000)
        self.Bind(wx.EVT_TIMER, self._onUpdateStats)        
        self._syncStats()
      
        self.Bind(wx.EVT_BUTTON, self._onClearNew, self._clear_new)
        self.Bind(wx.EVT_BUTTON, self._onClearUpdated, self._clear_updated)
      
        
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
        
        
