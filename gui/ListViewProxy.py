#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

from wx.lib.pubsub import Publisher
from data import signals

class ListViewProxy(object):
    def __init__(self, views):
        self._currView = None
        self._views = views

        Publisher().subscribe(self._onEpisodeAdded, signals.EPISODE_ADDED)
        Publisher().subscribe(self._onEpisodeDeleted, signals.EPISODE_DELETED)
        Publisher().subscribe(self._onEpisodeUpdated, signals.EPISODE_UPDATED)
        Publisher().subscribe(self._onClearAll, signals.EPISODES_CLEARED)
        
    
    def setView(self, viewname):
        """
        Sets the view to a specific listctrl, and makes sure
        that the other listctrl's are cleared.
        """
        if viewname in self._views:
            # first clear the current view
            if self._currView != self._views[viewname] and self._currView != None:
                self._currView.clear()
            
            # set the new view
            self._currView = self._views[viewname]
            print "set view"
            

    def _onEpisodeAdded(self, msg):
        if self._currView:
            self._currView.add(msg.data)
            

    def _onEpisodeDeleted(self, msg):
        if self._currView:
            self._currView.delete(msg.data)
            
            
    def _onEpisodeUpdated(self, msg):
        if self._currView:
            self._currView.update(msg.data)
    
            
    def _onClearAll(self, msg):
        if self._currView:
            self._currView.clear()
        