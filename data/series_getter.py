import urllib2
from BeautifulSoup import BeautifulSoup
from Queue import Queue
import re
import series_list

# Date convert. I'll do it like this because I don't know for sure if the month date
# is sensitive of system locales, and if the date parser can parse three digit months
_months = { "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
            "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12" }

class EpGuidesSeriesDownloadCmd(object):
    """ Extract serie from epguides.com site and returns result """
    
    def __init__(self, logqueue, series, url):
        self._series = series
        self.__log = logqueue
        self._url = url
        # regular expression with all information inside
        self._re1 = re.compile(r"(?P<ep_id>\d+)\.[ \t]+(?P<ep_season>(\d+[ \t]*\-[ \t]*\d+){0,1})" + \
                                "(.*?)(?P<ep_date>\d{1,2}[ \t]+[a-zA-Z]+" + \
                                "[ \t]+\d+)")
        self._re2 = re.compile(r"(?P<ep_id>\d+)\.[ \t]+(?P<ep_season>(\d+[ \t]*\-[ \t]*\d+){0,1})" + \
                                "(.*)")
        
        
    def __compose_result(self, episodes, message):
        """
        Compose the result on a uniform place
        """
        return (episodes, message)
        
    
    def retrieve(self):
        """ Retieves and decodes. Returns the following:
        
            (None, error_str)   - In case of error string
            (serie, status_str) - In case of succesful extract
            
            serie -> [ (episode_nr, episode_string, ... {future} ),
                       .... ]
        """

        self.__log.put("Opening URL : '%s'" % self._url)
        
        # attempt opening URL
        try:
            f = urllib2.urlopen(self._url)
            html = f.read()
        except urllib2.URLError, msg:
            return self.__compose_result(None, "Error accessing site '%s' for series '%s' : %s" % \
                                               (self._url, self._series.name, msg))
        except ValueError, msg:
            return self.__compose_result(None, "Error accessing site '%s' for series '%s' : %s" % \
                                               (self._url, self._series.name, msg))
            
        self.__log.put("Data for '%s' read. Parsing ..." % self._series.name)
        
        # find first divider for Episodes
        soup = BeautifulSoup(html)
        
        # <div id="eplist">
        bypass = False
        res = soup.find("div", attrs = {"id" :"eplist"})     
        if not res:            
            # attempt a bypass
            res = soup.find("pre")
            if not res:
                return self.__compose_result(None, "Can't find marker <div id='eplist'> or old marker <pre>")
            else:
                bypass = True
        else:
            res = res.find("pre")        
            if not res:
                return self.__compose_result(None, "Can't find marker <pre>")
        
        # <a target="_blank" href="???">{series title}</a>
        # chop up all series and also preserve the text in front of it
        episode_list = []
        ep_hrefs = res.findAll('a')
        
        self.__log.put("Found episode section. Parsing ...")
        
        for ep_href in ep_hrefs:
            text_before = ep_href.previousSibling.strip()
            text_title = ep_href.string.strip()
            
            # do special magic to remove stray newlines
            # between episodes it might be that there 
            # is extra (unneeded) text 
            pos = text_before.rfind('\n') 
            if pos > 0 and (pos+1) < len(text_before):  
                text_before = text_before[pos+1:].strip() 
            
            if text_before and text_title:
                episode_list.append( (text_before, text_title) )
         
        # now parse the things and see how far we get       
        ep_list = list()
        for ep_text, ep_title in episode_list:
            m = self._re1.match(ep_text)
            if not m:
                m = self._re2.match(ep_text)        
            if m:
                gd = m.groupdict()
                episode = series_list.Episode()
                episode.number = unicode(gd["ep_id"])
                episode.title = unicode(ep_title)            
                
                if "ep_season" in gd:
                    seaslist = gd["ep_season"]
                    if seaslist:
                        seaslist = seaslist.split('-')
                        if len(seaslist) > 1:
                            try:
                                se = int(seaslist[0].strip())
                                ep = int(seaslist[1].strip())
                                episode.season = unicode("S%02iE%02i" % (se, ep))
                            except ValueError:
                                pass
                if "ep_date" in gd:
                    if gd["ep_date"]:
                        datelist = gd["ep_date"].split(' ')
                        if len(datelist) > 2:
                            monthstr = datelist[1].lower().strip()
                            if monthstr in _months:
                                try:
                                    epday = int(datelist[0].strip(' '))
                                    epyr = int(datelist[2].strip(' '))
                                    datestr = "%02i-%s-%02i" % (epday, _months[monthstr], epyr)
                                    episode.aired = unicode(datestr)
                                except ValueError:
                                    pass
                
                # add episode
                episode.series_id = self._series.id                                                
                ep_list.append(episode)

        self.__log.put("Parsing complete!")

        if not ep_list:
            return self.__compose_result(None, "No valid series found!")
        else:
            return self.__compose_result(ep_list, "")


class TvComSeriesDownloadCmd(object):
    """ Extract serie from tv.com site and returns result """
    
    def __init__(self, logqueue, series, url):
        self._series = series
        self.__log = logqueue
        self._url = url
        
        
    def __compose_result(self, episodes, message):
        """
        Compose the result on a uniform place
        """
        return (episodes, message)
        
    
    def retrieve(self):
        """ Retieves and decodes. Returns the following:
        
            (None, error_str)   - In case of error string
            (serie, status_str) - In case of succesful extract
            
            serie -> [ (episode_nr, episode_string, ... {future} ),
                       .... ]
        """

        self.__log.put("Opening URL : '%s'" % self._url)
        
        # attempt opening URL
        try:
            f = urllib2.urlopen(self._url)
            html = f.read()
        except urllib2.URLError, msg:
            return self.__compose_result(None, "Error accessing site '%s' for serie '%s' : %s" % \
                                               (self._url, self._series.name, msg))
        except ValueError, msg:
            return self.__compose_result(None, "Error accessing site '%s' for serie '%s' : %s" % \
                                               (self._url, self._series.id, msg))
            
        self.__log.put("Data for '%s' read. Parsing ..." % self._series.name)
        
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
            ep = r.fetchText(text=True)
            if len(ep) > 1:
                episode = series_list.Episode()
                episode.number = unicode(ep[0].strip().rstrip('.'))
                episode.title = unicode(ep[1].strip())
                episode.series_id = self._series.id                                                
                ep_list.append( episode )
        
                
        self.__log.put("Parsing complete!")
        
        if not ep_list:
            return self.__compose_result(None, "No valid series found!")
        else:
            return self.__compose_result(ep_list, "")
    

# testing code! 
if __name__ == "__main__":

    log = Queue()
    
    alt_site = ''

    import sys

    if len(sys.argv) > 1:
        alt_site = sys.argv[1]
          
        print "Testing -- %s" % alt_site
        c = EpGuidesSeriesDownloadCmd(log, 'test', alt_site)
        series_lst, err_str = c.retrieve()
        if err_str:
            print "ERROR: %s" % err_str 
        else:
            for episode in series_lst:
                print "(%s) %s - %s. %s" % (episode._date, episode._season, episode._ep_nr, episode._ep_title)
                