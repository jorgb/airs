#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

from storm.locals import *
from storm.locals import SQL
import os
import datetime
import appcfg


class EpisodeFile(object):
    """
    File belonging to an episode
    """
    __storm_table__ = "episodefile"
    id = Int(primary = True)
    fullpath = Unicode()
    size= Int()
    reldir = Unicode()
    episode_id = Int()
    series_id = Int()
    filetype = Int()

    def __init__(self):
        self.fullpath = u""
        self.size = 0
        self.reldir = u""
        self.episode_id = -1
        self.series_id = -1
        self.filetype = -1
            
