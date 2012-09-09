from pymongo import Connection, errors
from django.conf import settings
from directory.models import LBEObjectInstance, OBJECT_IMPORTED

def LbeObjectInstanceToJson(lbeObjectInstance):
	return { '_id': lbeObjectInstance.dn, 
		'attributes': lbeObjectInstance.attributes, 
		'objectType': lbeObjectInstance.object_type,
		'status': OBJECT_IMPORTED
	}

class MongoService:
	def __init__(self):
		self.handler = Connection(settings.MONGODB_SERVER['HOST'], settings.MONGODB_SERVER['PORT'])
		self.db = self.handler[settings.MONGODB_SERVER['DATABASE']]

	def search(self, collection, filters = {}):
		return self.db[collection].find(filters)

	def create(self, collection, lbeObjectInstance):
		db = self.db[collection]
		document = LbeObjectInstanceToJson(lbeObjectInstance)
		try:
			print document
			id = db.insert(document)
			print 'Inserting ', id
		except Exception as e:
			print >> sys.stderr, 'Error: ', e