# -*- coding: utf-8 -*-
from dao.MongoDao import MongoService
from pymongo import errors
from directory.models import LBEObjectInstance, OBJECT_STATE_INVALID, OBJECT_STATE_IMPORTED
import logging

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
        'synced_at': lbeObjectInstance.synced_at
    }

def DocumentsToLBEObjectInstance(lbeObjectInstance, documents):
    result_set = []
    for document in documents:
        instance = LBEObjectInstance(lbeObjectInstance, name = document['_id'], displayName = document['displayName'], attributes = document['attributes'], status = document['status'])
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
        return self.handler.searchObjects(lbeObjectTemplate.name, { '_id': uniqueName })

    def createObject(self, lbeObjectTemplate, lbeObjectInstance):
        return self.handler.createDocument(lbeObjectTemplate.name, LBEObjectInstanceToDict(lbeObjectInstance) )
    
    # TODO: Implement per page search
    def searchObjects(self, lbeObjectTemplate, index = 0, size = 0):
        collection = lbeObjectTemplate.name
        filter = { 'status': { '$gt': OBJECT_STATE_INVALID } }
        return DocumentsToLBEObjectInstance(lbeObjectTemplate, self.handler.searchObjects(collection, filter))
