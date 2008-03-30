import wx, sys
from wx.lib.mixins.listctrl import CheckListCtrlMixin
from data import signals
from wx.lib.pubsub import Publisher


def _sort(a, b):
    """
    Sort episode
    """
    # sort by series title first
    if a._series._serie_name > b._series._serie_name:
        return 1
    if a._series._serie_name < b._series._serie_name:
        return -1
    # then sort by episode number (newest first)
    if a._ep_nr > b._ep_nr:
        return -1
    if a._ep_nr < b._ep_nr:
        return 1
    # sort by episode title
    if a._ep_title > b._ep_title:
        return 1
    if a._ep_title < b._ep_title:
        return -1
    # else it's equal enough
    return 0


class SeriesListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        CheckListCtrlMixin.__init__(self)
        
        self._ep_lookup = dict()
        self._ep_idx = 0

        self.InsertColumn(0, "Episode")
        self.InsertColumn(1, "Series", width = 100)        
        self.InsertColumn(2, "Title", width = 220)        
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        Publisher().subscribe(self._onEpisodeAdded, signals.EPISODE_ADDED)
        Publisher().subscribe(self._onEpisodeDeleted, signals.EPISODE_DELETED)
        

    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)


    def OnCheckItem(self, index, flag):
        pass
            
    
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
                curr_ep = self._ep_lookup[self.GetItemData(idx)]
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
        index = self.InsertStringItem(pos, ep._ep_nr)
        self.SetStringItem(index, 1, ep._series._serie_name)
        self.SetStringItem(index, 2, ep._ep_title)
        
        self._ep_lookup[self._ep_idx] = ep
        self.SetItemData(index, self._ep_idx)
        
        
    def _onEpisodeDeleted(self, msg):
        """
        Respond to a deleted command of an episode
        """
        
        # Who ever made the wx.ListCtrl must be punished by a life sentence
        # because there is no way to store a reference to the object in 
        # the wx.ListCtrl we must poorly scan through the list ourselves
        ep = msg.data
        for episode_idx in self._ep_lookup.iterkeys():
            if self._ep_lookup[episode_idx] == ep:
                idx = self.FindItemData(-1, episode_idx)
                self.DeleteItem(idx)
                del self._ep_lookup[episode_idx]
                break
            