#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import wx, sys
from wx.lib.mixins.listctrl import CheckListCtrlMixin
from data import signals, viewmgr, db, series_list
from wx.lib.pubsub import Publisher


def _sort_updated(a, b):
    """
    Sort method, updated view 
    """
    adate = a.getDate()
    bdate = b.getDate()
    
    if adate and bdate:
        if adate < bdate:
            return 1
        if adate > bdate:
            return -1
    else:
        if adate and not bdate:
            return -1
        if not adate and bdate:
            return 1
                
    if a.season > b.season:
        return -1
    if a.season < b.season:
        return 1
    if a.number > b.number:
        return -1
    if a.number < b.number:
        return 1
    # sort by episode title
    if a.title > b.title:
        return 1
    if a.title < b.title:
        return -1
    # else it's equal enough
    return 0


def _sort_normal(a, b):
    """
    Sort method, normal view (no updated) 
    """
    if a.season > b.season:
        return -1
    if a.season < b.season:
        return 1

    adate = a.getDate()
    bdate = b.getDate()    
    
    if adate and bdate:
        if adate < bdate:
            return 1
        if adate > bdate:
            return -1
    if a.number > b.number:
        return -1
    if a.number < b.number:
        return 1
    # sort by episode title
    if a.title > b.title:
        return 1
    if a.title < b.title:
        return -1
    # else it's equal enough
    return 0


class SeriesListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        CheckListCtrlMixin.__init__(self)
        
        self._ep_idx = 0
        self._updating = False

        self.InsertColumn(0, "Nr.", width = 50)
        self.InsertColumn(1, "Season", width = 70)
        self.InsertColumn(2, "Series", width = 100)        
        self.InsertColumn(3, "Title", width = 220) 
        self.InsertColumn(4, "Stat", width = 40) 
        self.InsertColumn(5, "Date", width = 100) 
        
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self._onMenuPopup)
        Publisher().subscribe(self._onEpisodeAdded, signals.EPISODE_ADDED)
        Publisher().subscribe(self._onEpisodeDeleted, signals.EPISODE_DELETED)
        Publisher().subscribe(self._onEpisodeUpdated, signals.EPISODE_UPDATED)
        Publisher().subscribe(self._onClearAll, signals.EPISODES_CLEARED)
        

    def _onMenuPopup(self, event):
        """
        Create popup menu to perform some options
        """
        if self.GetFirstSelected() != wx.NOT_FOUND:        
            menu = wx.Menu()
    
            if viewmgr._series_sel._selection_id != -2:
                m5 = menu.Append(wx.NewId(), "&Add to Queue View")
                menu.AppendSeparator()
    
                m1 = menu.Append(wx.NewId(), "&Mark Episode Processed")
                m2 = menu.Append(wx.NewId(), "&Mark Episode Unprocessed")
                menu.AppendSeparator()
                
                m3 = menu.Append(wx.NewId(), "&Clear Updated Status")
                m4 = menu.Append(wx.NewId(), "&Set Updated Status")

                self.Bind(wx.EVT_MENU, self._onCheckItem, m1)
                self.Bind(wx.EVT_MENU, self._onUncheckItem, m2)
                self.Bind(wx.EVT_MENU, self._onAddToQueueView, m5)
                self.Bind(wx.EVT_MENU, self._onClearUpdatedStatus, m1)
                self.Bind(wx.EVT_MENU, self._onSetUpdatedStatus, m2)
            else:
                m5 = menu.Append(wx.NewId(), "&Clear from Queue View")                
                menu.AppendSeparator()
                m6 = menu.Append(wx.NewId(), "&Revert to Updated")

                self.Bind(wx.EVT_MENU, self._onRemoveQueueView, m5)
                self.Bind(wx.EVT_MENU, self._onSetUpdatedStatus, m6)
    
            self.PopupMenu(menu)
            menu.Destroy()    

            
    def __getSelectedEpisodes(self):
        episodes = list()
        idx = self.GetFirstSelected()
        while idx != wx.NOT_FOUND:
            episode = db.store.get(series_list.Episode, self.GetItemData(idx))           
            if episode:
                episodes.append(episode)
            idx = self.GetNextSelected(idx)
        return episodes
            
            
    def _onAddToQueueView(self, event):
        episodes = self.__getSelectedEpisodes()
        for episode in episodes:
            episode.last_in = 0
            episode.queued = 1
            db.store.commit()
            viewmgr.episode_updated(episode)
    

    def _onRemoveQueueView(self, event):
        episodes = self.__getSelectedEpisodes()
        for episode in episodes:
            episode.last_in = 0
            episode.queued = 0
            episode.seen = 1
            db.store.commit()
            viewmgr.episode_updated(episode)
            
            
    def _onClearUpdatedStatus(self, event):
        episodes = self.__getSelectedEpisodes()
        for episode in episodes:
            episode.last_in = 0
            db.store.commit()
            viewmgr.episode_updated(episode)


    def _onSetUpdatedStatus(self, event):
        episodes = self.__getSelectedEpisodes()
        for episode in episodes:
            episode.last_in = 1
            episode.queued = 0
            db.store.commit()
            viewmgr.episode_updated(episode)

            
    def _onCheckItem(self, event):
        """
        Check all the selected items
        """
        episodes = self.__getSelectedEpisodes()
        for episode in episodes:
            episode.seen = 1
            episode.last_in = 0
            episode.queued = 0
            db.store.commit()
            viewmgr.episode_updated(episode)
        

    def _onUncheckItem(self, event):
        """
        Check all the selected items
        """
        episodes = self.__getSelectedEpisodes()
        for episode in episodes:
            episode.seen = 0
            db.store.commit()
            viewmgr.episode_updated(episode)
            
            
    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)


    def _onClearAll(self, msg):
        """
        Clear all episodes
        """
        self.DeleteAllItems()


    def OnCheckItem(self, index, flag):
        """
        Check the item as seen or unseen
        """
        # unfortunately, some really dump developers hook up an event
        # when the CheckItem is called PROGRAMATICALLY, and I have to 
        # work around not letting it screw up my flow of events (*sigh*)
        if not self._updating:
            episode_id = self.GetItemData(index)
            episode = db.store.get(series_list.Episode, episode_id)
            if flag:
                episode.seen = 1
                episode.last_in = 0
                episode.queued = 0
            else:
                episode.seen = 0
            
            db.store.commit()
            viewmgr.episode_updated(episode)
            
    
    def _onEpisodeAdded(self, msg):
        """
        Add an episode to the list, but sort it first and
        add the item to the list later with the given index
        """
        ep = msg.data
        pos = 0
        
        # dynamically determine position
        if viewmgr._series_sel._selection_id >= 0:
            sortfunc = _sort_normal
        else:
            sortfunc = _sort_updated
        
        if self.GetItemCount() > 0:            
            for idx in xrange(0, self.GetItemCount()):
                curr_ep = db.store.get(series_list.Episode, self.GetItemData(idx))
                if curr_ep:
                    if sortfunc(ep, curr_ep) <= 0:
                        pos = idx
                        break
                    pos += 1
        
        self._insertEpisode(ep, pos)
                

    def _insertEpisode(self, ep, pos):
        """
        Inserts the episode in the list
        """
        self._ep_idx += 1
        index = self.InsertStringItem(pos, ep.number)
        self.SetStringItem(index, 1, ep.season)
        
        series = db.store.get(series_list.Series, ep.series_id)
        if series:
            self.SetStringItem(index, 2, series.name)
        self.SetStringItem(index, 3, ep.title)
        str = ""
        if ep.last_in != 0:
            str = "U"
        if ep.queued != 0:
            str += "D"
        self.SetStringItem(index, 4, str)
        self.SetStringItem(index, 5, ep.aired)
        
        self._updating = True
        self.CheckItem(index, ep.seen != 0)
        self._updating = False
        
        self.SetItemData(index, ep.id)
        

    def _onEpisodeUpdated(self, msg):
        """
        Inserts the episode in the list
        """
        
        ep = msg.data
        idx = self.FindItemData(-1, ep.id) 
        if idx != wx.NOT_FOUND:     
            self.SetStringItem(idx, 0, ep.number)
            self.SetStringItem(idx, 1, ep.season)
            self.SetStringItem(idx, 3, ep.title)
            str = ""
            if ep.last_in != 0:
                str = "U"
            if ep.queued != 0:
                str += "D"
            self.SetStringItem(idx, 4, str)
            self.SetStringItem(idx, 5, ep.aired)        

            self._updating = True
            self.CheckItem(idx, ep.seen != 0)
            self._updating = False            
            
        
    def _onEpisodeDeleted(self, msg):
        """
        Respond to a deleted command of an episode
        """
        
        # Who ever made the wx.ListCtrl must be punished by a life sentence
        # because there is no way to store a reference to the object in 
        # the wx.ListCtrl we must poorly scan through the list ourselves
        ep = msg.data
        if self.GetItemCount() > 0:            
            idx = self.FindItemData(-1, ep.id)                
            if idx != wx.NOT_FOUND:
                self.DeleteItem(idx)
   