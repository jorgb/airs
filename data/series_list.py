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

def _convertDate(datestr):
    if datestr:
        try:
            dy = int(datestr[0:2])
            mn = int(datestr[3:5])
            yr = int(datestr[6:])
            if yr < 100:
                if yr < 99 and yr > 39:
                    yr = 1900 + yr
                else:
                    yr = 2000 + yr
            return date(yr, mn, dy)
        except ValueError:
            return None   
    else:
        return None


class Series(object):
    """
    List of episodes manager
    """
    __storm_table__ = "series"
    id = Int(primary = True)
    name = Unicode()
    url = Unicode()
    postponed = Int()
    last_update = Unicode()
    update_period = Int()       # in how many days later
    
    def __storm_loaded__(self):
        self._last_update = _convertDate(self.last_update)
        
    def __init__(self):
        self._last_update = None
        
        
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
    queued = Int()                # also listed in queue

    def __storm_loaded__(self):
        """
        Load hook used to convert the date to a 
        proper class
        """
        self.__date = _convertDate(self.aired)
        
    def __init__(self):
        self.title = u""
        self.number = u""
        self.season = u""
        self.aired = u""
        self.seen = 0
        self.last_in = 0
        self.__date = None
        self.queued = 0
        
    def getDate(self):
        """
        Returns date
        """
        if not self.__date and self.aired:
            self.__date = _convertDate(self.aired)
        return self.__date
    
    def setDate(self, d):
        """
        Sets date
        """
        self.__date = d
        if d:
            self.aired = unicode("%02i-%02i-%i" % (d.day, d.month, d.year))
        else:
            self.aired = unicode('')
    
    def getDateStr(self):
        d = self.getDate()
        if d:
            return "%02i-%02i-%i" % (d.day, d.month, d.year)
        else:
            return self.aired
            
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
    