#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

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

def getPrioFromURL(url):
    """
    Returns priority of the URL ranked by most reliability
    The lower the number, the better confidence 
    """
    if url.startswith("http://www.tv.com"):
        return 1
    elif url.startswith("http://epguides.com"):
        return 2
    return 0
    

class SeriesQueueItem(object):
    def __init__(self, series_id, series_name, series_url):
        self.id = series_id
        self.name = series_name
        self.url = series_url
        self.episodes = list()
        self.manual = False
        self.errors = False
        self.error_str = ''
        
    def setError(self, str):        
        if not self.errors:
            self.errors = True            
            self.error_str = str


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
        self._batchSize = 0              # a number how many items seen at once
        self._batch = list()
        self._currSize = 0               # use this for current size
        
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
            
            # first take a batch from the queue
            while not self.in_queue.empty():
                series = self.in_queue.get()
                self._batch.append(series)
            if self._batchSize < len(self._batch):
                self._batchSize = len(self._batch)
                
            # process the batch one at the time
            while len(self._batch) > 0 and not self.stop:
                self._is_downloading = True
                series = self._batch[0]
                del self._batch[0]
                self._currSize = len(self._batch)
                self.__report("Processing series '%s' ..." % series.name)
                self._current_series = series.name
                
                # do all URL's 
                for url in series.url:
                    url = url.strip()
                    if url:
                        # TODO: More intelligent gathering mechanism
                        cmd = None
                        if url.startswith("http://www.tv.com"):
                            cmd = series_getter.TvComSeriesDownloadCmd(self.msg_queue, series, url)
                        elif url.startswith("http://epguides.com") or url.startswith("http://www.epguides.com"):
                            cmd = series_getter.EpGuidesSeriesDownloadCmd(self.msg_queue, series, url)
        
                        if cmd:                            
                            cmd.retrieve()
                            
                            self._current_series = ''
                            
                            # in case of errors
                            if series.errors:
                                self.__report("ERROR: %s" % series.error_str)

                            epcount = len(series.episodes)
                            if epcount > 0:
                                self.__report("Retrieved %d episodes for series '%s'" % \
                                              (epcount, series.name))
                                self.out_queue.put( series )
                        else:
                            self.__report("ERROR: Unknown series url to process: %s" % url)
                            
            self._batchSize = 0
            self._currSize = 0
            self._is_downloading = False
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


    def getProgress(self):
        """
        Returns a tuple that reports the batch size and the current size
        """
        return (self._batchSize, self._currSize)