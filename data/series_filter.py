#
# Module that manages a selection list object
# which will send out signals if the criteria
# for the list changes
#

from wx.lib.pubsub import Publisher
import signals
import series_list
import db

class SeriesSelectionList(object):
    def __init__(self):
        self._selection = list()
        self._episodes = list()

        # selection criteria for the series ID. If an ID is selected
        # all episodes belonging to a different series are removed
        self._selection_id = -1
        self._show_only_unseen = False
        
    
    def setSelection(self, sel_id):
        """
        Sets the ID of the selection. This will trigger an episodes
        restore and an update of the view filter
        """
        if self._selection_id != sel_id:
            self._selection_id = sel_id
            
            # remove all from list
            self.syncEpisodes()
            self._episodes = list()
        
            if self._selection_id != -1:
                # restore the episode list belonging to this series_id
                result = db.store.find(series_sel.Episodes, 
                                       series_sel.Episodes.series_id == self._selection_id)
                episodes = [episode for episode in result]
                self._episodes = episodes[:]
    
                # resync for adding new items        
                self.syncEpisodes()
        
                
    def add_episode(self, episode):
        """
        Attempts to add episode given the proper criteria
        if it does match an add command is issued.
        """
        # no add if the selection is incorrect
        if episode.series_id != self._selection_id:
            return
            
        if episode not in self._episodes:
            self._episodes.append(episode)
            if self._checkAgainstCriteria(episode):
                self._selection.append(episode)
                Publisher().sendMessage(signals.EPISODE_ADDED, episode)
       

    def update_episode(self, episode):
        """
        Attempts an episode update, when present in list
        we reevaluate and issue the change
        """
        # no change if the selection is incorrect
        if episode.series_id != self._selection_id:
            return

        # issue the proper signal for update, delete or adding            
        if episode in self._episodes:
            allowed = self._checkAgainstCriteria(episode)
            if allowed and episode in self._selection:
                Publisher().sendMessage(signals.EPISODE_UPDATED, episode)
            else if not allowed and episode in self._selection:
                Publisher().sendMessage(signals.EPISODE_DELETED, episode)
            else if allowed and episode not in self._selection:
                Publisher().sendMessage(signals.EPISODE_ADDED, episode)


    def syncEpisodes(self):
        """
        Check which items must be removed or added
        to the selection list and emit the proper signals
        """
        for episode in self._episodes:
            allowed = self._checkAgainstCriteria(episode)
            if not allowed and episode in self._episodes:
                self._selection.remove(ep)
                Publisher().sendMessage(signals.EPISODE_DELETED, ep)
            if allowed and episode not in self._episodes:
                self._selection.append(ep)
                Publisher().sendMessage(signals.EPISODE_ADDED, ep)
                

    def _checkAgainstCriteria(self, episode):
        """
        Checks given serie against criteria, and returns True
        if we can keep or add it, false to delete it
        """
        if episode.series_id != self._selection_id:
            return False
            
        if episode._seen and self._show_only_unseen:
            return False
                                
        return True
                