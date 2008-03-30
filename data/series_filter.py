#
# Module that manages a selection list object
# which will send out signals if the criteria
# for the list changes
#

from wx.lib.pubsub import Publisher
import signals
import series_list

class SeriesSelectionList(object):
    def __init__(self):
        self._episodes = list()
        self._selection = list()
        # selection criteria for the series ID. If an ID is selected
        # all episodes belonging to a different series are removed
        self._crit_selection = ''
        
        
    def addEpisode(self, episode):
        """
        Adds episode to the list, and sync the selection list
        if the episode matches the criteria
        """
        if episode not in self._episodes:
            self._episodes.append(episode)
            if self._checkAgainstCriteria(episode):
                self._selection.append(episode)
                Publisher().sendMessage(signals.EPISODE_ADDED, episode)
       
                
    def syncEpisodes(self):
        """
        Check which items must be removed or added
        to the list and emit the proper signals
        """
        for ep in self._episodes:
            allowed = self._checkAgainstCriteria(ep)
            if not allowed and ep in self._selection:
                self._selection.remove(ep)
                Publisher().sendMessage(signals.EPISODE_DELETED, ep)
                continue
            if allowed and not ep in self._selection:
                self._selection.append(ep)
                Publisher().sendMessage(signals.EPISODE_ADDED, ep)
                
        
    def _checkAgainstCriteria(self, episode):
        """
        Checks given serie against criteria, and returns True
        if the serie matches the episode
        """
        # return true when no series is filtered
        if not self._crit_selection:
            return True
        
        # if the series ID is set, check against the ID
        if self._crit_selection == episode._series._serie_name.lower():
            return True
        
        return False