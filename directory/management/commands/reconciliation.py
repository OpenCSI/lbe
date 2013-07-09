import datetime
from directory.models import LBEObjectTemplate, OBJECT_CHANGE_CREATE_OBJECT,OBJECT_CHANGE_DELETE_OBJECT,OBJECT_CHANGE_UPDATE_OBJECT, LBEObjectInstance, OBJECT_STATE_SYNCED, OBJECT_STATE_DELETED
from services.backend import BackendHelper
from services.target import TargetHelper
from services.object import LBEObjectInstanceHelper
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import ldap
import logging
import ldap.modlist as modlist

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

    def createParent(self, lbeObjectTemplate, objService):
		base_dn = objService.callScriptMethod("base_dn")
		objectToCreate = base_dn.replace(settings.LDAP_SERVER['BASE_DN'],'')[:-1].split(',')
		objectToCreate.reverse()
		for i in range(0,len(objectToCreate)):
			dn = objectToCreate[i] + ','
			for j in range(0,i):
				dn  = dn + objectToCreate[j] + ','
			dn = dn + settings.LDAP_SERVER['BASE_DN']
			attrs = {}
			attrs['objectclass'] = ['top','organizationalUnit']
			# do not care if the ou already exists
			try:
			    self.target.createParent(dn,modlist.addModlist(attrs))
			except:
				pass
			
    def _createObject(self,objectTemplate,objectInstance):
        self.target.create(objectTemplate, objectInstance)
        # Ok, the object is added, empty changes set, and update object status
        changes = {}
        changes['status'] = OBJECT_STATE_SYNCED
        changes['changes'] = {}
        changes['changes']['set'] = {}
        changes['changes']['type'] = -1
        changes['synced_at'] = datetime.datetime.now()
        self.backend.updateObject(objectTemplate, objectInstance, changes)
        
    def _modifyObject(self,objectTemplate,objectInstance):
        rdnAttributeName = objectTemplate.instanceNameAttribute.name
        self.target.update(objectTemplate,objectInstance)
        if not objectInstance.attributes[rdnAttributeName][0] == objectInstance.changes['set'][rdnAttributeName][0]:
			self.backend.update_id(objectTemplate,objectInstance,objectInstance.changes['set'][rdnAttributeName][0])
        # Update Backend value:
        changes = {}
        changes['status'] = OBJECT_STATE_SYNCED
        changes['changes'] = {}
        changes['changes']['set'] = {}
        changes['changes']['type'] = -1
        changes['synced_at'] = datetime.datetime.now()
        self.backend.updateObject(objectTemplate, objectInstance, changes)
       
    def _deleteObject(self,objectTemplate,objectInstance):
		self.target.delete(objectTemplate, objectInstance)
		# Update Backend value:
		changes = {}
		changes['status'] = OBJECT_STATE_DELETED
		changes['changes'] = {}
		changes['changes']['set'] = {}
		changes['changes']['type'] = -1
		changes['synced_at'] = datetime.datetime.now()
		self.backend.updateObject(objectTemplate, objectInstance, changes)
     		

    def start(self):
        for objectTemplate in LBEObjectTemplate.objects.all():
            # We're looking for all objects with state = OBJECT_STATE_AWAITING_SYNC
            for objectInstance in self.backend.searchObjectsToUpdate(objectTemplate):
				# First of all, applies all changes stored in backend [ such Virtual attributes ]  
				# & create the parent DN if not exist:
                obj = LBEObjectInstanceHelper(objectTemplate,objectInstance)
                self.createParent(objectTemplate,obj)
                obj.compute(objectInstance)
                # then, upgrade:
                logger.debug('Object to create or update: ' + objectInstance.name)
                if objectInstance.changes['type'] == OBJECT_CHANGE_CREATE_OBJECT:
                    try:
                        print "Object '" + objectInstance.name + "' is creating."
                        self._createObject(objectTemplate, objectInstance)
                    # TODO: We should have a target exception rather ldap
                    except ldap.ALREADY_EXISTS:
                        logger.debug('Object "' + objectInstance.name + '" already exists')
                        print 'Object ' + objectInstance.name + ' already exists'
                        pass
                elif objectInstance.changes['type'] == OBJECT_CHANGE_DELETE_OBJECT:
                    try:
                        print "Object '" + objectInstance.name + "' is deleting."
                        self._deleteObject(objectTemplate, objectInstance)
                    except BaseException as e:
                        logger.debug('Object "' + objectInstance.name + '" does not exist')
                        print 'Object ' + objectInstance.name + ' does not exist.'
                        changes = {}
                        changes['status'] = OBJECT_STATE_DELETED
                        changes['changes'] = {}
                        changes['changes']['set'] = {}
                        changes['changes']['type'] = -1
                        changes['synced_at'] = datetime.datetime.now()
                        self.backend.updateObject(objectTemplate, objectInstance, changes)
                        pass
                elif objectInstance.changes['type'] == OBJECT_CHANGE_UPDATE_OBJECT:
                    try:
                        print "Object '" + objectInstance.name + "' is updating."
                        self._modifyObject(objectTemplate, objectInstance)
                    except BaseException as e:
                        print e
                        print "Object '" + objectInstance.name + "' does not exist, being created."
                        # Create object if not exists:
                        # Firstly, compute attributes values:
                        # Then, create it:
                        try:
                            self._createObject(objectTemplate, objectInstance)
                        except Exception as e:
							print e
							pass
                        pass


class Command(BaseCommand):
    def handle(self, *args, **options):
        reconciliation = Reconciliation()
        reconciliation.start()
