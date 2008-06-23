import libxml2
from data import series_list
from data import db
import re
import os

_media_extensions = ["avi", "mov", "wmv", "mkv", "xvid", "divx", "mpg", "mpeg"]

class EpisodeFile(object):
    def __init__(self):
        self.filename = ''
        self.filepath = ''
        

def _collectEpisodeFiles(series_path):
    """ Returns all the episodes recursively, searches for a season mask and if found
        indexes them. All unindexed files which are still media files will be returned 
        too for displaying in a seperate section """
    epfiles = dict()
    ucat = list()
    
    m = re.compile("(.*?)S(?P<season>[0-9]+)E(?P<episode>[0-9]+)(.*?)", flags = re.IGNORECASE)
    for root, dirs, files in os.walk(series_path):
        
        for fn in files:
            fnroot, fnext = os.path.splitext(fn)
            if fnext.lower().lstrip(".") in _media_extensions:

                item = EpisodeFile()
                item.filename = fn
                item.filepath = os.path.join(root, fn)

                result = m.match(fn)
                if result is not None:
                    season = "S%sE%s" % (result.group("season"), result.group("episode"))
                    
                    if season in epfiles:
                        epfiles[season].append(item)
                    else:
                        l = list()
                        l.append(item)
                        epfiles[season] = l
                        
                else:
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

def get_series_xml():
    """
    This function returns an XML structure that contains all the series
    that are currently in airs, with all properties needed for XSLT -> HTML
    """
    
    dom = libxml2.newDoc("1.0")
        
    root = libxml2.newNode("airs")
    dom.addChild(root)
    
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

    series = db.store.find(series_list.Series, series_list.Series.id == series_id).one()
    if series is None:
        return dom
        
    items = libxml2.newNode("episodes")
    items.setProp("id", str(series_id))
    items.setProp("name", series.name)
    root.addChild(items)

    result = db.store.find(series_list.Episode, series_list.Episode.series_id == series_id)
    episodes = [episode for episode in result]
    
    if series.folder != '':
        sfiles = _collectEpisodeFiles(series.folder)
    else:
        sfiles = dict()
    
    # TODO: Sort them by season string and then by episode nr
    
    for item in episodes:
        episode = libxml2.newNode("item")

        episode.setProp("number", str(item.number))
        episode.setProp("id", str(item.id))
        episode.setProp("title", item.title.encode('ascii', 'replace'))        
        sstr = item.season.upper()
        episode.setProp("season", sstr)
        episode.setProp("aired", item.aired)
        episode.setProp("status", str(item.status))
        
        # now go and see if we can find any files that match the season mask
        filesnode = libxml2.newNode("files")
        episode.addChild(filesnode)
    
        if len(sstr) > 3:
            if sstr in sfiles:
                epfiles = sfiles[sstr]
                for epobj in epfiles:
                    
                    filenode = libxml2.newNode("file")
                    filenode.setProp("filepath", epobj.filepath)
                    filenode.setProp("filename", epobj.filename)
                    filesnode.addChild(filenode)
                    
                # remove from season dict
                del sfiles[sstr]
                    
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
    