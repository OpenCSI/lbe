# -*- coding: utf-8 -*-
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
		instance.set_status(document['status'])
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

# Pensee
# Renommer rdnAttribute en uniqueAttribute, pour faire plus générique
# Dans le cas d'un target LDAP, on utilise ce champ pour calculer le DN à partir d'une méthode définie dans le script

# Pour faire une recherche LDAP, on appelle les methodes base_dn, object_classes du script lié à l'objet
# Puis on utilise la valeur du champ uniqueAttribute pour savoir quel champ lire

# Dans le cas d'un target MongoDB, on utilise une collection par type d'objet, donc on peut utiliser ce champ comme _id