#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

from storm.locals import *
from storm.locals import SQL
import re
from data import options, db

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
    

def delete_search(search):
    find_new = False
    id = options.getIntOption("default_search", -1)
    if id == search.id:
        find_new = True

    db.store.remove(search)
    db.store.commit()
    
    if find_new:
        s = db.store.find(Searches, Searches.id == search.id).one()
        next_id = -1
        if s:
            next_id = s.id()
        options.setOption("default_search", str(next_id))

