import datetime
import series_list
import db, appcfg, searches
import episodefile
import re
import os


class EpisodeScanFile(object):
    def __init__(self):
        self.filename = ''
        self.size = 0
        self.fuzzy = False          # if true, file is matched by fuzzy matching
        self.season = ""

        
_media_extensions = ["avi", "mov", "wmv", "mkv", "xvid", "divx", "mpg", "mpeg", "mp4", "m4v"]
        
m1 = re.compile("(.*?)S(?P<season>[0-9]+)[ ]*E(?P<episode>[0-9]+)(.*?)", flags = re.IGNORECASE)
m2 = re.compile("(?P<season>[1-9]{1})(?P<episode>[0-9]{2})(.*?)")
m3 = re.compile("(.*?)\.(?P<season>[0-9]{1})(?P<episode>[0-9]{2})\.(.*?)")
m4 = re.compile("(.*?)(?P<season>[0-9]+)x(?P<episode>[0-9]+)(.*?)", flags = re.IGNORECASE)


def _get_mediafiles(series_path):
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

                    item = EpisodeScanFile()
                    item.filename = os.path.join(root, fn)
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
    

# TODO: To be able to scan a seperate dir, like a download dir, this
# function should be passed as argument a list of episode file 
# objects that exist in the other directory so that the enumeration
# of files in that seperate dir is not constantly performed on 
# every series that is updated.

def update_mediafiles(series):
    """ This function scans all available files on disk for a specific series, and 
    compares that with the files in the database. If changes are foundm updates
    are performed or files are removed from the database """
    
    # get all relevant stored files
    dbfiles = db.store.find(episodefile.EpisodeFile, episodefile.EpisodeFile.series_id == series.id)
    dbfiles = [dbfile for dbfile in dbfiles]   # decouple from the query result
    
    # get all files from disk
    diskfiles = _get_mediafiles(series_list.get_series_path(series))
    


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


