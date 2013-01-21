import datetime
from directory.models import LBEObjectTemplate, OBJECT_CHANGE_CREATE_OBJECT,OBJECT_CHANGE_DELETE_OBJECT,OBJECT_CHANGE_UPDATE_OBJECT, LBEObjectInstance, OBJECT_STATE_SYNCED, OBJECT_STATE_DELETED
from services.backend import BackendHelper
from services.target import TargetHelper
from django.core.management.base import BaseCommand, CommandError
import ldap
import logging

logger = logging.getLogger(__name__)
#
# Algoritm used for reconciliation:
#
# First step (manage update):
#   - look for all need to be synced objects
#
# Second step (manage object than exists in target but not in backend):
# last_sync = now()
# Foreach object in target:
#   - check if object exists in backend
#   - if no:
#       - Delete object if RECONCILIATION_OBJECT_MODE = 'DELETE'
#       - Create object if RECONCILIATION_OBJECT_MODE = 'CREATE'
#   - else:
#       - apply changeset defined in backend for this object
#       - if RECONCILIATION_ATTRIBUTES_MODE = 'DELETE':
#               - delete target attributes not defined in object template
#
#
# Looking for all object to create:
# foreach object in backend where _synced_at < last_sync
#   - create object in target

class Reconciliation():
    def __init__(self):
        self.backend = BackendHelper()
        self.target = TargetHelper()
        self.start_date = datetime.datetime.now()

    def createObject(self, lbeObjectTemplate, lbeObjectInstance):
        pass

    def start(self):
        # First of all, applies all changes stored in backend
        
        for objectTemplate in LBEObjectTemplate.objects.all():
            # We're looking for all objects with state = OBJECT_STATE_AWAITING_SYNC
            for objectInstance in self.backend.searchObjectsToUpdate(objectTemplate):
                logger.debug('Object to create or update: ' + objectInstance.name)
                if objectInstance.changes['type'] == OBJECT_CHANGE_CREATE_OBJECT:
                    print "create"
                    try:
                        self.target.create(objectTemplate, objectInstance)
                        # Ok, the object is added, empty changes set, and update object status
                        changes = {}
                        changes['status'] = OBJECT_STATE_SYNCED
                        changes['changes'] = {}
                        changes['changes']['set'] = {}
                        changes['changes']['type'] = -1
                        changes['synced_at'] = datetime.datetime.now()
                        self.backend.updateObject(objectTemplate, objectInstance, changes)
                    # TODO: We should have a target exception rather ldap
                    except ldap.ALREADY_EXISTS:
                        logger.debug('Object "' + objectInstance.name + '" already exists')
                        print 'Object ' + objectInstance.name + ' already exists'
                        pass
                elif objectInstance.changes['type'] == OBJECT_CHANGE_DELETE_OBJECT:
                    print "delete"
                    try:
                        self.target.delete(objectTemplate, objectInstance)
                        # Update Backend value:
                        changes = {}
                        changes['status'] = OBJECT_STATE_DELETED
                        changes['changes'] = {}
                        changes['changes']['set'] = {}
                        changes['changes']['type'] = -1
                        changes['synced_at'] = datetime.datetime.now()
                        self.backend.updateObject(objectTemplate, objectInstance, changes)
                    except Exception as e:
                        print e
                        pass
                elif objectInstance.changes['type'] == OBJECT_CHANGE_UPDATE_OBJECT:
                    print "update"


class Command(BaseCommand):
    def handle(self, *args, **options):
        reconciliation = Reconciliation()
        reconciliation.start()
