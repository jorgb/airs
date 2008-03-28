#
# Series Getter Module
# --------------------
# This module processes a list of URL's from TV.com and returns a list of series per
# URL that are displayed on the site.
#

from threading import Thread
from Queue import Queue
import time
from series_getter import TvComSeriesDownloadCmd


class SeriesRetrieveThread(Thread):
    """
    Thread that retrieves series from tv.com site
    """

    def __init__ (self):
        Thread.__init__(self)
        self.in_queue = Queue()          # process series command
        self.out_queue = Queue()         # return retrieved series
        self.msg_queue = Queue()         # diagnostics messages
        self.stop = False
        self._is_downloading = False
        
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
        
        while not self.stop:
            
            # process stuff here
            if not self.in_queue.empty():
            
                job = self.in_queue.get()
                
                self.__report("Processing series '%s' ..." % job[0])

                self._is_downloading = True
                
                cmd = TvComSeriesDownloadCmd(self.msg_queue, job[0], job[1])
                items = cmd.retrieve()
                
                self._is_downloading = False
                
                # in case of errors
                if items[0] == None:
                    self.__report("ERROR: %s" % item[1])
                else:
                    series_list = items[0]
                    self.__report("Downloaded series data for '%s'" % job[0])
                    for serie in series_list:
                        # send back: serie ID, serie episode nr, serie title
                        self.out_queue.put( (job[0], serie[0], serie[1]) )
            time.sleep(0.2)
        
        self.__report('Series retrieve thread stopped')


    def is_downloading(self):
        return self._is_downloading