#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

from storm.locals import *
from datetime import date

#
# Module that contains functionality
# to store a number of series and functionality
#

class Series(object):
    """
    List of episodes manager
    """
    __storm_table__ = "series"
    id = Int(primary = True)
    name = Unicode()
    url = Unicode()
    

class Episode(object):
    """
    Serie episode item
    """
    __storm_table__ = "episode"
    id = Int(primary = True)
    title = Unicode()             # title of episode
    number = Unicode()            # follow up number
    season = Unicode()            # season string e.g. (S01E01)
    aired = Unicode()             # date when aired
    seen = Int()                  # seen or not by the user
    last_in = Int()               # present in last update
    series_id = Int()             # id of series table entry

    def __init__(self):
        self.title = u""
        self.number = u""
        self.season = u""
        self.aired = u""
        self.seen = 0
        self.last_in = 0
        
    def getDate(self):
        """
        Returns date
        """
        if self.aired:
            try:
                dy = int(self.aired[0:2])
                mn = int(self.aired[3:5])
                yr = int(self.aired[6:])
                if yr < 100:
                    if yr < 99:
                        yr = 1900 + yr
                    else:
                        yr = 2000 + yr
            except ValueError:
                return None    
            return date(yr, mn, dy)
        return None
    
class SeriesList(object):
    """
    List of series collection manager 
    """
    def __init__(self):        
        # series dictionary
        self._series = dict()

        
    def addEpisode(self, serie_id, episode_nr, episode_title):
        """
        Adds an episode to the series list, if the series
        did not yet exist, a new one is added.
        """
        ser = self.addSeries(serie_id)
        return ser.addEpisode(episode_nr, episode_title)
            

    def attachEpisode(self, serie_id, episode):
        """
        Attach an episode only when the ID of the episode
        does not yet exist, else discard it
        """
        sid = serie_id.lower()
        if sid in self._series:
            return self._series[sid].attachEpisode(episode)
        
        return False
    
    
    def addSeries(self, serie_id):
        """
        Adds the series only, returns a series object 
        if the series is actually added it emits a signal else
        it will only return a reference
        """
        sid = serie_id.lower()
        if sid not in self._series:
            seps = Series(serie_id)
            self._series[sid] = seps
        else:
            seps = self._series[sid]
        
        return seps
    