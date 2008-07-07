#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import wx, sys
from data import signals, viewmgr, db, series_list, series_filter, appcfg
from data import searches, options

from images import whats_new, to_download, \
                   downloading, icon_processed, icon_ready, icon_new, \
                   icon_downloaded

import menuhelper

from wx.lib.pubsub import Publisher
import datetime

aired_days    = { 0: 'Today',  1: 'Tomorrow', -1: 'Yesterday' }
aired_weekday = { 0: 'Monday', 1: 'Tuesday',   2: 'Wednesday', 3: 'Thursday',
                  4: 'Friday', 5: 'Saturday',  6: 'Sunday' }

def _sort_updated(a, b):
    """
    Sort method, updated view
    """
    adate = a.aired
    bdate = b.aired

    if adate and bdate:
        if adate < bdate:
            return 1
        if adate > bdate:
            return -1
    else:
        if adate and not bdate:
            return -1
        if not adate and bdate:
            return 1

    if a.season > b.season:
        return -1
    if a.season < b.season:
        return 1
    if a.number > b.number:
        return -1
    if a.number < b.number:
        return 1
    # sort by episode title
    if a.title > b.title:
        return 1
    if a.title < b.title:
        return -1
    # else it's equal enough
    return 0


def _sort_normal(a, b):
    """
    Sort method, normal view (no updated)
    """
    if a.season > b.season:
        return -1
    if a.season < b.season:
        return 1

    adate = a.aired
    bdate = b.aired

    if adate and bdate:
        if adate < bdate:
            return 1
        if adate > bdate:
            return -1
    if a.number > b.number:
        return -1
    if a.number < b.number:
        return 1
    # sort by episode title
    if a.title > b.title:
        return 1
    if a.title < b.title:
        return -1
    # else it's equal enough
    return 0


