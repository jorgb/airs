import libxml2
import datetime
from data import series_list
from data import db, appcfg, searches
import re
import os

_media_extensions = ["avi", "mov", "wmv", "mkv", "xvid", "divx", "mpg", "mpeg"]

class EpisodeFile(object):
    def __init__(self):
        self.filename = ''
        self.filepath = ''
        self.size = 0

def _getMediaCount(series_path):
    """ Returns number of files in directory which have a valid media extension """
    count = 0
    for root, dirs, files in os.walk(series_path):
        if os.path.split(root)[1] != appcfg.AIRS_ARCHIVED_PATH:
            for fn in files:
                fnroot, fnext = os.path.splitext(fn)
                if fnext.lower().lstrip(".") in _media_extensions:
                    count += 1
    return count


def _createOptionsNode():
    """ Creates a node with in there some options that the XSLT engine
    might want to alter the output """

    options = libxml2.newNode("options")
    options.setProp("today", datetime.date.today().strftime("%Y%m%d"))

    layout = libxml2.newNode("layout")
    options.addChild(layout)

    server = libxml2.newNode("server")
    server.setProp("ip", appcfg.options[appcfg.CFG_WEB_URL])
    server.setProp("port", str(appcfg.options[appcfg.CFG_WEB_PORT]))
    options.addChild(server)

    layout.setContent(appcfg.conv_layout_str[appcfg.options[appcfg.CFG_LAYOUT_SCREEN]])

    return options


m1 = re.compile("(.*?)S(?P<season>[0-9]+)[ ]*E(?P<episode>[0-9]+)(.*?)", flags = re.IGNORECASE)
m2 = re.compile("(?P<season>[1-9]{1})(?P<episode>[0-9]{2})(.*?)")
m3 = re.compile("(.*?)\.(?P<season>[0-9]{1})(?P<episode>[0-9]{2})\.(.*?)")
m4 = re.compile("(.*?)(?P<season>[0-9]+)x(?P<episode>[0-9]+)(.*?)", flags = re.IGNORECASE)

def _collectEpisodeFiles(series_path):
    """ Returns all the episodes recursively, searches for a season mask and if found
        indexes them. All unindexed files which are still media files will be returned
        too for displaying in a seperate section """
    epfiles = dict()
    ucat = list()

    matches = [ m1,
                m2,
                m3,
                m4 ]

    for root, dirs, files in os.walk(series_path):

        # only scan paths that do not end with "Seen-Airs"
        if os.path.split(root)[1] != appcfg.AIRS_ARCHIVED_PATH:
            for fn in files:
                fnroot, fnext = os.path.splitext(fn)
                if fnext.lower().lstrip(".") in _media_extensions:

                    item = EpisodeFile()
                    item.filename = fn
                    item.filepath = os.path.join(root, fn)
                    try:
                        item.size = os.stat(item.filepath)[6] / 1048576.0
                    except OSError:
                        item.size = 0

                    orphan = True
                    result = None
                    for m in matches:
                        result = m.match(fn)

                        if result is not None:
                            seas_str = result.group("season")
                            ep_str = result.group("episode")

                            season = "S%02iE%02i" % (int(seas_str), int(ep_str))

                            if season in epfiles:
                                epfiles[season].append(item)
                            else:
                                l = list()
                                l.append(item)
                                epfiles[season] = l

                            orphan = False
                            break

                    if orphan:
                        ucat.append(item)

    # store all not categorised items here, leave '_' as key
    # for sorting properly later on
    epfiles["_"] = ucat

    return epfiles


def _sortOrphans(a, b):
    """ Sorts the orphan list so that seasoned items are sorted first """
    if a[0] == b[0]:
        if a[1] < b[1]:
            return -1
        else:
            return 1

    if a[1] < b[1]:
        return -1
    elif a[1] > b[1]:
        return 1

    return 0

def _sortEpisodes(a, b):
    s1l = len(a.season)
    s2l = len(b.season)
    if s1l > 0 and  s2l > 0:
        if a.season > b.season:
            return 1
        else:
            return -1
    elif s1l > 0:
        return -1
    elif s2l > 0:
        return 1
    if a.number > b.number:
        return 1
    else:
        return -1

def _sortEpisodeFiles(a, b):
    if a.size > b.size:
        return -1
    elif a.size < b.size:
        return 1
    return a.filename < b.filename


