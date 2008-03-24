#
# Series Getter Module
# --------------------
# This module processes a list of URL's from TV.com and returns a list of series per
# URL that are displayed on the site.
#

from threading import Thread
from Queue import Queue
import logging
import time
import BeautifulSoup as soup
import urllib2

class SeriesRetriever(Thread):
    """
    Thread that retrieves series from tv.com site
    """

    def __init__ (self):
        Thread.__init__(self)
        self.in_queue = Queue()
        self.out_queue = Queue()
        self.stop = False
        logging.info('Series retrieve thread initialized')
        pass
        

    
    def run(self):
        """
        Runs the file scan, all files that are found are sent to the main
        window to populate the list
        """
        logging.info('Series retrieve thread started')
        while not self.stop:
            # process stuff here
            if not self.in_queue.empty():
            
                job = self.in_queue.get()
                self.in_queue.task_done()

                logging.info('Hooray, I got a job to process!')
                
                result = self._getSeriesList(job)
                self.out_queue.put(result)            
            
            time.sleep(0.2)
            
        logging.info('Series retrieve thread stopped')


    def _composeResult(self, series_id, series, errstr = ''):
        """
        Composes the series struct, if errstr is not empty it will return an 
        empty list with the error string as result.
        Format:
                (series_id, series_lst, error_msg)
                
                series_lst: [ (Episode Number, Episode Name), 
                               ...... ] or None if error
        """
        if errstr:
            result_lst = []
        else:
            result_lst = series
        
        return (series_id, result_lst, errstr)
        
    
        
    def _getSeriesList(self, job):
        """
        Downloads the link, processes the series, and if succesful, returns a list 
        of items that are found 
        """

        logging.info("Attempting open url '%s' for series '%s'" % (job[1], job[0])) 
        
        try:
            f = urllib2.urlopen(job[1])
            logging.info("Opened URL ... ") 
        except URLError, msg:
            errmsg = "Can't open the URL : %s" % msg
            logging.error(errmsg)
            return self._composeResult(job[0], None, errmsg)
        
        # if no file like object was opened
        if not f:
            msg = "No handle received to URL : %s" % job[1]
            logging.error(msg)
            return self._composeResult(job[0], None, msg)
        
        # read the contents
        serie = f.read()
        
        logging.info("Story continues ...")
        return self._composeResult(job[0], None, 'Not yet finished')