# -*- coding: utf-8 -*-
from directory.models import LBEObjectTemplate, OBJECT_CHANGE_CREATE_OBJECT,OBJECT_CHANGE_DELETE_OBJECT, \
OBJECT_CHANGE_UPDATE_OBJECT
from services.backend import BackendHelper
from services.target import TargetHelper

class DebugTarget():
    def __init__(self):
		self.backend = BackendHelper()
		self.target = TargetHelper()
		
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
					value =  "    " + type + ' \033[35m'  + objectInstance.displayName + '\033[0m : '
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
	
    def start(self):
		self._needModification()
		self._notExistObjectLBE()
