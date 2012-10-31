# -*- coding: utf-8 -*-
from pymongo import Connection, errors
from django.conf import settings
from directory.models import LBEObjectInstance, OBJECT_STATE_IMPORTED, OBJECT_STATE_AWAITING_SYNC, OBJECT_CHANGE_UPDATE_OBJECT
import sys, logging

import datetime
from django.utils.timezone import utc

logger = logging.getLogger(__name__)

class MongoService:
    def __init__(self):
        self.handler = Connection(settings.MONGODB_SERVER['HOST'], settings.MONGODB_SERVER['PORT'])
        self.db = self.handler[settings.MONGODB_SERVER['DATABASE']]

    def searchDocuments(self, collection, filters = {}):
        logger.debug('Performing MongoDB search on collection: ' + collection + ' with filter: ' + filters.__str__())
        return self.db[collection].find(filters)

    def createDocument(self, collection, document):
        db = self.db[collection]
        try:
            id = db.insert(document)
            logger.debug('MongoDB object id: ' + id + ' created')
            return id
        except BaseException as e:
            logger.error('Error while creating document: ' + e.__str__())
	
    def modifyDocument(self, collection, ID, values):
        db = self.db[collection]
        try:
			# Get ID values:
            changeSet = self.searchDocuments(collection,{'_id':ID})[0]['changes']['set']
            # change the set dict with new values:
            # In order to not lose values:
            newValues = {} # new dict because 'values' is QueryDict.
            # replace values:
            print changeSet
            for kset in changeSet:
				if not values.has_key(kset):
					newValues[kset] = changeSet[kset] # get other values
				else:
					print values[kset]
					if isinstance(values[kset],unicode) or isinstance(values[kset],str):
						newValues[kset] = [ values[kset] ] # new values
					else:
						newValues[kset] = values[kset] # new values
			# add new (key) value:
            for kval in values:
                if not newValues.has_key(kval):
                    newValues[kval] = [ values[kval] ]
            # set status for changes:
            newValues['status'] = OBJECT_CHANGE_UPDATE_OBJECT
            # updage Mongo:
            db.update({'_id':ID},{'$set':{'changes':{'set':newValues}}})
            # TO IMPROVE:
            db.update({'_id':ID},{'$set':{'updated_at':datetime.datetime.now(utc)}})
            return db.update({'_id':ID},{'$set':{'status':OBJECT_STATE_AWAITING_SYNC}})
        except BaseException as e:
            logger.error('Error while modifying document: ' + e.__str__())
		
# Pensee
# Dans le cas d'un target LDAP, on utilise ce champ pour calculer le DN à partir d'une méthode définie dans le script

# Pour faire une recherche LDAP, on appelle les methodes base_dn, object_classes du script lié à l'objet
# Puis on utilise la valeur du champ instanceNameAttribute pour savoir quel champ lire

# Dans le cas d'un target MongoDB, on utilise une collection par type d'objet, donc on peut utiliser ce champ comme _id
