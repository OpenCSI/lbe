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

def LBEObjectInstanceToJSON(lbeObjectInstance):
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

class BackendMongoImpl:
	def __init__(self):
		try:
			self.handler = MongoService()
		except errors.AutoReconnect:
			logging.error("Can't connect to MongoDB server (", settings.MONGODB_SERVER['HOST'], ' ',  settings.MONGODB_SERVER['PORT'], " )")
	
	def createObject(self, lbeObjectInstance):
		return self.handler.createDocument(lbeObjectInstance.objectType, LBEObjectInstanceToJSON(lbeObjectInstance) )
	
	# TODO: Implement per page search
	def searchObjects(self, LBEObjectTemplate, index = 0, size = 0):
		collection = LBEObjectTemplate.name
		filter = { 'status': { '$gt': OBJECT_STATE_INVALID } }
		return DocumentsToLBEObjectInstance(self.handler.searchObjects(collection, filter))
