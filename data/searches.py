#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

from storm.locals import *
from storm.locals import SQL

class Searches(object):
    __storm_table__ = "searches"
    id = Int(primary = True)
    name = Unicode()
    url = Unicode()

    
def getDefaultSearch():
    pass
