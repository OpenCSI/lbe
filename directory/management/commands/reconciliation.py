import datetime
from directory.models import LBEObjectTemplate, OBJECT_CHANGE_CREATE_OBJECT,OBJECT_CHANGE_DELETE_OBJECT, \
OBJECT_CHANGE_UPDATE_OBJECT, LBEObjectInstance, OBJECT_STATE_SYNCED, OBJECT_STATE_DELETED, LBEReconciliation, \
 OBJECT_ADD_BACKEND,OBJECT_DELETE_TARGET, TARGET, BACKEND
from services.backend import BackendHelper
from services.target import TargetHelper
from services.object import LBEObjectInstanceHelper
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import ldap
import django
import logging
import ldap.modlist as modlist
from django.conf import settings

logger = logging.getLogger(__name__)

class Reconciliation():
    def __init__(self):
        self.backend = BackendHelper()
        self.target = TargetHelper()
        self.start_date = django.utils.timezone.now()
        self.reconciliation_policy = LBEReconciliation.objects.get(id=1)

    def _changeRDN(self,objectTemplate):
        if objectTemplate.needReconciliationRDN:
            print "    |-> Upgrade the RDN Target server for \033[35m" + objectTemplate.name + "\033[0m..."
            # Change the RDN Attribute to the Target Server
            ob = self.backend.searchObjects(objectTemplate)
            for o in ob:
                try:
                    self.target.changeRDN(objectTemplate,o,objectTemplate.instanceNameBeforeAttribute.name,o.attributes[objectTemplate.instanceNameBeforeAttribute.name][0])
                except BaseException:
					# if object does not exists into the Target Server
					pass
            # Update values for changing RDN attribute
            objectTemplate.instanceNameBeforeAttribute = None
            objectTemplate.needReconciliationRDN = False
            objectTemplate.save()
            print "    |-> Done."

    def _createParent(self, lbeObjectTemplate, objService):
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
			    self.target._createParent(dn,modlist.addModlist(attrs))
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
        changes['synced_at'] =  django.utils.timezone.now()
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
        changes['synced_at'] =  django.utils.timezone.now()
        self.backend.updateObject(objectTemplate, objectInstance, changes)
       
    def _deleteObject(self,objectTemplate,objectInstance):
		self.target.delete(objectTemplate, objectInstance)
		# Update Backend value:
		changes = {}
		changes['status'] = OBJECT_STATE_DELETED
		changes['changes'] = {}
		changes['changes']['set'] = {}
		changes['changes']['type'] = -1
		changes['synced_at'] = django.utils.timezone.now()
		self.backend.updateObject(objectTemplate, objectInstance, changes)
     		
    def start(self):
        print "   Upgrade the Target server with the Backend server..."
        for objectTemplate in LBEObjectTemplate.objects.all():
            # need to check if we need to change before making reconciliation the RDN attribute
            self._changeRDN(objectTemplate)
            # We're looking for all objects with state = OBJECT_STATE_AWAITING_SYNC
            for objectInstance in self.backend.searchObjectsToUpdate(objectTemplate):
				# First of all, applies all changes stored in backend [ such Virtual attributes ]  
				# & create the parent DN if not exist:
                obj = LBEObjectInstanceHelper(objectTemplate,objectInstance)
                self._createParent(objectTemplate,obj)
                obj.compute(objectInstance)
                # then, upgrade:
                logger.debug('Object to create or update: ' + objectInstance.name)
                if objectInstance.changes['type'] == OBJECT_CHANGE_CREATE_OBJECT:
                    try:
                        print "    |-> Object '\033[35m" + objectInstance.name + "\033[0m' is \033[34mcreating\033[0m..."
                        self._createObject(objectTemplate, objectInstance)
                    # TODO: We should have a target exception rather ldap
                    except ldap.ALREADY_EXISTS:
                        logger.debug('Object "' + objectInstance.name + '" already exists')
                        print "    |-> Object '\033[35m" + objectInstance.name + "'\033[0m already exists"
                        pass
                elif objectInstance.changes['type'] == OBJECT_CHANGE_DELETE_OBJECT:
                    try:
                        print "    |-> Object '\033[35m" + objectInstance.name + "' is \033[33mdeleting\033[0m..."
                        self._deleteObject(objectTemplate, objectInstance)
                    except BaseException as e:
                        logger.debug('Object "' + objectInstance.name + '" does not exist')
                        print "    |-> Object '\033[35m" + objectInstance.name + "'\033[0m does not exist."
                        changes = {}
                        changes['status'] = OBJECT_STATE_DELETED
                        changes['changes'] = {}
                        changes['changes']['set'] = {}
                        changes['changes']['type'] = -1
                        changes['synced_at'] = django.utils.timezone.now()
                        self.backend.updateObject(objectTemplate, objectInstance, changes)
                        pass
                elif objectInstance.changes['type'] == OBJECT_CHANGE_UPDATE_OBJECT:
                    try:
                        print "    |-> Object '\033[35m" + objectInstance.name + "'\033[0m is \033[36mupdating\033[0m..."
                        self._modifyObject(objectTemplate, objectInstance)
                    except BaseException as e:
                        print e
                        print "    |-> Object '\033[35m" + objectInstance.name + "' does not exist, being \033[34mcreated\033[0m..."
                        # Create object if not exists:
                        # Firstly, compute attributes values:
                        # Then, create it:
                        try:
                            self._createObject(objectTemplate, objectInstance)
                        except Exception as e:
							print e
							pass
                        pass
			# Synced object:
			objectTemplate.synced_at = django.utils.timezone.now()
			objectTemplate.save()
        print "   End."


    def _deleteORCreate(self,objectTemplate,ot):
		if self.reconciliation_policy.reconciliation_object_missing_policy == OBJECT_ADD_BACKEND:
			print "    |-> Adding \033[95m'" + ot.name + "'\033[0m object into Backend... "
			try:
				self.backend.createObject(objectTemplate,ot,True)
				changes = {}
				changes['status'] = OBJECT_STATE_SYNCED
				changes['changes'] = {}
				changes['changes']['set'] = {}
				changes['changes']['type'] = -1
				changes['synced_at'] = django.utils.timezone.now()
				self.backend.updateObject(objectTemplate, ot, changes)
			except BaseException as e:
				print "''''''''"
				print e
				print "''''''''"
		elif self.reconciliation_policy.reconciliation_object_missing_policy == OBJECT_DELETE_TARGET:
			print "    |-> Removing \033[95m'" + ot.name + "'\033[0m object from Target... "
			try:
				self.target.delete(objectTemplate,ot)
			except BaseException as e:
				print "''''''''"
				print e
				print "''''''''"
		
    def _upgradeObject(self,objectTemplate,ot,ob):
		if not ot.attributes == ob.attributes:
			if self.reconciliation_policy.reconciliation_object_different_policy == TARGET:
				# check if values are empty []:
				# Then, skip it.
				numberEmpty = 0
				for values in set(ot.attributes) ^ set(ob.attributes):
					try:
						# either empty or empty string:
						if ob.attributes[values] == [] or ob.attributes[values] == ['']:
							numberEmpty += 1
					except BaseException:
						pass
				if not numberEmpty==0 and numberEmpty == len(set(ot.attributes) ^ set(ob.attributes)):
					return
				print "       |-> Upgrade Object '\033[35m" + ob.name + "\033[0m' into Target..."
				print "       |-> -------------------------------------------- "
				print "       ||-> Old Values: " + str(ot.attributes)
				print "       ||-> New Values: " + str(ob.attributes)
				print "       |-> -------------------------------------------- "
				# Remove & Add in order to add new attributes:
				# Remove:
				self.target.delete(objectTemplate,ob)
				# Add
				self.target.create(objectTemplate,ob)
				# Synced:
				changes = {}
				changes['status'] = OBJECT_STATE_SYNCED
				changes['changes'] = {}
				changes['changes']['set'] = {}
				changes['changes']['type'] = -1
				changes['synced_at'] = django.utils.timezone.now()
				self.backend.updateObject(objectTemplate, ob, changes)
			elif self.reconciliation_policy.reconciliation_object_different_policy == BACKEND:
				print "       |-> Upgrade Object '\033[35m" + ob.name + "\033[0m' into Backend..."
				print "       |-> -------------------------------------------- "
				print "       ||-> Old Values: " + str(ob.attributes)
				print "       ||-> New Values: " + str(ot.attributes)
				print "       |-> -------------------------------------------- "
				self._modifyObject(objectTemplate,ot)
		
    def upgrade(self):
		print "   Upgrade Server..."
		for objectTemplate in LBEObjectTemplate.objects.all():
			print "    |-> \033[91m" + objectTemplate.name + '\033[0m:'
			objTarget = self.target.searchObjects(objectTemplate)
			objBackend = self.backend.searchObjects(objectTemplate)
			# Target to Backend:
			for ot in objTarget:
				exist = False
				for ob in objBackend:
					if ot.name == ob.name:
						self._upgradeObject(objectTemplate,ot,ob)
						exist = True
						break
				if not exist:
					self._deleteORCreate(objectTemplate,ot)
			# Synced object:
			objectTemplate.synced_at = django.utils.timezone.now()
			objectTemplate.save()
		print "   End."
		
		
    """
	  Check which values' objects need to be sync and show them.
    """
    def _needModification(self):
		print 'Objects need change:'
		for objectTemplate in LBEObjectTemplate.objects.all():
			# We're looking for all objects with state = OBJECT_STATE_AWAITING_SYNC
			if not self.backend.searchObjectsToUpdate(objectTemplate):
				print "<None>"
			else:
				for objectInstance in self.backend.searchObjectsToUpdate(objectTemplate):
					type = ""
					if objectInstance.changes['type'] == OBJECT_CHANGE_CREATE_OBJECT:
						type += "\033[34mcreate"
					elif objectInstance.changes['type'] == OBJECT_CHANGE_UPDATE_OBJECT:
						type += "\033[36mupdate"
					elif objectInstance.changes['type'] == OBJECT_CHANGE_DELETE_OBJECT:
						type += "\033[33mdelete"
					type += "\033[0m"
					value =  "    " + type + ' \033[35m'  + objectInstance.name + '\033[0m : '
					valuesChanges = dict()
					for k in objectInstance.changes['set']:
						try:
							if objectInstance.attributes[k] != objectInstance.changes['set'][k]:
								valuesChanges[k] = 'new Value: ' + str(objectInstance.changes['set'][k]) + ' | old value: ' +  str(objectInstance.attributes[k])
						except KeyError:
							valuesChanges[k] = 'new Value: ' + str(objectInstance.changes['set'][k])
							pass
					print value + str(valuesChanges)
							 
    
    """
	   Show objects do not exist in LBE but LDAP.
	"""
    def _notExistObjectLBE(self):
		print 'Checking for Objects which do not exist into LBE but in LDAP Server:'
		for objectTemplate in LBEObjectTemplate.objects.all():
			print objectTemplate.name + '...'
			objTarget = self.target.searchObjects(objectTemplate)
			objBackend = self.backend.searchObjects(objectTemplate)
			number = 0
			for ot in objTarget:
				exist = False
				for ob in objBackend:
					if ot.name == ob.name:
						exist = True
						break
				if not exist:
					number += 1
					print ot.name
			if number == 0:
				print '<None>'
			print '.........................'
	
    def debug(self):
		self._needModification()
		self._notExistObjectLBE()
		
		
class Command(BaseCommand):
	def handle(self, *args, **options):
		print "Begin:"
		reconciliation = Reconciliation()
		if 'debug' in args:
			reconciliation.debug()
		else:
			reconciliation.start()
			print ""
			reconciliation.upgrade()
		print "End."
