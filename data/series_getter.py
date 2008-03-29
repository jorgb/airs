import urllib2
from BeautifulSoup import BeautifulSoup

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
		except urllib2.UrlError, msg:
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
				ep_list.append( (number, title) )
		
				
		self.__log.put("Parsing complete!")
		
		if not ep_list:
			return self.__compose_result(None, "No valid series found!")
		else:
			return self.__compose_result(ep_list, "")
	

# testing code!	
if __name__ == "__main__":

	sites = [ ("Supernatural", "http://www.tv.com/supernatural/show/30144/summary.html?q=supernatural&tag=search_results;title;1"), 
	          ("Prison Break", "http://www.tv.com/prison-break/show/31635/summary.html"),
			  ("Heroes", "http://www.tv.com/heroes/show/17552/summary.html?q=heroes&tag=search_results;title;1"),
			  ("new Amsterdam", "http://www.tv.com/new-amsterdam/show/68703/summary.html?q=new%20amsterdam&tag=search_results;title;1")]

	for site_id, site_url in sites:
		print "Testing -- %s"  % site_id
		c = TvComSeriesDownloadCmd(site_id, site_url)
		series_lst, err_str = c.retrieve()
		if err_str:
			print "ERROR: %s" % err_str	
			break