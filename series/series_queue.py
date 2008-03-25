#
# Series Getter Module
# --------------------
# This module processes a list of URL's from TV.com and returns a list of series per
# URL that are displayed on the site.
#

from threading import Thread
from Queue import Queue
import time


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
                self.in_queue.task_done()

                # TODO: Get the series
                # TODO: Return the result
                
            time.sleep(0.2)
            
        self.__report('Series retrieve thread stopped')

        