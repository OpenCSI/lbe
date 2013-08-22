# -*- coding: utf-8 -*-
import logging


from pymongo import Connection
from django.conf import settings

from directory.models import OBJECT_CHANGE_CREATE_OBJECT, OBJECT_STATE_AWAITING_SYNC, OBJECT_CHANGE_UPDATE_OBJECT,\
    OBJECT_CHANGE_DELETE_OBJECT, OBJECT_STATE_SYNCED, OBJECT_STATE_AWAITING_RECONCILIATION, OBJECT_STATE_AWAITING_APPROVAL

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
                raise Connection("Cannot connect to the Backend Server, please make sure the authentication data is correct.")

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

    def modifyGroup(self, groupInstanceHelper, oldObjectTemplate, oldNameGroup):
        db = self.db["groups"]
        try:
            # check if objectTemplate is changed
            if not oldObjectTemplate.id == groupInstanceHelper.template.objectTemplate.id:
                groupInstanceHelper.instance.changes['set'][groupInstanceHelper.attributeName] = []
            else:
                # get the members changes.set value
                documents = db.find({'_id': oldNameGroup})
                for document in documents:
                    try:
                        if document['status'] == OBJECT_STATE_SYNCED:
                            groupInstanceHelper.instance.changes['set'][groupInstanceHelper.attributeName] = document['attributes'][groupInstanceHelper.attributeName]
                        else:
                            groupInstanceHelper.instance.changes['set'][groupInstanceHelper.attributeName] = document['changes']['set'][groupInstanceHelper.attributeName]
                        groupInstanceHelper.instance.attributes = document['attributes']
                    except BaseException:  # no key value
                        groupInstanceHelper.instance.changes['set'][groupInstanceHelper.attributeName] = []
            # new name
            if not oldNameGroup == groupInstanceHelper.template.displayName:
                groupInstanceHelper.instance.changes['set']['cn'] = [groupInstanceHelper.template.displayName]
            db.update({'_id': oldNameGroup}, {
                '$set': {'changes': {'set': groupInstanceHelper.instance.changes['set'], 'type': OBJECT_CHANGE_UPDATE_OBJECT},
                         'displayName': groupInstanceHelper.template.displayName,
                         'updated_at': datetime.datetime.now(utc), 'status': OBJECT_STATE_AWAITING_SYNC}})
            groupInstanceHelper.instance.name = oldNameGroup
            groupInstanceHelper.instance.status = OBJECT_STATE_AWAITING_SYNC
            groupInstanceHelper.instance.changes['type'] = OBJECT_CHANGE_UPDATE_OBJECT
            return self.update_id('groups', groupInstanceHelper.instance, groupInstanceHelper.template.displayName)
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
            document.status = OBJECT_STATE_AWAITING_RECONCILIATION
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

    def updateStatus(self, collectionName, ID):
        collection = self.db[collectionName]
        object = self.searchDocuments(collectionName, {'_id': ID})[0]
        status = OBJECT_STATE_SYNCED
        if not object['changes']['set'] == {}:
            status = OBJECT_CHANGE_UPDATE_OBJECT
        return collection.update({'_id': ID}, {'$set': {'status': status}})

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
