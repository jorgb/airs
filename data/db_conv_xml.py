import libxml2
import datetime
from data import series_list
from data import db, appcfg, searches
import re
import os

_media_extensions = ["avi", "mov", "wmv", "mkv", "xvid", "divx", "mpg", "mpeg", "mp4", "m4v"]

escmap = [ ("&",  "%26"),
           (" ",  "%20"),
           ("/",  "%2f"),
           ("\\", "%5c") ]

def _escapefile(s):
    for from_esc, to_esc in escmap:
        s = s.replace(from_esc, to_esc)
    return s


def _unescapefile(s):
    for from_esc, to_esc in escmap:
        s = s.replace(to_esc, from_esc)
    return s

class EpisodeFileFuzzyMatch(object):
    def __init__(self, epfile):
        self.epfile = epfile
        self.candidate_id = -1      # episode that matches the most (LEAVE -1!)
        self.diff_score = 0.0       # closer to 1 means better match

class EpisodeFile(object):
    def __init__(self):
        self.filename = ''
        self.filepath = ''
        self.size = 0
        self.fuzzy = False          # if true, file is matched by fuzzy matching
        self.season = ""

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


# last resort title matcher
DIFF_THRESHOLD = 1 / 3.0                        # match at least 33%
m0 = re.compile("[a-z][a-z0-9]*", re.IGNORECASE)
bad_words = set( [ "bia", "pdtv", "ws", "dsrip", "proper", "hdtv", "hd", "tv", 
                   "x264", "aac", "ps3", "dsr" ] )

