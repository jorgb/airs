#
# Series Getter Module
# --------------------
# This module processes a list of URL's from TV.com and returns a list of series per
# URL that are displayed on the site.
#

from threading import Thread
from Queue import Queue

class SeriesRetriever(Thread):
    """
    Thread that retrieves series from tv.com site
    """

    def __init__ (self):
        Thread.__init__(self)

        pass
        
    # --------------------------------------------------------------------------
    def run(self):
        """
        Runs the file scan, all files that are found are sent to the main
        window to populate the list
        """
        pass
