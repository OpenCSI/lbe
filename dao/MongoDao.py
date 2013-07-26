# -*- coding: utf-8 -*-
import sys
import logging

from pymongo import Connection, errors
from django.conf import settings

from directory.models import LBEObjectInstance, OBJECT_CHANGE_CREATE_OBJECT, OBJECT_STATE_IMPORTED, OBJECT_STATE_AWAITING_SYNC, OBJECT_STATE_DELETED, OBJECT_CHANGE_UPDATE_OBJECT, OBJECT_CHANGE_DELETE_OBJECT

#from services.backend import BackendHelper

import datetime
from django.utils.timezone import utc

logger = logging.getLogger(__name__)


class MongoService:
    def __init__(self):
        self.handler = Connection(settings.MONGODB_SERVER['HOST'], settings.MONGODB_SERVER['PORT'])
        self.db = self.handler[settings.MONGODB_SERVER['DATABASE']]
        if not settings.MONGODB_SERVER['USER'] == '':
            try:
                self.db.authenticate(settings.MONGODB_SERVER['USER'],settings.MONGODB_SERVER['PASSWORD'])
            except BaseException as e:
                raise Connection("Cannot connect to the Backend Server, please make sure the authentification data is correct.")

    def searchDocuments(self, collection, filters={}, index=0, size=0):
        logger.debug('Performing MongoDB search on collection: ' + collection + ' with filter: ' + filters.__str__())
        return self.db[collection].find(filters).skip(index).limit(size)

    def sizeDocuments(self, collection, filters={}):
        logger.debug('Performing MongoDB size on collection: ' + collection + ' with filter: ' + filters.__str__())
        return self.db[collection].find(filters).count()

    def posDocument(self, collection, id):
        array = self.db[collection].find({}, {'_id': ''})
        i = 0
        for value in array:
            i += 1
            if value['_id'] == id:
                return i
        return 0

    def createDocument(self, awaiting, collection, document):
        db = self.db[collection]
        try:
            document['status'] = awaiting
            id = db.insert(document)
            logger.debug('MongoDB object id: ' + id + ' created')
            return id
        except BaseException as e:
            logger.error('Error while creating document: ' + e.__str__())

    def createGroup(self, lbeGroupTemplate):
        db = self.db["groups"]
        try:
            return db.insert(lbeGroupTemplate.toDict())
        except BaseException as e:
            print "Error to save the group: " + str(e)

    def modifyGroup(self, lbeGroupTemplate, lbeGroupInstance, oldObjectTemplate, oldNameObjectTemplate):
        db = self.db["groups"]
        try:
            # check if objectTemplate is changed
            if not oldObjectTemplate.id == lbeGroupTemplate.objectTemplate.id:
                lbeGroupInstance.changes['set']['uniqueMember'] = []
            # new name
            if not oldNameObjectTemplate == lbeGroupInstance.name:
                lbeGroupInstance.changes['set']['cn'] = lbeGroupInstance.name
            print lbeGroupInstance.toDict()
            #return db.update() # TODO
        except BaseException as e:
            print e

    def saveGroup(self, lbeGroupTemplate, lbeGroupInstance):
        db = self.db["groups"]
        try:
            if lbeGroupInstance.changes['set'] == {} and lbeGroupInstance.changes['set'] == lbeGroupInstance.attributes:
                raise Exception("The Group does not need to be saved (not modified)")
            return db.update({'_id': lbeGroupTemplate.name}, {'$set': {'changes': {'set':
                                                                                       lbeGroupInstance.changes['set'], 'type': OBJECT_CHANGE_UPDATE_OBJECT},
                                                                       'updated_at': datetime.datetime.now(utc), 'status': OBJECT_STATE_AWAITING_SYNC}})
        except BaseException as e:
            print e

    def approvalDocument(self, collection, ID):
        db = self.db[collection]
        try:
            return db.update({'_id': ID}, {'$set': {'status': OBJECT_STATE_AWAITING_SYNC}})
        except BaseException as e:
            logger.error('Error while approval document: ' + e.__str__())

    def update_id(self, collection, document, new_id):
        db = self.db[collection]
        try:
            db.remove({'_id': document.name})
            document.name = new_id
            db.insert(document.toDict())
        except BaseException as e:
            logger.error('Error while update _id"s document: ' + e.__str__())
            print e

    def modifyDNDocument(self, collection, ID, DN):
        db = self.db[collection]
        try:
            db.update({'_id': ID}, {'$set': {'displayName': DN}})
        except BaseException as e:
            logger.error('Error while modifying DisplayName document: ' + e.__str__())

    def modifyDocument(self, awaiting, collection, ID, values, displayName):
        db = self.db[collection]
        try:
        # Get Data values:
            collection = self.searchDocuments(collection, {'_id': ID})[0]
            change = collection['changes']
            changeSet = change['set']
            # check if values changed:
            if (not collection['changes']['set'] == {} and values == collection['changes']['set']) \
                or (collection['changes']['set'] == {} and values == collection['attributes']):
                raise Exception("The Object does not need to be saved (same values).")
                # set status for changes:
            if collection.has_key('status'):
                if collection['status'] == 4 or change[
                    'type'] == 0: # OBJECT_STATE_DELETED or OBJECT_CHANGE_CREATE_OBJECT
                    type = OBJECT_CHANGE_CREATE_OBJECT
                else:
                    type = OBJECT_CHANGE_UPDATE_OBJECT
            else:
                type = OBJECT_CHANGE_UPDATE_OBJECT
                # updage Mongo:
            return db.update({'_id': ID}, {
            '$set': {'changes': {'set': values, 'type': type}, 'displayName': displayName,
                     'updated_at': datetime.datetime.now(utc), 'status': awaiting}})
        except BaseException as e:
            logger.error('Error while modifying document: ' + e.__str__())
            if e.__str__() == "The Object does not need to be saved (same values).":
                raise KeyError("The Object does not need to be saved (same values).")

    def updateDocument(self, collectionName, lbeObjectInstance, filter, changes):
        collection = self.db[collectionName]
        logger.debug(
            'Update MongoDB object in collection ' + collectionName + ', with query:' + filter.__str__() + ' , with changes: ' + changes.__str__())
        collection = self.db[collectionName]
        # Update Attributes:
        attributes = {}
        attributes['attributes'] = {}
        for key, val in lbeObjectInstance.changes['set'].items():
            attributes['attributes'][key] = val
        collection.update(filter, changes)
        # Do not apply attributes save if changes.set is empty:
        if not lbeObjectInstance.changes['set'] == {}:
            collection.update(filter, {'$set': attributes})

    def removeDocument(self, awaiting, collection, ID):
        db = self.db[collection]
        try:
            return db.update({'_id': ID}, {
            '$set': {'status': awaiting, 'changes': {'set': {}, 'type': OBJECT_CHANGE_DELETE_OBJECT}}})
        except BaseException as e:
            logger.error('Error while removing document: ' + e.__str__())

    def deleteDocument(self, collection, ID):
        db = self.db[collection]
        try:
            return db.remove({'_id': ID})
        except BaseException as e:
            logger.error('Error while removing document: ' + e.__str__())

    def removeAttributeDocument(self, collection, attribute_name):
        db = self.db[collection]
        try:
            # Attribute Field:
            res = db.update({}, {'$unset': {'attributes': {attribute_name: 1}}}, multi=True)
            # Changes['set'] Field:
            res += db.update({}, {'$unset': {'changes': {'set': {attribute_name: 1}}}}, multi=True)
            return res
        except BaseException as e:
            logger.error('Error while removing attribute document: ' + e.__str__())
