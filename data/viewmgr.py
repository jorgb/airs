#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import os
import os.path
import sys

import wx
from wx.lib.pubsub import Publisher
import series_queue
from webserver import reactor
from series_filter import SeriesSelectionList
import series_filter
#from storage import series_list_xml
import series_list
import signals
import appcfg
import db
import datetime
import db_conv_xml

# Signals constants are used in the view manager (and the rest of the
# application to send around changes in the application.

is_closing = False
retriever = None
server = None
_series_sel = SeriesSelectionList()

# generic application state dictionary,
# used to set states in when parts of the GUI
# need to act upon other parts on the GUI
_pstates = [
             ("series_id",   -1),                     # id of selected series
             ("epcount",      0),                     # number of episodes selected
             ("lstcount",     0)                      # number of episodes in list
           ]

appstate = dict()
for pstate in _pstates:
    appstate[pstate[0]] = pstate[1]


# callback function to get selected episodes
_callbackGetSelectedEpisodes = None

#===============================================================================

# All actions that the viewmanager can do are defined here. These actions can
# be called in the application to send around certain events

def app_init():
    """
    Initialize all singleton and data elements of viewmgr
    """
    global retriever, server, _series_sel

    # set up classes
    retriever = series_queue.SeriesRetrieveThread()
    server = reactor.WebServerThread()

    # finish work
    _series_sel._show_only_unseen = appcfg.options[appcfg.CFG_SHOW_UNSEEN]
    _series_sel._update_mode = appcfg.options[appcfg.CFG_UPDATED_VIEW]

    retriever.start()
    server.start()

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


def update_statuses(sel = None):
    # every serie with a folder assigned will be scanned, all
    # episodes that match a file, and have the status downloaded,
    # downloading, to download

    candidates = [ series_list.EP_TO_DOWNLOAD,
                   series_list.EP_DOWNLOADING,
                   series_list.EP_DOWNLOADED]

    updatecount = 0
    epcount = 0

    if sel is None:
        serieslist = db.store.find(series_list.Series)
        serieslist = [series for series in serieslist]     # decouple resultset
    else:
        serieslist = [ sel ]
        
    for series in serieslist:
        if series.folder != '':
            sfiles = db_conv_xml._collectEpisodeFiles(series_list.get_series_path(series))

            episodes = db.store.find(series_list.Episode, series_list.Episode.series_id == series.id)
            episodes = [episode for episode in episodes]    
            for episode in episodes:
                if (episode.status in candidates) and (episode.season in sfiles):
                    episode.status = series_list.EP_READY
                    episode.changed = 0
                    db.store.commit()

                    if sel is not None:
                        episode_updated(episode)

                    updatecount += 1
                epcount += 1

    if sel is None:
        set_view(series_filter.VIEW_SERIES)

    return (updatecount, epcount)

def select_all_episodes():
    Publisher().sendMessage(signals.SELECT_ALL_EPISODES)


def get_selected_episodes():
    if _callbackGetSelectedEpisodes is not None:
        return _callbackGetSelectedEpisodes()
    return list()


def clear_new_episodes():
    result = db.store.find(series_list.Episode, series_list.Episode.status == series_list.EP_NEW)
    episodes = [ ep for ep in result ]
    for ep in episodes:
        ep.status = series_list.EP_READY
        ep.changed = 0
        episode_updated(ep)
    db.store.commit()


def clear_updated_episodes():
    result = db.store.find(series_list.Episode, series_list.Episode.changed != 0)
    episodes = [ ep for ep in result ]
    for ep in episodes:
        ep.changed = 0
        episode_updated(ep)
    db.store.commit()


def set_view(viewtype):
    """
    Sets a certain view. This is to sync the data belonging to that view
    and trigger a new update
    """
    _series_sel.setView(viewtype)
    if viewtype != series_filter.VIEW_SERIES:
        appstate["series_id"] = -1
    Publisher().sendMessage(signals.SET_VIEW, viewtype)


def series_active():
    """
    Returns true if the view is VIEW_SERIES and there is a series selected
    to look at
    """
    return _series_sel._selected_series_id != -1 and \
           _series_sel._view_type == series_filter.VIEW_SERIES


def edit_episode(episode_id):
    """
    Publishes a signal to edit the episode
    """
    Publisher().sendMessage(signals.EPISODE_EDIT, episode_id);


def add_series(series):
    """
    Add this new series object to the database, and emit signal that
    other views can also append it to the list
    """
    db.store.add(series)
    db.store.commit()
    # reflect ID to series object
    db.store.flush()

    Publisher().sendMessage(signals.SERIES_ADDED, series)


def app_settings_changed():
    """
    Call this to send a signal that informs all the views that the
    application settings are changed. Every view using these settings
    should investigate if their view needs to be updated
    """
    _series_sel._show_only_unseen = appcfg.options[appcfg.CFG_SHOW_UNSEEN]
    _series_sel._update_mode = appcfg.options[appcfg.CFG_UPDATED_VIEW]
    _series_sel.syncEpisodes()

    Publisher().sendMessage(signals.APP_SETTINGS_CHANGED)


def set_selection(series):
    """
    Select the series that is given here
    """
    Publisher().sendMessage(signals.SERIES_SELECT, series)
    if series:
        appstate["series_id"] = series.id
        if _series_sel._view_type != series_filter.VIEW_SERIES:
            Publisher().sendMessage(signals.SET_VIEW, series_filter.VIEW_SERIES)
            _series_sel.setSelection(series.id)
            _series_sel.setView(series_filter.VIEW_SERIES)
        else:
            _series_sel.setSelection(series.id)
    else:
        appstate["series_id"] = -1


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


