import urllib2
from BeautifulSoup import BeautifulSoup
from Queue import Queue
import re
import series_list

class EpGuidesSeriesDownloadCmd(object):
    """ Extract serie from epguides.com site and returns result """
    
    def __init__(self, logqueue, site_id, site_url):
        self._site_url = site_url
        self._site_id = site_id
        self.__log = logqueue
        self._re = re.compile("[ \t]*(?P<ep_id>\d+)\.[ \t]+(?P<ep_season>\d+[ \t]*\-[ \t]*\d+)" + \
                              "[ \t]+(?P<prod_nr>.*)[ \t]+(?P<ep_date>\d{1,2}[ \t]+[a-zA-Z]+" + \
                              "[ \t]+\d+)[ \t]+(?P<ep_title>.*)")
        
        
    def __compose_result(self, series_list, message):
        """
        Compose the result on a uniform place
        """
        return (series_list, message)
        
    
    def retrieve(self):
        """ Retieves and decodes. Returns the following:
        
            (None, error_str)   - In case of error string
            (serie, status_str) - In case of succesful extract
            
            serie -> [ (episode_nr, episode_string, ... {future} ),
                       .... ]
        """

        self.__log.put("Opening URL : '%s'" % self._site_url)
        
        # attempt opening URL
        try:
            f = urllib2.urlopen(self._site_url)
            html = f.read()
        except urllib2.URLError, msg:
            return self.__compose_result(None, "Error accessing site '%s' for serie '%s' : %s" % \
                                               (self._site_url, self._site_id, msg))
        except ValueError, msg:
            return self.__compose_result(None, "Error accessing site '%s' for serie '%s' : %s" % \
                                               (self._site_url, self._site_id, msg))
            
        self.__log.put("Data for '%s' read. Parsing ..." % self._site_id)
        
        # find first divider for Episodes
        soup = BeautifulSoup(html)
        
        # <div id="eplist">
        res = soup.find("div", attrs = {"id" :"eplist"})     
        if not res:
            return self.__compose_result(None, "Can't find marker <div id='eplist'>")
            
        # find table entry where episodes are located in
        res = res.find("pre")
        if not res:
            return self.__compose_result(None, "Can't find marker <pre>")
        
        # iterate for series, first fetch all text in a list..
        res = res.fetchText(text=True)
        res = ''.join(res)
        
        # ..now split it up again upon every CR
        # and perform a regexp
        serie_items = res.split('\n')
        
        self.__log.put("Found episode section. Parsing ...")

        ep_list = []        
        for serie_item in serie_items:
            m = self._re.match(serie_item)
            if m:
                gd = m.groupdict()
                episode = series_list.SerieEpisode(None, gd["ep_id"], gd["ep_title"])
                if "ep_season" in gd:
                    seaslist = gd["ep_season"]
                    if seaslist:
                        seaslist = seaslist.split('-')
                        if len(seaslist) > 1:
                            try:
                                se = int(seaslist[0].strip())
                                ep = int(seaslist[1].strip())
                                episode._season = "S%02iE%02i" % (se, ep)
                            except ValueError:
                                pass
                
                # add episode
                ep_list.append(episode)            

                
        self.__log.put("Parsing complete!")

        if not ep_list:
            return self.__compose_result(None, "No valid series found!")
        else:
            return self.__compose_result(ep_list, "")


class TvComSeriesDownloadCmd(object):
    """ Extract serie from tv.com site and returns result """
    
    def __init__(self, logqueue, site_id, site_url):
        self._site_url = site_url
        self._site_id = site_id
        self.__log = logqueue
        
        
    def __compose_result(self, series_list, message):
        """
        Compose the result on a uniform place
        """
        return (series_list, message)
        
    
    def retrieve(self):
        """ Retieves and decodes. Returns the following:
        
            (None, error_str)   - In case of error string
            (serie, status_str) - In case of succesful extract
            
            serie -> [ (episode_nr, episode_string, ... {future} ),
                       .... ]
        """

        self.__log.put("Opening URL : '%s'" % self._site_url)
        
        # attempt opening URL
        try:
            f = urllib2.urlopen(self._site_url)
            html = f.read()
        except urllib2.URLError, msg:
            return self.__compose_result(None, "Error accessing site '%s' for serie '%s' : %s" % \
                                               (self._site_url, self._site_id, msg))
        except ValueError, msg:
            return self.__compose_result(None, "Error accessing site '%s' for serie '%s' : %s" % \
                                               (self._site_url, self._site_id, msg))
            
        self.__log.put("Data for '%s' read. Parsing ..." % self._site_id)
        
        # find first divider for Episodes
        soup = BeautifulSoup(html)
        
        res = soup.find("div", attrs = {"class" :"pod", "section": "episodes"})     
        if not res:
            return self.__compose_result(None, "Can't find marker #1")
            
        # find table entry where episodes are located in
        res = res.find("table", {"class": "f-11"})
        if not res:
            return self.__compose_result(None, "Can't find marker #2")
        
        # iterate for series
        res = res.findAll("td", {"class": "f-bold"})
        if not res:
            return self.__compose_result(None, "Can't find marker #3")
        
        self.__log.put("Found episode section. Parsing ...")

        ep_list = []
        for r in res:
            # extract the episode query
            episode = r.fetchText(text=True)
            if len(episode) > 1:
                number = episode[0].strip().rstrip('.')
                title = episode[1].strip()
                episode = series_list.SerieEpisode(None, number, title)                                
                ep_list.append( episode )
        
                
        self.__log.put("Parsing complete!")
        
        if not ep_list:
            return self.__compose_result(None, "No valid series found!")
        else:
            return self.__compose_result(ep_list, "")
    

# testing code! 
if __name__ == "__main__":

    sites = [ ("Supernatural", "http://epguides.com/Supernatural/") ]

    log = Queue()
              
    for site_id, site_url in sites:
        print "Testing -- %s"  % site_id
        c = EpGuidesSeriesDownloadCmd(log, site_id, site_url)
        series_lst, err_str = c.retrieve()
        if err_str:
            print "ERROR: %s" % err_str 
            break
        else:
            for episode in series_lst:
                print episode._ep_nr, episode._ep_title
                