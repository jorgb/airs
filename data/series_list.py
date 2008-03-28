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
 

class SeriesEpisodes(object):
    """
    List of episodes manager
    """
    def __init__(self, serie_name):
        # serie item data
        self._serie_name = serie_name
        self._episodes = dict()
        
        
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
        sid = serie_id.lower()
        if sid not in self._series:
            seps = SeriesEpisodes(serie_id)
            self._series[sid] = seps
        else:
            seps = self._series[sid]
            
        return seps.addEpisode(episode_nr, episode_title)
            
            
    
    