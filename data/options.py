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
     opt = db.store.find(Options, Options.name == unicode(name)).one()
     if opt:
          return opt.value
     return ''
     
def setOption(name, value):
     opt = db.store.find(Options, Options.name == name).one()
     if opt:
          opt.value = unicode(value)
     else:
          opt = Options()
          opt.name = unicode(name)
          opt.value = unicode(value)
          db.store.add(opt)
     
     db.store.commit()

def getIntOption(name, defaultVal = -1):
     s = getOption(name)
     if s:
          try:
               i = int(s)
               return i
          except ValueError:
               pass
     return defaultVal
     