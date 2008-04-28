#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

from storm.locals import *
from storm.locals import SQL
import datetime

EP_NEW         = 0
EP_TO_DOWNLOAD = 1
EP_DOWNLOADING = 2
EP_READY       = 3
EP_PROCESSED   = 4

#
# Module that contains functionality
# to store a number of series and functionality
#

def _convertDate(datestr):
    if datestr:
        try:
            dy = int(datestr[6:])
            mn = int(datestr[4:6])
            yr = int(datestr[0:4])
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
        if self.update_period == None:
            self.update_period = 0
    
    
    def setLastUpdate(self, d = None):
        if d:
            self.last_update = unicode("%04i%02i%02" % (d.year, d.month, d.day))
        else:
            self.last_update = unicode(datetime.date.today().strftime("%Y%m%d"))    
    
            
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
    last_update = Unicode()       # last update
    status = Int()                # status of episode
    changed = Int()
    series_id = Int()             # id of series table entry
        
    def __init__(self):
        self.title = u""
        self.number = u""
        self.season = u""
        self.aired = u""
        self.last_update = u""
        self.status = EP_READY
        self.changed = 0 
            

    def setAired(self, d):
        """
        Sets date
        """
        if d:
            self.aired = unicode("%04i%02i%02" % (d.year, d.month, d.day))
        else:
            self.aired = unicode('')
    
    def setLastUpdate(self, d = None):
        """
        Sets date
        """
        if d:
            self.last_update = unicode("%04i%02i%02" % (d.year, d.month, d.day))
        else:
            self.last_update = unicode(datetime.date.today().strftime("%Y%m%d"))
          
    def getStrDate(self):
        if len(self.aired) > 7:
            s = self.aired
            return "%s-%s-%s" % (s[0:4], s[4:6], s[6:8])
        return ''
    
                    
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
    