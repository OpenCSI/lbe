from dao.MongoDao import MongoService
from pymongo import errors

class BackendConnectionError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class BackendInvalidCredentials(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class BackendDaoMongo:
	def __init__(self):
		try:
			self.handler = MongoService()
		except errors.AutoReconnect:
				print >> sys.stderr, "Can't connect to MongoDB server (", settings.MONGODB_SERVER['HOST'], ' ',  settings.MONGODB_SERVER['PORT'], " )"
	
	def addObject(self, lbeObjectInstance):
		self.handler.create('collection', lbeObjectInstance)

class BackendDao(BackendDaoMongo):
	pass