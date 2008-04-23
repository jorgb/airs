#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================
#
# Module that manages a selection list object
# which will send out signals if the criteria
# for the list changes
#

from wx.lib.pubsub import Publisher
import datetime
import signals
import series_list
import db

# this filter has effect only in the UPDATED view

SHOW_ALL      = 0        # show all series (undated episodes as well)
SHOW_UPCOMING = 1        # show upcoming (only upcoming and lower)
SHOW_AIRED    = 2        # show all aired but not undated or upcoming

VIEW_WHATS_NEW   = 0
VIEW_WHATS_ON    = 1
VIEW_TO_DOWNLOAD = 2
VIEW_DOWNLOADING = 3
VIEW_SERIES      = 4

class SeriesSelectionList(object):
    def __init__(self):
        self._selection = dict()

        # selection criteria for the series ID. If an ID is selected
        # all episodes belonging to a different series are removed
        self._selected_series_id = -1
        self._update_mode = SHOW_ALL
        self._view_type = VIEW_WHATS_ON
        
        self._show_only_unseen = False
        self._today = datetime.date.today().strftime("%Y%m%d")
        
        
    def setView(self, viewtype):
        """
        Sets a certain view. Will trigger a resync for episodes. 
        """
        #if self._view_type != viewtype:
        self._view_type = viewtype
        # clear all series
        self._selection = dict()
        Publisher().sendMessage(signals.EPISODES_CLEARED)
        # reload eps and fill
        self.syncEpisodes()
        

    def setSelection(self, sel_id):
        """
        Sets the ID of the selection. This will trigger an episodes
        restore and an update of the view filter
        """
        # only clear list when the series view is active
        if self._view_type == VIEW_SERIES:
            print "set selection"
            if self._selected_series_id != sel_id:
                self._selection = dict()
                Publisher().sendMessage(signals.EPISODES_CLEARED)
            self._selected_series_id = sel_id
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
        self._today = datetime.date.today().strftime("%Y%m%d")
        
        if self._selection:
            episodes = [episode for episode in self._selection.itervalues()]
            for episode in episodes:
                self.filterEpisode(episode)

        # reset the DB selection    
        if self._view_type == VIEW_WHATS_NEW:
            # we restore all episodes that are last updated
            result = db.store.find(series_list.Episode, 
                                   series_list.Episode.changed != 0)
        elif self._view_type == VIEW_TO_DOWNLOAD:
            # we restore all episodes that are queued
            result = db.store.find(series_list.Episode, 
                                   series_list.Episode.status == series_list.EP_TO_DOWNLOAD)
        elif self._view_type == VIEW_DOWNLOADING:
            # we restore all episodes that are queued
            result = db.store.find(series_list.Episode, 
                                   series_list.Episode.status == series_list.EP_DOWNLOADING)
        elif self._view_type == VIEW_WHATS_ON:
            # we restore all episodes that are last updated
            result = db.store.find(series_list.Episode, 
                                   series_list.Episode.aired != unicode(""),
                                   series_list.Episode.aired <= unicode(self._today))
            # narrow list
            result = [ ep for ep in result if ep.status != series_list.EP_PROCESSED and \
                                              ep.status != series_list.EP_TO_DOWNLOAD and \
                                              ep.status != series_list.EP_DOWNLOADING ]
            
            
        else:
            # restore the episode list belonging to this series_id
            # TODO: Add filter criteria that narrows the selection being
            # returned (e.g. if there are seen items and the filter is 
            # set to hide these items)
            result = db.store.find(series_list.Episode, 
                                   series_list.Episode.series_id == self._selected_series_id)
                        
        # resync for adding new items        
        episodes = [episode for episode in result]
        max = 100
        for episode in episodes:
            self.filterEpisode(episode)
            max -= 1
            if max <= 0:
                break
                
                
    def _checkAgainstCriteria(self, episode):
        """
        Checks given serie against criteria, and returns True
        if we can keep or add it, false to delete it
        """        
        
        # if we are in update mode, perform other logic
        if self._view_type == VIEW_WHATS_NEW and episode.changed != 0:
            return True
            
        if self._view_type == VIEW_WHATS_ON and \
           (episode.aired == "" or episode.aired > self._today):
            return False
           
        if self._view_type == VIEW_TO_DOWNLOAD and \
           episode.status != series_list.EP_TO_DOWNLOAD:
            return False
            
        if self._view_type == VIEW_DOWNLOADING and \
           episode.status != series_list.EP_DOWNLOADING:
            return False

        if self._view_type == VIEW_SERIES and \
           (episode.series_id != self._selected_series_id or \
            self._selected_series_id == -1):
            return False
    
        return True
