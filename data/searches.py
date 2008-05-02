#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

from storm.locals import *
from storm.locals import SQL
import re

def _encodeText(s):
    l = s.split(' ')
    l = [s for s in l if s != '']
    return '+'.join(l)

class Searches(object):
    __storm_table__ = "searches"
    id = Int(primary = True)
    name = Unicode()
    url = Unicode()
    show = Int()
    options = Unicode()
    defoptions = Unicode()

    def getSearchURL(self, episode, series):
        """
        @series@     - Series name
        @season_nr@  - Season number like 03 in S03
        @season@     - Season string like S03E01
        @episode_nr@ - Episode number like 01 in E01
        @title@      - Episode title
        """
        
        season_nr = ''
        episode_nr = ''
        
        r = re.compile("S(?P<season>[0-9]+)E(?P<episode>[0-9]+)")
        m = r.search(episode.season)
        if m:
            season_nr = m.group('season')
            episode_nr = m.group('episode')
                    
        lookup = [ ( "@series@",     series.name ),
                   ( "@episode_nr@", episode_nr ), 
                   ( "@season_nr@",  season_nr ),
                   ( "@season@",     episode.season ) ]
        
        # very super lazy replacing
        s = self.url
        for str, rep in lookup:
            s = s.replace(str, _encodeText(rep))
        return s
    
def getDefaultSearch():
    pass
