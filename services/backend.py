from dao.MongoDao import MongoService
from pymongo import errors
from directory.models import LBEObjectInstance, OBJECT_INVALID

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

def DocumentsToLBEObjectInstance(documents):
	result_set = []
	for document in documents:
		instance = LBEObjectInstance(document['_id'], document['objectType'], document['attributes'])
		result_set.append(instance)
	return result_set

class BackendDaoMongo:
	def __init__(self):
		try:
			self.handler = MongoService()
		except errors.AutoReconnect:
				print >> sys.stderr, "Can't connect to MongoDB server (", settings.MONGODB_SERVER['HOST'], ' ',  settings.MONGODB_SERVER['PORT'], " )"
	
	def addObject(self, lbeObjectInstance):
		self.handler.create(lbeObjectInstance.object_type, lbeObjectInstance)
	
	# TODO: Implement per page search
	def searchObject(self, LBEObject, index = 0, size = 0):
		collection = LBEObject.name
		filter = { 'status': { '$gt': OBJECT_INVALID } }
		result = self.handler.search(collection, filter)
		return DocumentsToLBEObjectInstance(result) 

class BackendDao(BackendDaoMongo):
	pass