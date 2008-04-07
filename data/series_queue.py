#
# Series Getter Module
# --------------------
# This module processes a list of URL's from TV.com and returns a list of series per
# URL that are displayed on the site.
#

from threading import Thread
from Queue import Queue
import time
import series_getter


class SeriesQueueItem(object):
    def __init__(self, series_id, series_name, series_url):
        self.id = series_id
        self.name = series_name
        self.url = series_url


class SeriesRetrieveThread(Thread):
    """
    Thread that retrieves series from tv.com site
    """

    def __init__ (self):
        Thread.__init__(self)
        self.in_queue = Queue()          # process SeriesQueueItem
        self.out_queue = Queue()         # return retrieved series
        self.msg_queue = Queue()         # diagnostics messages
        self.stop = False
        self._is_downloading = False
        self._current_series = ""
        
        self.__report('Series retrieve thread initialized...')
        pass
        

    def __report(self, msg):
        """
        Log a message back. Ideally we should logging module for this with
        redirecting, but I could not find a suitable method for this yet
        """
        self.msg_queue.put(msg)
    
    
    def run(self):
        """
        Runs the file scan, all files that are found are sent to the main
        window to populate the list
        """
        self.__report("Series retrieve thread started")
        
        # process stuff here
        while not self.stop:
            if not self.in_queue.empty():
            
                series = self.in_queue.get()
                
                self.__report("Processing series '%s' ..." % series.name)
                self._current_series = series.name
                self._is_downloading = True
                
                # TODO: More intelligent gathering mechanism
                if series.url.startswith("http://www.tv.com"):
                    cmd = series_getter.TvComSeriesDownloadCmd(self.msg_queue, series)
                else:
                    cmd = series_getter.EpGuidesSeriesDownloadCmd(self.msg_queue, series)

                items = cmd.retrieve()
                
                self._is_downloading = False
                self._current_series = ''
                
                # in case of errors
                if items[0] == None:
                    self.__report("ERROR: %s" % items[1])
                else:
                    episode_list = items[0]
                    self.__report("Downloaded %d episodes for series '%s'" % \
                                  (len(epsiode_list), series.name))
                    for episode in series_list:
                        self.out_queue.put( episode )
            time.sleep(0.2)
        
        self.__report('Series retrieve thread stopped')


    def is_downloading(self):
        return self._is_downloading
    
    
    def getCurrentSeries(self):
        """
        Returns the series being downloaded or an empty
        string if none
        """
        return self._current_series

    