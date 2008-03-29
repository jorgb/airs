import os
import os.path

import wx
from wx.lib.pubsub import Publisher
from data.series_list import SeriesList
from data.series_queue import SeriesRetrieveThread
from data.series_filter import SeriesSelectionList
import signals

# Signals constants are used in the view manager (and the rest of the 
# application to send around changes in the application.

is_closing = False
retriever = None
series_list = None
series_sel = None

#===============================================================================

# All actions that the viewmanager can do are defined here. These actions can
# be called in the application to send around certain events

def app_init():
    """
    Initialize all singleton and data elements of viewmgr
    """
    global retriever, series_list, series_sel
    
    series_list = SeriesList()
    series_sel = SeriesSelectionList()

    retriever = SeriesRetrieveThread()
    Publisher().sendMessage(signals.APP_INITIALIZED)
    retriever.start()
    
    
def app_close():
    """ 
    Sends a signal that closes the application. If the QueryResult object
    is set to veto the closure, the final signal is not sent
    """
    global is_closing
    
    is_closing = False
    res = signals.QueryResult()
    Publisher().sendMessage(signals.QRY_APP_CLOSE, res)
    if res.allowed():
        is_closing = True
        Publisher.sendMessage(signals.APP_CLOSE)
    return res.allowed()
    

def app_settings_changed():
    """
    Call this to send a signal that informs all the views that the 
    application settings are changed. Every view using these settings 
    should investigate if their view needs to be updated
    """
    Publisher().sendMessage(signals.APP_SETTINGS_CHANGED)
    
    
def app_restore():
    """
    Sends a signal that the application needs to restore it's window
    """
    Publisher().sendMessage(signals.APP_RESTORE)
    
    
def app_log(msg):
    """
    Sends a log message to the listeners
    """
    Publisher().sendMessage(signals.APP_LOG, msg)


def get_all_series():
    """ 
    Initializes the transfer to send all the serie jobs to the 
    receive thread, and after that, hopefully results will 
    come back
    """
    Publisher().sendMessage(signals.APP_LOG, "Sending all series to Series Receive thread...")
    
    # some dummy series
    series = [ ("Supernatural", "http://www.tv.com/supernatural/show/30144/summary.html"),
               ("Prison Break", "http://www.tv.com/prison-break/show/31635/summary.html") ]
    
    for serie in series:
        retriever.in_queue.put(serie)


def probe_series():
    """
    Probes if there are more series. If there are series left to process,
    the series list is updated, and the appropiate signals are sent out to
    display them. This is done in the main (GUI) thread because there are
    signals involved.
    """
    
    while not retriever.out_queue.empty():
        series = retriever.out_queue.get()
        
        ep = series_list.addEpisode(series[0], series[1], series[2])
        series_sel.addEpisode(ep)
        
        
def is_busy():
    """
    Returns true when
    1) Thread is busy downloading
    2) In queue of retriever is not empty
    3) Out queue of retriever is not empty
    """
    return (not retriever.in_queue.empty()) or (not retriever.out_queue.empty()) or \
           retriever.is_downloading()


def get_current_title():
    """
    Returns current title that is downloaded (if any)
    potentially thread unsafe but it is only a read
    action so the risk is low
    """
    return retriever.getCurrentSeries()


def app_destroy():
    """
    Close down thread
    """
    retriever.stop = True
    retriever.join(2000)
    