def _collectEpisodesByID(series, episode_list):
    """ Function that collects per episode ID all files that match this
    episode. This function uses _collectEpisodeFiles to auto match the
    season strings, and further processes all unknown episodes to do
    fuzzy matching on title and file name parts """

    ep_to_file = dict()
    sfiles = _collectEpisodeFiles(series_list.get_series_path(series))

    bad_series_words = set([s.lower() for s in series.name.split()])
    
    ablookup = list()
    if "_" in sfiles:
        # pre process and make lookup
        mediaext_set = set(_media_extensions)
        for abitem in sfiles["_"]:
            orgfile_set = set([ s.lower() for s in m0.findall(abitem.filename) ])
            orgfile_set = orgfile_set - mediaext_set - bad_words - bad_series_words
            ablookup.append( (EpisodeFileFuzzyMatch(abitem), orgfile_set) )

    for episode in episode_list:
        seasonstr = episode.season.upper()
        if len(seasonstr) > 2:
            if seasonstr in sfiles:
                ep_to_file[episode.id] = [efile for efile in sfiles[seasonstr]]

        if appcfg.options[appcfg.CFG_FUZZY_MATCH]:
            # now check episode title with any sets
            title_set = set([ s.lower() for s in m0.findall(episode.title) ])
            if len(title_set) > 0:
                for fuzzy_info, file_set in ablookup:
                    if len(file_set) > 0:
                        score = 1 - len(title_set - file_set) / float(len(title_set))
                        if score >= DIFF_THRESHOLD:
                            if (fuzzy_info.candidate_id == -1) or score > fuzzy_info.diff_score:
                                fuzzy_info.candidate_id = episode.id
                                fuzzy_info.diff_score = score

    # now let's feed the episode info from the ablookup into the lookup list of
    # episodes. This will also group all permanently abandoned files in the
    # category -1.
    abandoned = list()
    for fuzzy_info, dummy in ablookup:
        epid = fuzzy_info.candidate_id
        epfile = fuzzy_info.epfile
        if epid != -1:
            if epid in ep_to_file:
                ep_to_file[epid].append(epfile)
            else:
                ep_to_file[epid] = [ epfile ]
        else:
            abandoned.append(epfile)
    ep_to_file[-1] = abandoned
                    
    return ep_to_file


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
                                item.season = season
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
    if a.season < b.season:
        return -1
    elif a.season > b.season:
        return 1
    else:
        if a.filename < b.filename:
            return -1
        else:
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

    todaystr = series_list.date_to_str(datetime.datetime.now())

    wdelta = series_list.idx_to_weekdelta(appcfg.options[appcfg.CFG_EPISODE_DELTA])
    bottomstr = series_list.date_to_str(datetime.date.today() - datetime.timedelta(weeks = wdelta))

    c = db.store.execute("select count(*) from episode where aired != '' and aired <= '%s'"
                         "and aired > '%s' and new != 0" % (todaystr, bottomstr) )
    items.setProp("airedcount", str(c.get_one()[0]))

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
        c = db.store.execute("select count(*) from episode where series_id = %i and aired != '' and aired < '%s'" % \
                             (item.id, todaystr) )
        totalcount = str(c.get_one()[0])

        c = db.store.execute("select count(*) from episode where series_id = %i and status = %i" % \
                             (item.id, series_list.EP_SEEN))
        seencount = str(c.get_one()[0])

        #c = db.store.execute("select count(*) from episode where series_id = %i and status = 4" % item.id)
        #seencount = str(c.get_one()[0])

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
        sfiles = _collectEpisodesByID(series, episodes)
    else:
        sfiles = dict()

    engines = db.store.find(searches.Searches)

    for item in episodes:
        episode = libxml2.newNode("item")

        episode.setProp("number", str(item.number))
        episode.setProp("id", str(item.id))
        episode.setProp("search_id", str(item.id))
        episode.setProp("title", item.title.encode('utf-8', 'replace'))
        sstr = item.season.upper()
        episode.setProp("season", sstr)
        episode.setProp("aired", item.aired)
        episode.setProp("status", str(item.status))

        # now go and see if we can find any files that match the season mask
        filesnode = libxml2.newNode("files")
        episode.addChild(filesnode)

        files_added = False
        if item.id in sfiles:
            epfiles = sfiles[item.id]
            epfiles.sort(_sortEpisodeFiles)

            for epobj in epfiles:

                if epobj.size > 0:
                    files_added = True
                    filenode = libxml2.newNode("file")
                    # pathetic solution to skipping files that seem to contain
                    # illegal unicode characters
                    try:
                        fp = _escapefile(epobj.filepath)
                        filenode.setProp("filepath", fp.encode('utf-8', 'replace'))
                        filenode.setProp("filename", epobj.filename.encode('utf-8', 'replace'))
                        if epobj.size > 1024:
                            filenode.setProp("size", str("%.02f" % (epobj.size / 1024)))
                            filenode.setProp("unit", "Gb")
                        else:
                            filenode.setProp("size", str("%.02f" % epobj.size))
                            filenode.setProp("unit", "Mb")
                    except UnicodeEncodeError:
                        continue

                    filesnode.addChild(filenode)

            # remove from season dict, but not when the episode is seen
            # because that will most likely not display it in the orphaned files
            if item.status != series_list.EP_SEEN:
                del sfiles[item.id]

        if not files_added:
            searchnode = libxml2.newNode("engines")
            episode.addChild(searchnode)

            for engine in engines:
                se = libxml2.newNode("engine")
                se.setProp("name", engine.name)
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
            orphans.append( orphan )

    orphans.sort(cmp = _sortOrphans)

    onodes = libxml2.newNode("orphans")
    root.addChild(onodes)

    for orphan in orphans:
        filenode = libxml2.newNode("file")

        # pathetic solution to skipping files that seem to contain
        # illegal unicode characters
        filenode.setProp("season", orphan.season)
        try:
            filenode.setProp("filepath", _escapefile(orphan.filepath).encode('utf-8', 'replace'))
            filenode.setProp("filename", orphan.filename.encode('utf-8', 'replace'))
        except UnicodeEncodeError:
            continue

        onodes.addChild(filenode)

    return dom


def get_aired_episode_list(series_id):
    """
    This function returns an XML structure that contains all the episodes that
    are recently aired.
    """

    return None