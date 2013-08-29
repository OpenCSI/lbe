# -*- coding: utf-8 -*-
from directory.models import LBEObjectTemplate, OBJECT_CHANGE_CREATE_OBJECT, OBJECT_CHANGE_DELETE_OBJECT, \
    OBJECT_CHANGE_UPDATE_OBJECT, LBEGroup
from services.backend import BackendHelper
from services.target import TargetHelper
from services.group import GroupInstanceHelper
from services.object import LBEObjectInstanceHelper


class DebugTarget():
    def __init__(self):
        self.backend = BackendHelper()
        self.target = TargetHelper()

    """
	  Check which values' objects need to be sync and show them.
    """

    def _needModification(self):
        print '  Objects need change:'
        number = 0
        for objectTemplate in LBEObjectTemplate.objects.all():
            # We're looking for all objects with state = OBJECT_STATE_AWAITING_SYNC
            for objectInstance in self.backend.searchObjectsToUpdate(objectTemplate):
                type = ""
                if objectInstance.changes['type'] == OBJECT_CHANGE_CREATE_OBJECT:
                    type += "\033[34mcreate"
                elif objectInstance.changes['type'] == OBJECT_CHANGE_UPDATE_OBJECT:
                    type += "\033[36mupdate"
                elif objectInstance.changes['type'] == OBJECT_CHANGE_DELETE_OBJECT:
                    type += "\033[33mdelete"
                type += "\033[0m"
                value = "    " + type + ' \033[35m' + objectInstance.displayName + '\033[0m : '
                valuesChanges = dict()
                for k in objectInstance.changes['set']:
                    try:
                        if objectInstance.attributes[k] != objectInstance.changes['set'][k]:
                            valuesChanges[k] = 'new Value: ' + str(
                                objectInstance.changes['set'][k]) + ' | old value: ' + str(
                                objectInstance.attributes[k])
                    except KeyError:
                        valuesChanges[k] = 'new Value: ' + str(objectInstance.changes['set'][k])
                        pass
                print value + str(valuesChanges)
                number += 1
        if number == 0:
            print "    \033[91m<None>\033[0m"

        print ""
        print '  Groups need change:'
        number = 0
        for groupTemplate in LBEGroup.objects.all():
            for groupInstance in self.backend.searchObjectsToUpdate(groupTemplate):
                number += 1
                type = ""
                if groupInstance.changes['type'] == OBJECT_CHANGE_CREATE_OBJECT:
                    type += "\033[34mcreate"
                elif groupInstance.changes['type'] == OBJECT_CHANGE_UPDATE_OBJECT:
                    type += "\033[36mupdate"
                elif groupInstance.changes['type'] == OBJECT_CHANGE_DELETE_OBJECT:
                    type += "\033[33mdelete"
                type += "\033[0m"
                value = "    " + type + ' \033[35m' + groupInstance.displayName + '\033[0m : '
                valuesChanges = dict()
                for k in groupInstance.changes['set']:
                    try:
                        if groupInstance.attributes[k] != groupInstance.changes['set'][k]:
                            valuesChanges[k] = 'new Value: ' + str(
                                groupInstance.changes['set'][k]) + ' | old value: ' + str(
                                groupInstance.attributes[k])
                    except KeyError:
                        valuesChanges[k] = 'new Value: ' + str(groupInstance.changes['set'][k])
                        pass
                print value + str(valuesChanges)
        if number == 0:
            print "    \033[91m<None>\033[0m"

    """
	   Show objects do not exist in LBE but LDAP.
	"""

    def _notExistObjectLBE(self):
        print '  Checking for Objects which do not exist into LBE but in LDAP Server:'
        for objectTemplate in LBEObjectTemplate.objects.all():
            print "  - \033[35m" + objectTemplate.name + '\033[0m...'
            objHelper = LBEObjectInstanceHelper(objectTemplate)
            try:
                scope = objHelper.callScriptClassMethod("search_scope")
            except BaseException:
                scope = 0
            objTarget = self.target.searchObjects(objectTemplate, scope)
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
                    print "    " + ot.name
            if number == 0:
                print '    \033[91m<None>\033[0m'
        print ""
        print '  Checking for Groups which do not exist into LBE but in LDAP Server:'
        number = 0
        for groupTemplate in LBEGroup.objects.all():
            grpHelper = GroupInstanceHelper(groupTemplate)
            try:
                scope = grpHelper.callScriptClassMethod("search_scope")
            except BaseException:
                scope = 0
            grpTarget = self.target.searchObjects(groupTemplate, scope, '(cn=' + groupTemplate.displayName + ')')
            grpBackend = self.backend.searchObjectsByPattern(groupTemplate, groupTemplate.displayName)
            if not grpBackend:
                print "   - \033[36m" + groupTemplate.displayName + "\033[0m does not exists."
                number += 1
        if number == 0:
            print '    \033[91m<None>\033[0m'

    def start(self):
        self._needModification()
        print ""
        print '\033[93m.........................\033[0m'
        print '\033[93m.........................\033[0m'
        print ""
        self._notExistObjectLBE()
