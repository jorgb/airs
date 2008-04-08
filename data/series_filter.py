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
        self._selection = dict()

        # selection criteria for the series ID. If an ID is selected
        # all episodes belonging to a different series are removed
        # if id is -1, the last updated list is shown
        self._selection_id = -1
        self._show_only_unseen = False
        
    
    def setSelection(self, sel_id):
        """
        Sets the ID of the selection. This will trigger an episodes
        restore and an update of the view filter
        """
        if self._selection_id != sel_id:
            self._selection_id = sel_id
            
            self.syncEpisodes()
                
        
    def filterEpisode(self, episode, updated = False):
        """
        Check the episode with the current criteria,
        and update the selection list to add / delete 
        or update it
        """
        allowed = self._checkAgainstCriteria(episode)
        if allowed and episode.id in self._selection:
            if updated:
                self._selection[episode.id] = episode
                Publisher().sendMessage(signals.EPISODE_UPDATED, episode)
        elif not allowed and episode.id in self._selection:
            del self._selection[episode.id]
            Publisher().sendMessage(signals.EPISODE_DELETED, episode)
        elif allowed and episode.id not in self._selection:
            self._selection[episode.id] = episode        
            Publisher().sendMessage(signals.EPISODE_ADDED, episode)
        
          
    def delete_episode(self, episode):
        """
        Deletes episode from list if present, this forces the
        delete probably when a delete occurs in the database
        """
        if episode.id in self._selection:
            del self._selection[episode.id]
            Publisher().sendMessage(signals.EPISODE_DELETED, episode)
                          

    def syncEpisodes(self):
        """
        Check which items must be removed or added
        to the selection list and emit the proper signals
        """
        # first filter out all unwanted
        episodes = [episode for episode in self._selection.itervalues()]
        for episode in episodes:
            self.filterEpisode(episode)

        # reset the DB selection    
        if self._selection_id != -1:
            # restore the episode list belonging to this series_id
            result = db.store.find(series_list.Episode, 
                                   series_list.Episode.series_id == self._selection_id)
            episodes = [episode for episode in result]
        else:
            # we restore all episodes that are last updated
            result = db.store.find(series_list.Episode, 
                                   series_list.Episode.last_in != 0)
            episodes = [episode for episode in result]
            
        # resync for adding new items        
        for episode in episodes:
            self.filterEpisode(episode)
                
                
    def _checkAgainstCriteria(self, episode):
        """
        Checks given serie against criteria, and returns True
        if we can keep or add it, false to delete it
        """        
        
        if (episode.last_in == 0 and self._selection_id == -1):
            return False
        
        if self._selection_id != -1:
            if (episode.series_id != self._selection_id):
                return False
            
        if episode.seen != 0 and self._show_only_unseen:
            return False
                                
        return True
                