def get_all_series(manual = False):
    """
    Initializes the transfer to send all the serie jobs to the
    receive thread, and after that, hopefully results will
    come back
    """
    Publisher().sendMessage(signals.APP_LOG, "Sending all series to Series Receive thread...")

    # send all series from db to the receive queue
    result = db.store.find(series_list.Series)
    all_series = [ series for series in result.order_by(series_list.Series.name) ]
    ignored = 0
    sent = 0
    td = datetime.date.today()
    for series in all_series:
        # we have to decouple the series object (due to multi threading issues)
        if series.postponed != 0:
            ignored += 1
            continue

        # empty URL's are allowed, but not processed
        if series.url.strip() == '':
            continue

        allow = True
        d = series.getLastUpdate()
        if not manual and d != None:
            upd = series.update_period
            if upd < 0:
                # we have to check if the weekday is today
                # and we haven't checked today yet
                if upd > -8:
                    delta = td - d
                    if delta.days <= 7 and delta.days > 0:
                        # if less or equal to a week, check for the week day
                        if td.weekday() == abs(upd + 1):
                            # if we updated today already, skip
                            if td.strftime("%Y%m%d") == series.last_update:
                                allow = False
                        else:
                            allow = False
                    elif delta.days == 0:
                        # today already checked, skip it
                        allow = False
                    else:
                        # placeholder for fall through if days > 7
                        # we should always check because the user could
                        # have logged in one day later or even longer
                        # ago.
                        pass

                else:
                    # check every bi-weekly or monthly
                    if upd == -8:
                        weeks = 2
                    else:
                        weeks = 4
                    allow = (d + datetime.timedelta(weeks=weeks) <= td)
            else:
                allow = (d + datetime.timedelta(days=upd) <= td)

        if allow:
            sent += 1
            item = series_queue.SeriesQueueItem(series.id, series.name, series.url.split('\n'))
            item.manual = manual
            retriever.in_queue.put( item )
        else:
            ignored += 1

    Publisher().sendMessage(signals.APP_LOG, "Sent %i series and ignored %i (not yet in time slot) ..." % \
                            (sent, ignored))


def probe_series():
    """
    Probes if there are more series. If there are series left to process,
    the series list is updated, and the appropiate signals are sent out to
    display them. This is done in the main (GUI) thread because there are
    signals involved.
    """

    # cache list with ID of series as lookup
    # we use this to verify the series is present
    series_cache = dict()
    db_changed = False

    while not retriever.out_queue.empty():
        item = retriever.out_queue.get()
        if item:
            for episode in item.episodes:
                # for every episode, check if it exists in the DB. If it does
                # attempt an update. If it doesn't, we add it. We use the
                # follow up number (which is mandatory) for identification
                if not episode.number or episode.series_id < 0:
                    continue

                nr = str(episode.number)
                result = db.store.find(series_list.Episode, (series_list.Episode.number == unicode(nr)),
                                                            (series_list.Episode.series_id == episode.series_id)).one()

                # also check if we need to cache the series ID
                if episode.series_id not in series_cache:
                    series = db.store.find(series_list.Series, series_list.Series.id == episode.series_id).one()

                    if series:
                        series_cache[episode.series_id] = series
                    else:
                        # ignore this episode, the series parent is killed / gone
                        continue
                else:
                    series = series_cache[episode.series_id]

                # only update the series if we are not manually retrieving
                if not item.manual:
                    series.setLastUpdate()

                if not result:
                    episode.changed = 1
                    episode.status = series_list.EP_NEW
                    episode.setLastUpdate()

                    db.store.add(episode)
                    db_changed = True
                    db.store.flush()

                    _series_sel.filterEpisode(episode)
                else:
                    # we found the episode, we will update only certain parts
                    # if they are updated properly, we willl inform and update the DB
                    if result.locked == 0:
                        updated = False
                        if result.title == '' and episode.title != '':
                            result.title = unicode(episode.title)
                            updated = True
                        if result.season == '' and episode.season != '':
                            result.season = unicode(episode.season)
                            updated = True
                        # resolve policy
                        if (result.aired == "" and episode.aired != "") or \
                           (result.getPriority("aired") < episode.getPriority("aired")):
                            result.aired = episode.aired
                            result.setPriority("aired", episode.getPriority("aired"))
                            result.new = 1
                            updated = True

                        if updated:
                            db_changed = True
                            result.changed = 1
                            result.setLastUpdate()
                            _series_sel.filterEpisode(result, updated = True)

            # all changes are committed here
            if db_changed:
                db.store.commit()

            return

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

    server.stop()
    server.join(2000)


def get_selected_series():
    """
    Determine selected series, get that one or else get all
    """
    series = db.store.get(series_list.Series, _series_sel._selected_series_id)
    if series and series.url.strip() != '':
        item = series_queue.SeriesQueueItem(series.id, series.name, series.url.split("\n"))
        item.manual = True
        retriever.in_queue.put(item)


def delete_series(series):
    """
    Delete the series from all lists and let the GUI update
    itself.
    """

    if series.id == _series_sel._selected_series_id:
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

    _do_clear_cache(series)

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
    _series_sel.filterEpisode(episode, updated = True)


def _do_clear_cache(series):
    """
    Internal function to clear cache of series
    e.g. wipe all episodes
    """
    # delete all episodes belonging to series
    result = db.store.find(series_list.Episode, series_list.Episode.series_id == series.id)
    for episode in result:
        db.store.remove(episode)
        _series_sel.delete_episode(episode)
    db.store.commit()


def clear_current_cache():
    """
    Clear all or some series
    """
    # get current selected series
    sid = _series_sel._selected_series_id
    if sid != -1:
        series = db.store.get(series_list.Series, sid)
        if series:
            # now delete all related episodes
            _do_clear_cache(series)
