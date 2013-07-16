# -*- coding: utf-8 -*-
from dao.MongoDao import MongoService
from pymongo import errors
from directory.models import LBEObjectInstance, OBJECT_STATE_INVALID, OBJECT_STATE_IMPORTED, OBJECT_STATE_AWAITING_SYNC, OBJECT_STATE_AWAITING_APPROVAL, OBJECT_STATE_DELETED
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

def DocumentsToLBEObjectInstance(lbeObjectInstance, documents):
    result_set = []
    for document in documents:
        instance = LBEObjectInstance(lbeObjectInstance, \
            name = document['_id'], \
            displayName = document['displayName'], \
            attributes = document['attributes'], \
            status = document['status'], \
            changes = document['changes']
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

	"""
	Get User values from his UID attribute. §Used for ACLs
	We do not get deleted values.
	"""
    def getUserUIDForObject(self, lbeObjectTemplate, UID):
        searchResult = self.handler.searchDocuments(lbeObjectTemplate.name, { 'attributes.uid': UID, 'status':{'$nin':[OBJECT_STATE_DELETED]} })
        if searchResult.count() > 0:
            return searchResult[0]
        return None
        
    """
    Get User values from his _id attribute.
    """
    def getUserForObject(self, lbeObjectTemplate, uniqueName):
        searchResult = self.handler.searchDocuments(lbeObjectTemplate.name, { '_id': uniqueName })
        if searchResult.count() > 0:
            return searchResult[0]
        return None

    def createObject(self, lbeObjectTemplate, lbeObjectInstance, Import=False):
		if not Import:
			if lbeObjectTemplate.approval:
				awaiting = OBJECT_STATE_AWAITING_APPROVAL
			else:
				awaiting = OBJECT_STATE_AWAITING_SYNC
		else:
			awaiting = OBJECT_STATE_IMPORTED
		return self.handler.createDocument(awaiting,lbeObjectTemplate.name, lbeObjectInstance.toDict() )
        
    """
		Used in Reconciliation:
    """
    def updateObject(self, lbeObjectTemplate, lbeObjectInstance, changes):
        # Changes is already a dict with key = newvalue, no need to transform it
        return self.handler.updateDocument(lbeObjectTemplate.name,lbeObjectInstance, { '_id' : lbeObjectInstance.name.__str__() }, {'$set': changes })
    
    def update_id(self,lbeObjectTemplate, lbeObjectInstance, new_id):
		return self.handler.update_id(lbeObjectTemplate.name,lbeObjectInstance,new_id)

    def modifyDisplayName(self,lbeObjectTemplate, ID, DN):
		return self.handler.modifyDNDocument(lbeObjectTemplate.name,ID,DN)
		
    def modifyObject(self, lbeObjectTemplate, ID, values):
        if lbeObjectTemplate.approval:
            awaiting = OBJECT_STATE_AWAITING_APPROVAL
        else:
            awaiting = OBJECT_STATE_AWAITING_SYNC
        return self.handler.modifyDocument(awaiting,lbeObjectTemplate.name,ID,values)
    
    def removeObject(self,lbeObjectTemplate, ID):
        if lbeObjectTemplate.approval:
            awaiting = OBJECT_STATE_AWAITING_APPROVAL
        else:
            awaiting = OBJECT_STATE_AWAITING_SYNC
        return self.handler.removeDocument(awaiting,lbeObjectTemplate.name,ID)
	
    def deleteObject(self, lbeObjectTemplate, ID):
		return self.handler.deleteDocument(lbeObjectTemplate.name, ID)
	
    def removeAttributeObject(self,lbeObjectTemplate,attribute_name):
		return self.handler.removeAttributeDocument(lbeObjectTemplate,attribute_name)
		
    def approvalObject(self,lbeObjectTemplate, ID):
		return self.handler.approvalDocument(lbeObjectTemplate.name,ID)
        
    def lengthObjects(self,lbeObjectTemplate):
		return self.handler.sizeDocuments(lbeObjectTemplate.name,{ 'status': { '$gt': OBJECT_STATE_INVALID } })
	
    def positionObject(self,lbeObjectTemplate,ID):
		return self.handler.posDocument(lbeObjectTemplate,ID)	
		
    def searchObjects(self, lbeObjectTemplate, index = 0, size = 0):
        return DocumentsToLBEObjectInstance(lbeObjectTemplate, self.handler.searchDocuments(lbeObjectTemplate.name, { 'status': { '$gt': OBJECT_STATE_INVALID } }, index, size))
	
    def searchObjectsByPattern(self, lbeObjectTemplate, pattern):
        value = {}
        if pattern != '':
            _id = {'_id':{'$regex' : pattern, '$options' : 'i'}}
            _valid = {'status' : { '$gt' : OBJECT_STATE_INVALID }}
			
            value['$and'] = []
            value['$and'].insert(0,_id)
            value['$and'].insert(1,_valid)
        else:
            value['status'] = {}
            value['status']['$gt'] = OBJECT_STATE_INVALID
        return DocumentsToLBEObjectInstance(lbeObjectTemplate, self.handler.searchDocuments(lbeObjectTemplate.name, value, 0, 0))
        
    # Search objects with synced_at <= lbeObjectTemplate.synced_at
    def searchObjectsToUpdate(self, lbeObjectTemplate, index = 0, size = 0):
        return DocumentsToLBEObjectInstance(lbeObjectTemplate, self.handler.searchDocuments(lbeObjectTemplate.name, { 'status': OBJECT_STATE_AWAITING_SYNC }, index, size))
