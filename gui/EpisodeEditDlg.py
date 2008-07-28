#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import sys
import wx
import wx.xrc as xrc
import xmlres
import datetime
from data import appcfg, options
from data import viewmgr, db, searches
from data import series_list

class EpisodeEditDlg(wx.Dialog):
    def __init__(self, parent, id = wx.ID_ANY):
        
        pre = wx.PreDialog()
        res = xmlres.loadGuiResource("EpisodeEditDlg.xrc")
        res.LoadOnDialog(pre, parent, "EpisodeEditDlg")
        self.PostCreate(pre)

        self._season = xrc.XRCCTRL(self, "ID_SEASON")
        self._title = xrc.XRCCTRL(self, "ID_TITLE")
        self._aired = xrc.XRCCTRL(self, "ID_AIRED")
        self._status = xrc.XRCCTRL(self, "ID_STATUS")
        self._updated = xrc.XRCCTRL(self, "ID_UPDATED")
        self._lock_update = xrc.XRCCTRL(self, "ID_LOCK_UPDATE")
        self._new = xrc.XRCCTRL(self, "ID_NEW")
        
        self._dt_valid = False
        
        statuses = [ ( series_list.EP_NEW,         "New"),
                     ( series_list.EP_TO_DOWNLOAD, "To Download"),
                     ( series_list.EP_DOWNLOADING, "Downloading"),
                     ( series_list.EP_DOWNLOADED,  "Downloaded"),
                     ( series_list.EP_READY,       "Ready"),
                     ( series_list.EP_SEEN,        "Seen") ]

        self._st_lookup = dict()
        for st in statuses:
            idx = self._status.Append( st[1], st[0] )
            self._st_lookup[st[0]] = idx
        
        self.Bind(wx.EVT_BUTTON, self._onOK,  xrc.XRCCTRL(self, "wxID_OK"))
        self.Bind(wx.EVT_TEXT, self._onEdited, self._title)
        self.Bind(wx.EVT_TEXT, self._onEdited, self._season)
        self.Bind(wx.EVT_DATE_CHANGED, self._onEdited, self._aired)
        
    def _onEdited(self, event):
        self._lock_update.SetValue(True)

        
    def ObjectToGui(self, episode):
        self._season.SetValue(episode.season)
        self._title.SetValue(episode.title)
        
        d = episode.getAired()
        if d is not None:
            dt = wx.DateTimeFromDMY(d.day, d.month - 1, d.year)
            self._aired.SetValue(dt)
            self._dt_valid = True
            
        pos = self._st_lookup[episode.status]
        self._status.SetSelection(pos)

        self._new.SetValue(episode.new != 0)
        self._updated.SetValue(episode.changed != 0)
        self._lock_update.SetValue(episode.locked != 0)
        
    
    def GuiToObject(self, episode):
        dt = self._aired.GetValue()
        d = datetime.date(day = dt.GetDay(), month = dt.GetMonth()+1, year = dt.GetYear())
        if self._dt_valid:
            episode.setAired(d)
        
        episode.season = self._season.GetValue().strip()
        episode.title = self._title.GetValue().strip()
        episode.status = self._status.GetClientData(self._status.GetSelection())
        
        if self._new.GetValue():
            episode.new = 1
        else:
            episode.new = 0
        
        if self._updated.GetValue():
            episode.changed = 1
        else:
            episode.changed = 0
                
        if self._lock_update.GetValue():
            episode.locked = 1
        else:
            episode.locked = 0
            
        
    def _onOK(self, event): 
        title = self._title.GetValue().strip()
        
        if title == '':
            wx.MessageBox("Please fill in a title!", "Error", wx.ICON_ERROR)
            return
        
        event.Skip()

