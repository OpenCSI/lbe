# -*- coding: utf-8 -*-
from dao.MongoDao import MongoService
from pymongo import errors
from directory.models import LBEObjectInstance, OBJECT_STATE_INVALID, OBJECT_STATE_IMPORTED, OBJECT_STATE_AWAITING_SYNC
from django.utils.timezone import utc
import logging, datetime


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

def LBEObjectInstanceToDict(lbeObjectInstance):
    # TODO: Probably need optimization
    return { '_id': lbeObjectInstance.name, 
        'attributes': lbeObjectInstance.attributes, 
        'displayName': lbeObjectInstance.displayName,
        'status': lbeObjectInstance.status,
        'created_at': lbeObjectInstance.created_at,
        'updated_at': lbeObjectInstance.updated_at,
        'synced_at': lbeObjectInstance.synced_at,
        'changes_set': lbeObjectInstance.changesSet,
    }

def DocumentsToLBEObjectInstance(lbeObjectInstance, documents):
    result_set = []
    for document in documents:
        instance = LBEObjectInstance(lbeObjectInstance, \
            name = document['_id'], \
            displayName = document['displayName'], \
            attributes = document['attributes'], \
            status = document['status'], \
            changesSet = document['changes_set']
        )
        result_set.append(instance)
    return result_set

class BackendMongoImpl:
    def __init__(self):
        try:
            self.handler = MongoService()
        except errors.AutoReconnect:
            logging.error("Can't connect to MongoDB server (", settings.MONGODB_SERVER['HOST'], ' ',  settings.MONGODB_SERVER['PORT'], " )")
            raise BackendConnectionError("Can't connect to the backend server")

    def getObjectByName(self, lbeObjectTemplate, uniqueName):
        searchResult = self.handler.searchDocuments(lbeObjectTemplate.name, { '_id': uniqueName })
        print searchResult.count()
        if searchResult.count() > 0:
            return searchResult[0]
        return None

    def createObject(self, lbeObjectTemplate, lbeObjectInstance):
        return self.handler.createDocument(lbeObjectTemplate.name, LBEObjectInstanceToDict(lbeObjectInstance) )
    
    # TODO: Implement per page search
    def searchObjects(self, lbeObjectTemplate, index = 0, size = 0):
        return DocumentsToLBEObjectInstance(lbeObjectTemplate, self.handler.searchDocuments(lbeObjectTemplate.name, { 'status': { '$gt': OBJECT_STATE_INVALID } }))

    # Search objects with synced_at <= lbeObjectTemplate.synced_at
    def searchObjectsToUpdate(self, lbeObjectTemplate, index = 0, size = 0):
        return DocumentsToLBEObjectInstance(lbeObjectTemplate, self.handler.searchDocuments(lbeObjectTemplate.name, { 'status': OBJECT_STATE_AWAITING_SYNC }))
