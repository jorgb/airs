import os
import os.path
import sys

import wx
from wx.lib.pubsub import Publisher
import series_queue
from series_filter import SeriesSelectionList
#from storage import series_list_xml
import series_list
import signals
import appcfg
import db

# Signals constants are used in the view manager (and the rest of the 
# application to send around changes in the application.

is_closing = False
retriever = None
_series_sel = SeriesSelectionList()

#===============================================================================

# All actions that the viewmanager can do are defined here. These actions can
# be called in the application to send around certain events

def app_init():
    """
    Initialize all singleton and data elements of viewmgr
    """
    global retriever, _series_sel

    # set up classes
    retriever = series_queue.SeriesRetrieveThread()
    
    # initialize / create database
    dbfile = os.path.join(wx.StandardPaths.Get().GetUserDataDir(), 'series.db')
    db.init(dbfile)
    
    # finish work
    _series_sel._show_only_unseen = appcfg.options[appcfg.CFG_SHOW_UNSEEN]
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
    

def add_series(series):
    """ 
    Add this new series object to the database, and emit signal that
    other views can also append it to the list
    """
    db.store.add(series)
    db.store.commit()
    
    Publisher().sendMessage(signals.SERIES_ADDED, series)

    # now, if not selected, select this one
    if _series_sel._selection_id == -1:
        set_selection(series)
        
    
def app_settings_changed():
    """
    Call this to send a signal that informs all the views that the 
    application settings are changed. Every view using these settings 
    should investigate if their view needs to be updated
    """
    _series_sel._show_only_unseen = appcfg.options[appcfg.CFG_SHOW_UNSEEN]
    _series_sel.syncEpisodes()
    
    Publisher().sendMessage(signals.APP_SETTINGS_CHANGED)
    
    
def set_selection(series):
    """
    Select the series that is given here
    """
    Publisher().sendMessage(signals.SERIES_SELECT, series)
    if series:
        sel_id = series.id
    else:
        sel_id = -1
    _series_sel.setSelection(sel_id)
    
    
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
    
    # send all series from db to the receive queue
    result = db.store.find(series_list.Series)
    all_series = [ series for series in result.order_by(series_list.Series.name) ]
    for series in all_series:
        # we have to decouple the series object (due to multi threading issues)
        item = series_queue.SeriesQueueItem(series.id, series.name, series.url)
        retriever.in_queue.put( item )


def probe_series():
    """
    Probes if there are more series. If there are series left to process,
    the series list is updated, and the appropiate signals are sent out to
    display them. This is done in the main (GUI) thread because there are
    signals involved.
    """
    
    # cache list with ID of series as lookup
    # we use this to verify the series is present 
    series_cache = []
    db_changed = False
    
    while not retriever.out_queue.empty():
        episode = retriever.out_queue.get()
        
        
        # for every episode, check if it exists in the DB. If it does 
        # attempt an update. If it doesn't, we add it. We use the 
        # follow up number (which is mandatory) for identification
        if not episode.number:
            continue
            
        nr = str(episode.number)
        result = db.store.find(series_list.Episode, (series_list.Episode.number == unicode(nr)),
                                                    (series_list.Episode.series_id == episode.series_id)).one()
        if not result:
            # not found, add to database, perform extra check for integrity
            can_add = episode.series_id not in series_cache
            if not can_add:
                series = db.store.find(series_list.Series, series_list.Series.id == episode.series_id).one()
                if series:
                    series_cache.append(series.id)
                    can_add = True
            
            if can_add:
                episode.last_in = 1
                db.store.add(episode)
                db_changed = True
                db.store.flush()
                _series_sel.add_episode(episode)
        else:
            # we found the episode, we will update only certain parts
            # if they are updated properly, we willl inform and update the DB
            updated = False
            if not result.title and episode.title != '':
                result.title = unicode(episode.title)
                updated = True
            if episode.season:
                result.season = unicode(episode.season)
                updated = True
            if episode.aired:
                result.aired = unicode(episode.aired)
                updated = True
                
            if updated:
                db_changed = True
                result.last_in = 1
                _series_sel.update_episode(episode)
                db.store.flush()

    # all changes are committed here
    if db_changed:
        db.store.commit()
        
        
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
        
    db.close()
        
        
def attach_series(series):
    """
    Attaches series to the big list, and when all is well, emit a restored
    signal so it gets added to the proper lists 
    """
    
    raise Exception("Fout")
    
    #sid = series._serie_name.lower()
    #if sid not in _series_list._series:
    #    _series_list._series[sid] = series
    #    Publisher().sendMessage(signals.DATA_SERIES_RESTORED, series)
        
    
def get_selected_series():
    """
    Determine selected series, get that one or else get all
    """
    series = db.store.get(series_list.Series, _series_sel._selection_id)
    if series:
        item = series_queue.SeriesQueueItem(series.id, series.name, series.url)
        retriever.in_queue.put(item)
    
    
def delete_series(series):
    """
    Delete the series from all lists and let the GUI update
    itself.
    """

    if not retriever.present(series):    
        if series.id == _series_sel._selection_id:        
            # select a different series first
            result = db.store.find(series_list.Series)
            slist = [serie for serie in result.order_by(series_list.Series.name)]
            
            # TODO: In future maybe select previous or next in line
            # instead of first of the list
            if len(slist) > 1:        
                for ser in slist:
                    if ser.id != series.id:
                        set_selection(ser)
                        break
            else:
                set_selection(None)
                
        # first delete all episodes belonging to series
        result = db.store.find(series_list.Episode, series_list.Episode.series_id == series.id)
        for episode in result:
            db.store.remove(episode)
            # TODO: it is debatable if a signal needs to be sent
            Publisher.sendMessage(signals.EPISODE_DELETED, episode)
                
        db.store.remove(series)    
        db.store.commit()
        
        Publisher().sendMessage(signals.SERIES_DELETED, series)
    

def update_series(series):
    """
    Update the series in the database and issue an update 
    command
    """
    
    db.store.flush()
    db.store.commit()
    Publisher().sendMessage(signals.SERIES_UPDATED, series)
    
    
def episode_updated(episode):
    """
    Episode is updated, let's resync the filter
    """
    
    # go through all episodes again and see if we missed
    # out on something after this update
    # TODO: Could be more optimized by only evaluating this episode
    _series_sel.update_episode(episode)
    
    
def _do_clear_cache(series):
    """
    Internal function to clear cache of series
    e.g. wipe all episodes
    """
    series._episodes = dict()
    _series_sel.deleteSeries(series)
        

def clear_current_cache():
    """ 
    Clear all or some series
    """
    if _series_sel._crit_selection:
        series = _series_list._series[_series_sel._crit_selection]
        _do_clear_cache(series)
    else:
        for series in _series_list._series.itervalues():
            _do_clear_cache(series)

