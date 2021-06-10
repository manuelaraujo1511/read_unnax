import pymongo

from django.conf import settings

class DBConnection(object):
  instance=None
  def __new__(cls, *args, **kargs):
    if cls.instance is None:
      cls.instance=object.__new__(cls, *args, **kargs)          
    return cls.instance
  
  def connect(self):
  
    url_connect = "%s:%s/" % (
      settings.DATABASES['mongo_db']['CLIENT']['host'],
      str(settings.DATABASES['mongo_db']['CLIENT']['port'])
    )    
    self.conexion= pymongo.MongoClient("mongodb://%s" % url_connect)
    self.db = self.conexion["unnax_read"]
  
  def get_collection(self, collection):
    self.collect = self.db[collection]
      
  def close(self):
    self.conexion.close()
  