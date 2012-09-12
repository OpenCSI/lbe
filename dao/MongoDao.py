from pymongo import Connection, errors
from django.conf import settings
from directory.models import LBEObjectInstance, OBJECT_STATE_IMPORTED

# TODO: This methods must be implemented in the models, or maybe the helper but not here
def LbeObjectInstanceToJson(lbeObjectInstance):
	return { '_id': lbeObjectInstance.dn, 
		'attributes': lbeObjectInstance.attributes, 
		'displayName': lbeObjectInstance.displayName,
		'status': OBJECT_STATE_IMPORTED,
		'objectType': lbeObjectInstance.objectType,
	}

def DocumentsToLBEObjectInstance(documents):
	result_set = []
	for document in documents:
		instance = LBEObjectInstance(document['_id'], document['objectType'], document['displayName'], document['attributes'])
		# Must be override by hand
		instance.setStatus(document['status'])
		result_set.append(instance)
	return result_set

class MongoService:
	def __init__(self):
		self.handler = Connection(settings.MONGODB_SERVER['HOST'], settings.MONGODB_SERVER['PORT'])
		self.db = self.handler[settings.MONGODB_SERVER['DATABASE']]

	def searchObjects(self, collection, filters = {}):
		return DocumentsToLBEObjectInstance(self.db[collection].find(filters))

	def createObject(self, lbeObjectInstance):
		db = self.db[lbeObjectInstance.objectType]
		document = LbeObjectInstanceToJson(lbeObjectInstance)
		try:
			print document
			id = db.insert(document)
			print 'Inserting ', id
		except Exception as e:
			print >> sys.stderr, 'Error: ', e
