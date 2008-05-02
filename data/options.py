#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

from storm.locals import *
from storm.locals import SQL
from data import db

class Options(object):
     __storm_table__ = "options"
     id = Int(primary = True)
     name = Unicode()
     value = Unicode()
     
def getOption(name):
     opt = db.store.find(Options, Options.name == name).one()
     if opt:
          return opt.value
     
def setOption(name, value):
     opt = db.store.find(Options, Options.name == name).one()
     if opt:
          opt.value = value
     else:
          opt = Options()
          opt.name = name
          opt.value = value
          db.store.add(opt)
     
     db.store.commit()
