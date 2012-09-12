from dao.MongoDao import MongoService
from pymongo import errors
from directory.models import LBEObjectInstance, OBJECT_STATE_INVALID
import sys
from django.conf import settings

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
	
	def createObject(self, lbeObjectInstance):
		self.handler.createObject(lbeObjectInstance)
	
	# TODO: Implement per page search
	def searchObjects(self, LBEObjectTemplate, index = 0, size = 0):
		collection = LBEObjectTemplate.name
		filter = { 'status': { '$gt': OBJECT_STATE_INVALID } }
		return self.handler.searchObjects(collection, filter)

class BackendDao(BackendDaoMongo):
	pass
