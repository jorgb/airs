#==============================================================================
# Author:      Jorgen Bodde
# Copyright:   (c) Jorgen Bodde
# License:     GPLv2 (see LICENSE.txt)
#==============================================================================

import storm.databases.sqlite
from storm.locals import *
import os.path
from datetime import datetime

VERSION = 2

ALL_OK = 0
UPGRADE_NEEDED = 1

_db_create_list = [ "CREATE TABLE series (id INTEGER PRIMARY KEY, name VARCHAR, url VARCHAR, " + \
                    "                     last_update VARCHAR, update_period INTEGER )",
                    "CREATE TABLE episode (id INTEGER PRIMARY KEY, title VARCHAR, number VARCHAR, " + \
                    "                      season VARCHAR, aired VARCHAR, seen INTEGER, " + \
                    "                      last_in INTEGER, series_id INTEGER, hide_until_update INTEGER)",
                    "CREATE TABLE version (id INTEGER PRIMARY KEY, version INTEGER, updated_on VARCHAR)" ]


_db_update_list = [ ( 1, 2, [ "ALTER TABLE series ADD last_update VARCHAR",
                              "ALTER TABLE series ADD update_period INTEGER",
                              "update series set update_period = 0" ] ) ]

class Version(object):
   __storm_table__ = "version"
   id = Int(primary=True)
   version = Int()
   updated_on = Unicode()

   
database = None
store = None
version = None
   

def init(db_filename, upgrade = False):
   """
   Initializes the database if it doesn't exist, create one. 
   Returns
   """
   global database, store, version
   
   new_db = not os.path.isfile(db_filename)
   
   # create instance
   database = create_database("sqlite:" + db_filename)
   store = Store(database)
   
   # create a new database 
   if new_db:
         for sql_str in _db_create_list:
            store.execute(sql_str)
        
         #  set version
         version = Version()
         version.version = VERSION
         version.updated_on = unicode(datetime.today().strftime("%d-%m-%Y %H:%M:%S"))
        
         store.add(version)
         store.commit()
   else:
      version = store.find(Version).one()

      # run updates if needed, return        
      if version.version < VERSION:
         if not upgrade:
            close()
            return UPGRADE_NEEDED
         else:
            for from_version, to_version, upd_list in _db_update_list:
               if from_version == version.version:
                  for qry in upd_list:
                     store.execute(qry)
                  version.version = to_version
                  version.updated_on = unicode(datetime.today().strftime("%d-%m-%Y %H:%M:%S"))
                  store.commit()
                            
def close():
   """
   Close the database connection
   """
   global database, store
    
   if store:
      store.close()
   store = None
   database = None    