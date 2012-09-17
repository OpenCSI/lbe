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

    def searchDocuments(self, collection, filter = {}):
        logger.debug('Performing MongoDB search on collection: ' + collection + ' with filter: ' + filter.__str__())
        return self.db[collection].find(filter)

    def createDocument(self, collectionName, document):
        collection = self.db[collectionName]
        try:
            id = collection.insert(document)
            logger.debug('MongoDB object id: ' + id + ' created')
            return id
        except BaseException as e:
            logger.error('Error while creating document: ' + e.__str__())
            raise BaseException('an error occured in  mongodb')

    def updateDocument(self, collectionName, filter, changes):
        collection = self.db[collectionName]
        logger.debug('Update MongoDB object in collection ' + collectionName  + ', with query:' + filter.__str__() + ' , with changes: '  + changes.__str__())
        collection = self.db[collectionName]
        collection.update(filter, changes)