def get_series_xml():
    """
    This function returns an XML structure that contains all the series
    that are currently in airs, with all properties needed for XSLT -> HTML
    """

    dom = libxml2.newDoc("1.0")

    root = libxml2.newNode("airs")
    dom.addChild(root)

    options = _createOptionsNode()
    root.addChild(options)

    items = libxml2.newNode("series")
    root.addChild(items)

    result = db.store.find(series_list.Series).order_by(series_list.Series.name)
    series = [serie for serie in result]

    for item in series:
        serie = libxml2.newNode("item")

        serie.setProp("name", item.name)
        serie.setProp("id", str(item.id))
        serie.setProp("cancelled", str(item.postponed))
        serie.setProp("folder", item.folder)

        seriespath = series_list.get_series_path(item)
        serie.setProp("mediacount", str(_getMediaCount(seriespath)))

        # report total number of episodes and the
        # episodes already seen
        c = db.store.execute("select count(*) from episode where series_id = %i" % item.id)
        totalcount = str(c.get_one()[0])

        c = db.store.execute("select count(*) from episode where series_id = %i and status = 4" % item.id)
        seencount = str(c.get_one()[0])

        serie.setProp("seencount", seencount)
        serie.setProp("count", totalcount)

        items.addChild(serie)

    return dom


def get_episode_list(series_id):
    """
    This function returns an XML structure that contains all the episodes that
    a certain series contains, and with the episodes also the files that can
    be played per episode.
    """

    dom = libxml2.newDoc("1.0")

    root = libxml2.newNode("airs")
    dom.addChild(root)

    options = _createOptionsNode()
    root.addChild(options)

    #searchnode = libxml2.newNode("engines")
    #root.addChild(searchnode)

    #engines = db.store.find(searches.Searches)
    #for engine in engines:
    #    se = libxml2.newNode("engine")
    #    se.setProp("name", engine.name.encode('ascii', 'replace'))
    #    se.setProp("sid", str(engine.id))
    #    searchnode.addChild(se)

    series = db.store.find(series_list.Series, series_list.Series.id == series_id).one()
    if series is None:
        return dom

    items = libxml2.newNode("episodes")
    items.setProp("id", str(series_id))
    items.setProp("name", series.name)

    c = db.store.execute("select count(*) from episode where series_id = %i and status != %i" % \
                         (series_id, series_list.EP_SEEN))
    unseen = str(c.get_one()[0])
    items.setProp("unseen", unseen)

    root.addChild(items)

    result = db.store.find(series_list.Episode, series_list.Episode.series_id == series_id)
    episodes = [episode for episode in result]

    episodes.sort(_sortEpisodes)

    if series.folder != '':
        sfiles = _collectEpisodeFiles(series_list.get_series_path(series))
    else:
        sfiles = dict()

    engines = db.store.find(searches.Searches)

    for item in episodes:
        episode = libxml2.newNode("item")

        episode.setProp("number", str(item.number))
        episode.setProp("id", str(item.id))
        episode.setProp("search_id", str(item.id))
        episode.setProp("title", item.title.encode('ascii', 'replace'))
        sstr = item.season.upper()
        episode.setProp("season", sstr)
        episode.setProp("aired", item.aired)
        episode.setProp("status", str(item.status))

        # now go and see if we can find any files that match the season mask
        filesnode = libxml2.newNode("files")
        episode.addChild(filesnode)

        files_added = False
        if len(sstr) > 3:
            if sstr in sfiles:
                epfiles = sfiles[sstr]
                epfiles.sort(_sortEpisodeFiles)

                for epobj in epfiles:

                    if epobj.size > 0:
                        files_added = True
                        filenode = libxml2.newNode("file")
                        filenode.setProp("filepath", epobj.filepath.encode('ascii', 'replace'))
                        filenode.setProp("filename", epobj.filename.encode('ascii', 'replace'))
                        if epobj.size > 1024:
                            filenode.setProp("size", str("%.02f" % (epobj.size / 1024)))
                            filenode.setProp("unit", "Gb")
                        else:
                            filenode.setProp("size", str("%.02f" % epobj.size))
                            filenode.setProp("unit", "Mb")

                        filesnode.addChild(filenode)

                # remove from season dict, but not when the episode is seen
                # because that will most likely not display it in the orphaned files
                if item.status != series_list.EP_SEEN:
                    del sfiles[sstr]

        if not files_added:
            searchnode = libxml2.newNode("engines")
            episode.addChild(searchnode)

            for engine in engines:
                se = libxml2.newNode("engine")
                se.setProp("name", engine.name.encode('ascii', 'replace'))
                se.setProp("url", engine.getSearchURL(item, series))
                searchnode.addChild(se)

        items.addChild(episode)

    # now check what files we have left that are not yet linked to an episode
    # these are linked to a season string if there is any, and all non season
    # files sorted at the bottom

    orphans = list()
    for skey in sfiles.iterkeys():
        sfile = sfiles[skey]
        for orphan in sfile:
            orphans.append( (skey, orphan.filename, orphan.filepath) )

    orphans.sort(cmp = _sortOrphans)

    onodes = libxml2.newNode("orphans")
    root.addChild(onodes)

    for orphan in orphans:
        filenode = libxml2.newNode("file")
        if orphan[0] != '_':
            filenode.setProp("season", orphan[0])

        filenode.setProp("filepath", orphan[2])
        filenode.setProp("filename", orphan[1])
        onodes.addChild(filenode)

    return dom
