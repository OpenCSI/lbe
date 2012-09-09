from pymongo import Connection, errors
from django.conf import settings
from directory.models import LBEObjectInstance

def LbeObjectInstanceToJson(lbeObjectInstance):
	return { '_id': lbeObjectInstance.dn, 'attributes': lbeObjectInstance.attributes, 'objectType': lbeObjectInstance.object_type }

class MongoService:
	def __init__(self):
		self.handler = Connection(settings.MONGODB_SERVER['HOST'], settings.MONGODB_SERVER['PORT'])
		self.db = self.handler[settings.MONGODB_SERVER['DATABASE']]

	def search(self):
		pass

	def create(self, collectionName, lbeObjectInstance):
		# self.db[collectionName].insert(json.dumps(lbeObjectInstance, default=convertLbeObjectInstanceToJson))		
		db = self.db[collectionName]
		document = LbeObjectInstanceToJson(lbeObjectInstance)
		try:
			id = db.insert(document)
			print 'Inserting ', id
		except Exception as e:
			print >> sys.stderr, 'Error: ', e