import os
import os.path

import wx
from wx.lib.pubsub import Publisher
from gui import appcfg
from series.series_queue import SeriesRetrieveThread

# Signals constants are used in the view manager (and the rest of the 
# application to send around changes in the application.

is_closing = False
retriever = None

# signal that tells the application is initialized
SIGNAL_APP_INITIALIZED      = ('app', 'initialized')  
# query signal to allow application to veto the close event
SIGNAL_QRY_APP_CLOSE        = ('query', 'app', 'close')  
# final signal that app closes, the destroy follows after this event
SIGNAL_APP_CLOSE            = ('app', 'close')  
# signal to restore the application window
SIGNAL_APP_RESTORE          = ('app', 'restore')
SIGNAL_APP_SETTINGS_CHANGED = ('app', 'settings', 'changed')
# log signal that a message must be processed
SIGNAL_APP_LOG              = ('app', 'logging')

class QueryResult(object):
    """
    This class is designed to act as a reference object. If a signal is
    sent with this QueryResult object as data member, a listener can 
    veto the action by calling deny(). Calling allow() will allow the 
    action, but it will only set the flag to true if no others have denied it 
    """
    def __init__(self, allow = True):
        self._result = allow
        self._denied = False

    def allowed(self):
        """ Return true when the action is allowed """
        return self._result

    def deny(self):
        """ Set the result to False """
        self._result = False
        self._denied = True

    def allow(self):
        """ Set the result to True but only if none others have denied it """
        if not self._denied:
            self._result = True


#===============================================================================

# All actions that the viewmanager can do are defined here. These actions can
# be called in the application to send around certain events

def app_init():
    """
    Initialize all singleton and data elements of viewmgr
    """
    global retriever
    retriever = SeriesRetrieveThread()
    Publisher().sendMessage(SIGNAL_APP_INITIALIZED)
    retriever.start()
       
    
def app_close():
    """ 
    Sends a signal that closes the application. If the QueryResult object
    is set to veto the closure, the final signal is not sent
    """
    global is_closing
    
    is_closing = False
    res = QueryResult()
    Publisher().sendMessage(SIGNAL_QRY_APP_CLOSE, res)
    if res.allowed():
        is_closing = True
        Publisher.sendMessage(SIGNAL_APP_CLOSE)
        # cleanup thread
        if retriever.isAlive():
            retriever.stop = True
            retriever.join(4000)        
    
    return res.allowed()
    

def app_settings_changed():
    """
    Call this to send a signal that informs all the views that the 
    application settings are changed. Every view using these settings 
    should investigate if their view needs to be updated
    """
    Publisher().sendMessage(SIGNAL_APP_SETTINGS_CHANGED)
    
    
def app_restore():
    """
    Sends a signal that the application needs to restore it's window
    """
    Publisher().sendMessage(SIGNAL_APP_RESTORE)
    
    
def app_log(msg):
    """
    Sends a log message to the listeners
    """
    Publisher().sendMessage(SIGNAL_APP_LOG, msg)


def get_all_series():
    """ 
    Initializes the transfer to send all the serie jobs to the 
    receive thread, and after that, hopefully results will 
    come back
    """
    Publisher().sendMessage(SIGNAL_APP_LOG, "Sending all series to Series Receive thread...")
    
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
        
        # print for now
        app_log("Serie : '%s' (%s - %s)" % (series[0], series[1], series[2]))


def is_busy():
    """
    Returns true when
    1) Thread is busy downloading
    2) In queue of retriever is not empty
    3) Out queue of retriever is not empty
    """
    return (not retriever.in_queue.empty()) or (not retriever.out_queue.empty()) or \
           retriever.is_downloading()
