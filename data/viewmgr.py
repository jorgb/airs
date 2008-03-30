import os
import os.path
import sys

import wx
from wx.lib.pubsub import Publisher
from series_list import SeriesList
from series_queue import SeriesRetrieveThread
from series_filter import SeriesSelectionList
from storage import series_list_xml
import signals

# Signals constants are used in the view manager (and the rest of the 
# application to send around changes in the application.

is_closing = False
retriever = None
_series_list = None
series_sel = None

#===============================================================================

# All actions that the viewmanager can do are defined here. These actions can
# be called in the application to send around certain events

def app_init():
    """
    Initialize all singleton and data elements of viewmgr
    """
    global retriever, _series_list, series_sel
    
    datafile = os.path.join(wx.StandardPaths.Get().GetUserDataDir(), 'series.xml')
    try:
        _series_list = series_list_xml.read_series(datafile)
    except series_list_xmlSerieListXmlException, msg:
        wx.LogError(msg)
        sys.exit(1)
        
    retriever = SeriesRetrieveThread()
    series_sel = SeriesSelectionList()

    # go through all the series, and append them to the 
    # view filter selection class so we update the GUI
    for series in _series_list._series.values():
        for ep in series._episodes.values():
            series_sel.addEpisode(ep)
    
    retriever.start()
    
    # send signal to listeners telling the data is ready
    Publisher().sendMessage(signals.APP_INITIALIZED)
    
    
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
    
    # send series to the receive queue
    for series in _series_list._series.itervalues():
        retriever.in_queue.put( (series._serie_name, series._link) )


def probe_series():
    """
    Probes if there are more series. If there are series left to process,
    the series list is updated, and the appropiate signals are sent out to
    display them. This is done in the main (GUI) thread because there are
    signals involved.
    """
    
    while not retriever.out_queue.empty():
        series = retriever.out_queue.get()
        
        ep = _series_list.addEpisode(series[0], series[1], series[2])
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
    Close down thread, save changes
    """
    
    retriever.stop = True
    retriever.join(2000)

    datafile = os.path.join(wx.StandardPaths.Get().GetUserDataDir(), 'series.xml')
    try:
        series_list_xml.write_series(datafile, _series_list)
    except series_list_xml.SerieListXmlException, msg:
        wx.LogError(msg)
        
        
def attach_series(series):
    """
    Attaches series to the big list, and when all is well, emit a restored
    signal so it gets added to the proper lists 
    """
    
    sid = series._serie_name.lower()
    if sid not in _series_list._series:
        _series_list._series[sid] = series
        Publisher().sendMessage(signals.DATA_SERIES_RESTORED, series)
        

def select_series(series):
    """
    Select a series and update the viewfilter
    """
    if series:
        series_sel._crit_selection = series._serie_name.lower()
    else:
        series_sel._crit_selection = ''
    series_sel.syncEpisodes()

    
def get_selected_series():
    """
    Determine selected series, get that one or else get all
    """
    try:
        series = _series_list._series[series_sel._crit_selection]
    except KeyError:
        get_all_series()
        return
    
    retriever.in_queue.put( (series._serie_name, series._link) )
    
    
def delete_series(series):
    """
    Delete the series from all lists and let the GUI update
    itself.
    """
    
    sid = series._serie_name.lower()
    if sid in _series_list._series:
        del _series_list._series[sid]
    
    series_sel.deleteSeries(series)

    Publisher().sendMessage(signals.SERIES_DELETED, series)
    