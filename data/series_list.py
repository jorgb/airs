#
# Module that contains functionality
# to store a number of series and functionality
#

class SerieEpisode(object):
    """
    Serie episode item
    """
    def __init__(self, parent, ep_nr, ep_title):
        self._ep_nr = ep_nr
        self._ep_title = ep_title
        self._series = parent
        self._seen = False
 

class SeriesEpisodes(object):
    """
    List of episodes manager
    """
    def __init__(self, serie_name):
        # serie item data
        self._serie_name = serie_name
        self._episodes = dict()
        self._link = ''
        
        
    def addEpisode(self, ep_nr, ep_title):
        """
        Add episode to to list of episodes 
        """
        if ep_nr not in self._episodes:
            ep = SerieEpisode(self, ep_nr, ep_title)
            self._episodes[ep_nr] = ep
        else:
            ep = self._episodes[ep_nr]
        
        return ep
            
            
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
            
            
    def addSeries(self, serie_id):
        """
        Adds the series only, returns a series object 
        if the series is actually added it emits a signal else
        it will only return a reference
        """
        sid = serie_id.lower()
        if sid not in self._series:
            seps = SeriesEpisodes(serie_id)
            self._series[sid] = seps
        else:
            seps = self._series[sid]
        
        return seps
    