class EpisodeListCtrl(wx.ListCtrl):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)

        self._ep_idx = 0
        self._updating = False
        self.viewID = ''    # kind of view
        self._search_ids = dict()

        a = appcfg
        self.InsertColumn(0, "Nr.", width = a.options[a.CFG_LAYOUT_COL_NR])
        self.InsertColumn(1, "Season", width = a.options[a.CFG_LAYOUT_COL_SEASON])
        self.InsertColumn(2, "Series", width = a.options[a.CFG_LAYOUT_COL_SERIES])
        self.InsertColumn(3, "Title", width = a.options[a.CFG_LAYOUT_COL_TITLE])
        self.InsertColumn(4, "Date", width = a.options[a.CFG_LAYOUT_COL_DATE])

        self._icons = wx.ImageList(16, 16)

        self._stat_to_icon = dict()
        self._stat_to_icon[series_list.EP_NEW] = self._icons.Add(icon_new.getBitmap())
        self._stat_to_icon[series_list.EP_DOWNLOADING] = self._icons.Add(downloading.getBitmap())
        self._stat_to_icon[series_list.EP_SEEN] = self._icons.Add(icon_processed.getBitmap())
        self._stat_to_icon[series_list.EP_TO_DOWNLOAD] = self._icons.Add(to_download.getBitmap())
        self._stat_to_icon[series_list.EP_READY] = self._icons.Add(icon_ready.getBitmap())
        self._stat_to_icon[series_list.EP_DOWNLOADED] = self._icons.Add(icon_downloaded.getBitmap())

        self.SetImageList(self._icons, wx.IMAGE_LIST_SMALL)

        Publisher().subscribe(self._add, signals.EPISODE_ADDED)
        Publisher().subscribe(self._delete, signals.EPISODE_DELETED)
        Publisher().subscribe(self._update, signals.EPISODE_UPDATED)
        Publisher().subscribe(self._clear, signals.EPISODES_CLEARED)
        Publisher().subscribe(self._onSelectAll, signals.SELECT_ALL_EPISODES)
        Publisher().subscribe(self._onAppClose, signals.APP_CLOSE)
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self._onMenuPopup)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._onItemActivated)
        self.Bind(wx.EVT_UPDATE_UI, self._onListChange)

        # for wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self._onMenuPopup)

        # for wxGTK
        self.Bind(wx.EVT_RIGHT_UP, self._onMenuPopup)

        self._syncToday()

    def _onListChange(self, event):
        self._syncEpisodeCount()

    def _syncEpisodeCount(self):
        count = 0
        idx = self.GetFirstSelected()
        while idx != wx.NOT_FOUND:
            count += 1
            idx = self.GetNextSelected(idx)
        viewmgr.appstate["epcount"] = count
        viewmgr.appstate["lstcount"] = self.GetItemCount()

    def _onItemActivated(self, event):
        # find search engine to use
        executed = False
        id = options.getIntOption("default_search")
        if id != -1:
            search = db.store.find(searches.Searches, searches.Searches.id == id).one()
            if search:
                self._doExecuteSearch(search)
                executed = True
        if not executed:
            wx.MessageBox("Please specify a default search engine!", "Error",
                          wx.ICON_ERROR)

    def _doExecuteSearch(self, search):
        eps = self.__getSelectedEpisodes()
        if eps:
            episode = eps[0]
            series = db.store.find(series_list.Series, series_list.Series.id == episode.series_id).one()
            url = search.getSearchURL(episode, series)
            wx.LaunchDefaultBrowser(url)


    def _onAppClose(self, event):
        a = appcfg
        a.options[a.CFG_LAYOUT_COL_NR] = self.GetColumnWidth(0)
        a.options[a.CFG_LAYOUT_COL_SEASON] = self.GetColumnWidth(1)
        a.options[a.CFG_LAYOUT_COL_SERIES] = self.GetColumnWidth(2)
        a.options[a.CFG_LAYOUT_COL_TITLE] = self.GetColumnWidth(3)
        a.options[a.CFG_LAYOUT_COL_DATE] = self.GetColumnWidth(4)


    def _onSelectAll(self, msg):
        for i in range(0, self.GetItemCount()):
            self.Select(i, on = 1)
        self.SetFocus()


    def _clear(self, msg):
        """
        Proxy method to clear list
        """
        self.DeleteAllItems()
        self._syncToday()


    def _syncToday(self):
        self._today_d = datetime.date.today()
        self._today = self._today_d.strftime("%Y%m%d")


    def _onMenuPopup(self, event):
        """
        Create popup menu to perform some options
        """
        self._se_lookup = dict()
        if self.GetFirstSelected() != wx.NOT_FOUND:
            se_dict = dict()
            menulst = list()
            addsep = False
            if viewmgr._series_sel._view_type == series_filter.VIEW_WHATS_NEW or \
               viewmgr._series_sel._view_type == series_filter.VIEW_WHATS_ON:
                menulst.append("s_todownload")
                addsep = True

            if viewmgr._series_sel._view_type == series_filter.VIEW_TO_DOWNLOAD:
                menulst.append("s_download")
                addsep = True

            if viewmgr._series_sel._view_type == series_filter.VIEW_DOWNLOADING:
                menulst.append("s_downloaded")
                addsep = True

            if viewmgr._series_sel._view_type == series_filter.VIEW_DOWNLOADED or \
                viewmgr._series_sel._view_type == series_filter.VIEW_WHATS_NEW:
                menulst.append("s_ready")
                addsep = True

            if addsep:
                menulst.append("-")

            idx = self.GetFirstSelected()
            if self.GetNextSelected(idx) == wx.NOT_FOUND:
                se_items = list()

                result = db.store.find(searches.Searches)
                lst = [s for s in result.order_by(searches.Searches.name)]
                if lst:
                    for se in lst:
                        se_dict[se.id] = (se.name, se.name, "", None, menuhelper.NORMAL, se)
                        se_items.append(se.id)

                menulst.append( ("&Online Search", se_items) )

                menulst.append("edit_episode")

                if viewmgr.appstate["series_id"] == -1:
                    menulst.append("edit_series")

                if viewmgr._series_sel._view_type != series_filter.VIEW_QUEUES:
                    menulst.append("-")

                menulst.append(("Mark Episode(s) As ...", [ "s_todownload",
                                                            "s_download",
                                                            "s_downloaded",
                                                            "s_ready",
                                                            "s_seen" ] ))
        mnu = wx.Menu()
        menu_ids = menuhelper.populate(mnu, menulst, se_dict)

        for id in se_items:
            self.Bind(wx.EVT_MENU, self._onSearchEntry, id = menu_ids[id])

        self.PopupMenu(mnu)
        mnu.Destroy()

    def _onEditEpisode(self, event):
        eps = self.__getSelectedEpisodes()
        if eps:
            viewmgr.edit_episode(eps[0].id)

    def _onEditSeries(self, event):
        eps = self.__getSelectedEpisodes()
        if eps:
            Publisher().sendMessage(signals.QUERY_EDIT_SERIES, eps[0])

    def _onSearchEntry(self, event):
        se = menuhelper.menuid_to_data(event.GetId())
        if se:
            self._doExecuteSearch(se)

    def __getSelectedEpisodes(self):
        episodes = list()
        idx = self.GetFirstSelected()
        while idx != wx.NOT_FOUND:
            episode = db.store.get(series_list.Episode, self.GetItemData(idx))
            if episode:
                episodes.append(episode)
            idx = self.GetNextSelected(idx)
        return episodes

    def _doSetStatus(self, status):
        episodes = self.__getSelectedEpisodes()
        for episode in episodes:
            episode.status = status
            episode.changed = 0
            episode.new = 0
            db.store.commit()
            viewmgr.episode_updated(episode)

    def _onSetToDownload(self, event):
        self._doSetStatus(series_list.EP_TO_DOWNLOAD)

    def _onSetDownloaded(self, event):
        self._doSetStatus(series_list.EP_DOWNLOADED)

    def _onSetDownloading(self, event):
        self._doSetStatus(series_list.EP_DOWNLOADING)

    def _onSetReady(self, event):
        self._doSetStatus(series_list.EP_READY)

    def _onSetProcessed(self, event):
        self._doSetStatus(series_list.EP_SEEN)

    def _add(self, msg):
        """
        Add an episode to the list, but sort it first and
        add the item to the list later with the given index
        """
        ep = msg.data
        pos = 0

        # dynamically determine position
        if viewmgr.series_active():
            sortfunc = _sort_normal
        else:
            sortfunc = _sort_updated

        if self.GetItemCount() > 0:
            for idx in xrange(0, self.GetItemCount()):
                curr_ep = db.store.get(series_list.Episode, self.GetItemData(idx))
                if curr_ep:
                    if sortfunc(ep, curr_ep) <= 0:
                        pos = idx
                        break
                    pos += 1

        self._insertEpisode(ep, pos)


    def _insertEpisode(self, ep, pos):
        """
        Inserts the episode in the list
        """
        self._ep_idx += 1
        index = self.InsertStringItem(pos, '')
        self.SetItemData(index, ep.id)
        self._updateEpisode(index, ep)


    def _updateEpisode(self, index, ep):
        """
        Convenience function to update episode contents in one place
        """
        self.SetStringItem(index, 0, ep.number)
        self.SetStringItem(index, 1, ep.season)

        series = db.store.get(series_list.Series, ep.series_id)
        if series:
            self.SetStringItem(index, 2, series.name)
        self.SetStringItem(index, 3, ep.title)

        str = ""
        imgidx = self._stat_to_icon[ep.status]

        self.SetItemImage(index, imgidx, imgidx)

        # set date
        if viewmgr._series_sel._view_type == series_filter.VIEW_WHATS_ON:
            # display in periods
            epdate = ep.getAired()
            if epdate:
                delta = epdate - self._today_d
                if delta.days in aired_days:
                    self.SetStringItem(index, 4, aired_days[delta.days])
                else:
                    if delta.days < 0 and delta.days > -8:
                        self.SetStringItem(index, 4, "%i days ago" % abs(delta.days))
                    elif delta.days > 0 and delta.days < 8:
                        self.SetStringItem(index, 4, aired_weekday[epdate.weekday()])
                    else:
                        self.SetStringItem(index, 4, ep.getStrDate())
            else:
                self.SetStringItem(index, 4, '')
        else:
            self.SetStringItem(index, 4, ep.getStrDate())

        upd = ep.last_update
        item = self.GetItem(index)
        if ep.last_update == self._today:
            item.SetTextColour(appcfg.highlightColor)
        elif ep.aired > self._today:
            item.SetTextColour(wx.RED)
        elif ep.aired == '':
            item.SetTextColour(wx.Colour(130, 130, 130))
        else:
            item.SetTextColour(wx.BLACK)
        self.SetItem(item)

    def _update(self, msg):
        """
        Inserts the episode in the list
        """
        ep = msg.data
        idx = self.FindItemData(-1, ep.id)
        if idx != wx.NOT_FOUND:
            self._updateEpisode(idx, ep)

    def _delete(self, msg):
        """
        Respond to a deleted command of an episode
        """

        # Who ever made the wx.ListCtrl must be punished by a life sentence
        # because there is no way to store a reference to the object in
        # the wx.ListCtrl we must poorly scan through the list ourselves
        ep = msg.data
        if self.GetItemCount() > 0:
            idx = self.FindItemData(-1, ep.id)
            if idx != wx.NOT_FOUND:
                self.DeleteItem(idx)
