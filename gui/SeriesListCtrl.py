import wx, sys
from wx.lib.mixins.listctrl import CheckListCtrlMixin
from data import signals, viewmgr, db, series_list
from wx.lib.pubsub import Publisher


def _sort(a, b):
    """
    Sort episode
    """
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
        self.InsertColumn(4, "Date", width = 100) 
        
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        Publisher().subscribe(self._onEpisodeAdded, signals.EPISODE_ADDED)
        Publisher().subscribe(self._onEpisodeDeleted, signals.EPISODE_DELETED)
        

    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)


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
        if self.GetItemCount() > 0:            
            for idx in xrange(0, self.GetItemCount()):
                curr_ep = db.store.get(series_list.Episode, self.GetItemData(idx))
                if curr_ep:
                    if _sort(ep, curr_ep) <= 0:
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
        self.SetStringItem(index, 4, ep.aired)
        
        self._updating = True
        self.CheckItem(index, ep.seen != 0)
        self._updating = False
        
        self.SetItemData(index, ep.id)
        
        
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
   