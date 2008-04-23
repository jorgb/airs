#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import storm.databases.sqlite
from storm.locals import *
import os.path
import db_sqlite

ALL_OK = 0
UPGRADE_NEEDED = 1
UPGRADE_FAILED = 2
DB_OK = 4

class Version(object):
   __storm_table__ = "version"
   id = Int(primary=True)
   version = Int()
   updated_on = Unicode()
   
database = None
store = None
version = None
   

def _setup_db(db_filename):
   global database, store

   # create instance
   database = create_database("sqlite:" + db_filename.encode('utf-8'))
   store = Store(database)


def _close():
   """
   Close the database connection
   """
   global database, store
    
   if store:
      store.close()
   store = None
   database = None      
   
   
def init(db_filename, upgrade = False):
   """ 
   Initializes the database if it doesn't exist, create one. 
   """   

   new_db = not os.path.isfile(db_filename)
   
   if new_db:
      db_sqlite.create(db_filename)
   _setup_db(db_filename)           

   version = store.find(Version).one()
   if version.version < db_sqlite.VERSION:      
      # perform upgrade if needed
      _close()
      
      if not upgrade:
         return UPGRADE_NEEDED
      else:
         if not db_sqlite.upgrade(db_filename):
            return UPGRADE_FAILED
      
      _setup_db(db_filename)
      
   return DB_OK
 