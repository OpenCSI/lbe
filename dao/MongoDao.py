# -*- coding: utf-8 -*-
from pymongo import Connection, errors
from django.conf import settings
from directory.models import LBEObjectInstance, OBJECT_STATE_IMPORTED
import sys, logging

logger = logging.getLogger(__name__)

class MongoService:
	def __init__(self):
		self.handler = Connection(settings.MONGODB_SERVER['HOST'], settings.MONGODB_SERVER['PORT'])
		self.db = self.handler[settings.MONGODB_SERVER['DATABASE']]

	def searchObjects(self, collection, filters = {}):
		return self.db[collection].find(filters)

	def createDocument(self, collection, document):
		db = self.db[collection]
		try:
			# TODO: remove print
			print document
			id = db.insert(document)
			return id
		except Exception as e:
			print >> sys.stderr, 'Error while creating document: ', e

# Pensee
# Dans le cas d'un target LDAP, on utilise ce champ pour calculer le DN à partir d'une méthode définie dans le script

# Pour faire une recherche LDAP, on appelle les methodes base_dn, object_classes du script lié à l'objet
# Puis on utilise la valeur du champ uniqueAttribute pour savoir quel champ lire

# Dans le cas d'un target MongoDB, on utilise une collection par type d'objet, donc on peut utiliser ce champ comme _id
