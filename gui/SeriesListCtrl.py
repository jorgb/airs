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
    # then sort by episode number
    if a._ep_nr > b._ep_nr:
        return 1
    if a._ep_nr < b._ep_nr:
        return -1
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
        
        self._episorted = list()

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
        if len(self._episorted) == 0:
            self._episorted.append(ep)
        else:
            idx = 0
            added = False
            for e in self._episorted:
                if _sort(ep, e) <= 0:
                    self._episorted.insert(idx, ep)
                    added = True
                    pos = idx
                    break
                idx += 1
            if not added:
                pos = idx
                self._episorted.append(ep)
        
        index = self.InsertStringItem(pos, ep._ep_nr)
        self.SetStringItem(index, 1, ep._series._serie_name)
        self.SetStringItem(index, 2, ep._ep_title)
        #self.SetItemData(index, ep)


    def _onEpisodeDeleted(self, msg):
        pass
