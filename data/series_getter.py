#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import urllib2
#from BeautifulSoup import BeautifulSoup
from bs4 import BeautifulSoup
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
        # regex: ep_id without final dot (.) and ep_date separator is slash (/)
        self._re1 = re.compile(r"(?P<ep_id>\d+)[ \t]+(?P<ep_season>(\d+[ \t]*\-[ \t]*\d+){0,1})" + \
                                "(.*?)(?P<ep_date>\d{1,2}/[a-zA-Z]+" + \
                                "/\d+)")
        # regex: ep_id with final dot (.) and ep_date separator is space or tab
        self._re2 = re.compile(r"(?P<ep_id>\d+)\.[ \t]+(?P<ep_season>(\d+[ \t]*\-[ \t]*\d+){0,1})" + \
                                "(.*?)(?P<ep_date>\d{1,2}[ \t]+[a-zA-Z]+" + \
                                "[ \t]+\d+)")
        # regex: ep_id without final dot (.) and ep_date separator is slash (/) without day
        self._re3 = re.compile(r"(?P<ep_id>\d+)[ \t]+(?P<ep_season>(\d+[ \t]*\-[ \t]*\d+){0,1})" + \
                                "(.*?)(?P<ep_date>[a-zA-Z]+" + \
                                "/\d+)")
        # regex: ep_id without final dot (.) and ep_date unspecified
        self._re4 = re.compile(r"(?P<ep_id>\d+)[ \t]+(?P<ep_season>(\d+[ \t]*\-[ \t]*\d+){0,1})" + \
                                "(.*)")	

        
    def retrieve(self):
        """ Retieves and decodes. Fills in the self._series which is returned
            later. In case of errors, set series.errors = True and set the error_str
            property. Also APPEND episodes to the series.episodes list, no not
            overwrite this list. It doesn't matter if there are episodes already there
        """

        self.__log.put("Opening URL : '%s'" % self._url)
        
        # attempt opening URL
        try:
            f = urllib2.urlopen(self._url)
            html = f.read()
        except urllib2.URLError, msg:
            self._series.setError("Error accessing site '%s' for series '%s' : %s" % \
                                  (self._url, self._series.name, msg))
            return
        except ValueError, msg:
            self._series.setError("Error accessing site '%s' for series '%s' : %s" % \
                                  (self._url, self._series.name, msg))
            return
            
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
                self._series.setError("Can't find marker <div id='eplist'> or old marker <pre>")
                return
            else:
                bypass = True
        else:
            res = res.find("pre")        
            if not res:
                self._series.setError("Can't find marker <pre>")
        
        # <a target="_blank" href="???">{series title}</a>
        # chop up all series and also preserve the text in front of it
        episode_list = []

    	# remove span tag with id=recap
    	spans = res.findAll("span", id="recap")
    	[spn.extract() for spn in spans]

    	# remove span tag with id=Trailers
    	spans2 = res.findAll("span", id="Trailers")
    	[spn2.extract() for spn2 in spans2]

    	# remove parent tag of preview image
    	images = res.findAll("img", src="http://www.tvrage.com/_layout_v3/misc/film.gif")
        [mg.parent.extract() for img in images]

    	# process a tag with id=latest
    	images2 = res.findAll("a", id="latest")
        # remove tag
        [lat.extract() for lat in images2]

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
        for ep_text, ep_title in episode_list:
            m = self._re1.match(ep_text)
            if not m:
                m = self._re2.match(ep_text)
            if not m:
                m = self._re3.match(ep_text)
            if not m:
                m = self._re4.match(ep_text)
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
                        datelist = gd["ep_date"].split('/')
                        if len(datelist) > 2:
                            monthstr = datelist[1].lower().strip()
                            if monthstr in _months:
                                try:
                                    epday = int(datelist[0].strip('/'))
                                    epyr = int(datelist[2].strip('/'))
                                    if epyr < 1900:
                                        if epyr > 39:
                                            epyr += 1900
                                        else:
                                            epyr += 2000
                                    datestr = "%04i%s%02i" % (epyr, _months[monthstr], epday)
                                    episode.aired = unicode(datestr)
                                except ValueError:
                                    pass
                
                # add episode
                episode.setPriority("aired", 2)
                episode.series_id = self._series.id                                                
                self._series.episodes.append(episode)

        self.__log.put("Parsing complete!")
        return
    

def _parseTvComDate(s):
    """
    Parses the date in the format:
       MonthName DayNr, YearNr
    """
    l = s.split(' ')    
    # remove all empty pieces
    if l:
        l = [s for s in l if s != '']

    if len(l) < 3:
        return ''
            
    if l[0].lower() in _months:
        month = _months[l[0].lower()]
    else:
        return ''
    
    try:
        daynr = int(l[1].strip(','))
        yearnr = int(l[2])
        if yearnr < 1900:
            if yearnr > 39:
                yearnr += 1900
            else:
                yearnr += 2000
    except ValueError:
        return ''
    
    return "%04i%s%02i" % (yearnr, month, daynr)
    
        
class TvComSeriesDownloadCmd(object):
    """ Extract serie from tv.com site and returns result """
    
    def __init__(self, logqueue, series, url):
        self._series = series
        self.__log = logqueue
        self._url = url
        
        
    def retrieve(self):
        """ Retieves and decodes. 
        """

        self.__log.put("Opening URL : '%s'" % self._url)
        
        # attempt opening URL
        try:
            f = urllib2.urlopen(self._url)
            html = f.read()
        except urllib2.URLError, msg:
            self._series.setError("Error accessing site '%s' for serie '%s' : %s" % \
                                   (self._url, self._series.name, msg))
            return
        except ValueError, msg:
            self._series.setError("Error accessing site '%s' for serie '%s' : %s" % \
                                  (self._url, self._series.id, msg))
            return
            
        self.__log.put("Data for '%s' read. Parsing ..." % self._series.name)
        
        # find first divider for Episodes
        soup = BeautifulSoup(html)
        
        res = soup.find("div", attrs = {"class" :"pod", "section": "episodes"})     
        if not res:
            self._series.setError("Can't find marker #1")
            return
            
        # find table entry where episodes are located in
        res = res.find("table", {"class": "f-11"})
        if not res:
            self._series.setError("Can't find marker #2")
            return
        
        # iterate for series
        res = res.findAll("td", {"class": "f-bold"})
        if not res:
            self._series.setError("Can't find marker #3")
            return
        
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
                
                # find date 
                td_date = r.findNextSibling("td")
                if td_date:
                    txt = td_date.fetchText(text = True)
                    if txt:
                        date_txt = txt[0].strip()
                        episode.aired = unicode(_parseTvComDate(date_txt))
                
                episode.setPriority("aired", 1)
                self._series.episodes.append( episode )
        
        self.__log.put("Parsing complete!")
        return
        
