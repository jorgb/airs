import xml.etree.ElementTree as et
from xml.parsers.expat import ExpatError
from data import series_list
from wx.lib.pubsub import Publisher
from data import signals
import os.path

class SerieListXmlException(Exception):
    pass


def read_series(filename):
    """
    Reads the series from an XML file into a given list which
    is returned.
    """
    
    # create a list object
    serieslist = series_list.SeriesList()    

    # if no file exists (first run), we return an empty list
    if not os.path.isfile(filename):
        return serieslist
    
    try:
        dom = et.parse(filename)
    except (IOError, ExpatError):
        raise SerieListXmlException("Can't open '%s' or error parsing it!" % filename)
    
    elem = dom.getroot()
    
    # iterate through all our series
    for serie in elem.findall("series/item"):

        # construct a SeriesEpisodes object 
        serie_id = serie.get("id")
        serie_link = serie.get("link")
        if serie_id and serie_link:
            series_item = serieslist.addSeries(serie_id)
            series_item._link = serie_link
        else:
            raise SerieListXmlException("Error in attributes 'id' or 'link'!")
        
        # now add all episodes to it
        for eps in serie.findall("episodes/episode"):
            ep_id = eps.get("id")
            ep_seen = eps.get("seen", "0")
            ep_title = eps.text
            if ep_id and ep_title:
                episode_item = series_item.addEpisode(ep_id, ep_title)
                episode_item._seen = (ep_seen == "1")
                episode_item._season = eps.get("season", "-")
                episode_item._date = eps.get("date", "")
            else:
                raise SerieListXmlException("Error in episode of serie '%s'" % serie_id)
            
        # send out the data notification
        # NOTE: send this last so that all children are also restored
        Publisher().sendMessage(signals.DATA_SERIES_RESTORED, series_item)

    return serieslist


def write_series(filename, serieslist):
    """
    Writes the series back to disk
    """

    # first ensure that the path can be created
    datadir, _ = os.path.split(filename)
    if not os.path.exists(datadir):
        try:
            os.makedirs(datadir)
        except:
            raise SerieListXmlException("Can't write data to '%s'" % filename)
    
    root = et.Element("airs")
    
    # collect all series and episodes in this node
    series_node = et.Element("series")
    root.append(series_node)
    
    for series in serieslist._series.values():
        
        # construct a series item
        item_node = et.Element("item")
        item_node.attrib["id"] = series._serie_name
        item_node.attrib["link"] = series._link
        
        if series._episodes:
            eps_node = et.Element("episodes")
            item_node.append(eps_node)
            
            # append all episodes 
            for ep in series._episodes.values():
                ep_node = et.Element("episode")
                if el._seen:
                    ep_node.attrib["seen"] =  "1"
                else:
                    ep_node.attrib["seen"] =  "0"                
                ep_node.attrib["id"] = ep._ep_nr
                ep_node.attrib["season"] = ep._season
                ep_node.attrib["date"] = ep._date
                ep_node.text = ep._ep_title
                
                eps_node.append(ep_node)
        
        series_node.append(item_node)
        
    etr = et.ElementTree(root)
    etr.write(filename)
    