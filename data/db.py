from storm.locals import *
import os.path
from datetime import datetime

VERSION = 1

_db_create_list = [ "CREATE TABLE series (id INTEGER PRIMARY KEY, name VARCHAR, url VARCHAR)",
                    "CREATE TABLE episode (id INTEGER PRIMARY KEY, title VARCHAR, number VARCHAR, " + \
                    "                      season VARCHAR, aired VARCHAR, seen INTEGER, " + \
                    "                      last_in INTEGER, series_id INTEGER)",
                    "CREATE TABLE version (id INTEGER PRIMARY KEY, version INTEGER, updated_on VARCHAR)" ]


class Version(object):
   __storm_table__ = "version"
   id = Int(primary=True)
   version = Int()
   updated_on = Unicode()

   
database = None
store = None
version = None
   

def init(db_filename):
   """
   Initializes the database if it doesn't exist, create one
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
      
      # TODO: In the future maybe some upgrades are needed, we use 
      # the version to see if the database is out of date
      
      
def close():
   """
   Close the database connection
   """
   if store:
      store.close()