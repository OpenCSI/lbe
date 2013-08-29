# -*- coding: utf-8 -*-
import django

from directory.models import LBEObjectTemplate, OBJECT_ADD_BACKEND, OBJECT_DELETE_TARGET, \
    TARGET, BACKEND, OBJECT_STATE_SYNCED
from services.backend import BackendHelper
from services.target import TargetHelper
from services.object import LBEObjectInstanceHelper


class UpgradeBT():
    def __init__(self):
        self.backend = BackendHelper()
        self.target = TargetHelper()
        self.start_date = django.utils.timezone.now()

    def _deleteORCreate(self, objectTemplate, ot):
        if objectTemplate.reconciliation_object_missing_policy == OBJECT_ADD_BACKEND:
            print "    |-> Adding \033[95m'" + ot.displayName + "'\033[0m object into Backend... "
            try:
                self.backend.createObject(objectTemplate, ot, True)
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
        elif objectTemplate.reconciliation_object_missing_policy == OBJECT_DELETE_TARGET:
            print "    |-> Removing \033[95m'" + ot.displayName + "'\033[0m object from Target... "
            try:
                self.target.delete(objectTemplate, ot)
            except BaseException as e:
                print "''''''''"
                print e
                print "''''''''"

    def _upgradeObject(self, objectTemplate, objHelper, ot, ob):
        # check and replace ignore attributes:
        ignoreAttributes = objHelper.callScriptClassMethod("ignore_attributes")
        for key, values in ot.attributes.items():
            if key in ignoreAttributes:
                ob.attributes[key] = ot.attributes[key]

        if not ot.attributes == ob.attributes:
            if objectTemplate.reconciliation_object_different_policy == TARGET:
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
                    if not numberEmpty == 0 and numberEmpty == len(set(ot.attributes) ^ set(ob.attributes)):
                        return
                print " |-> Upgrade Object '\033[35m" + ob.displayName + "\033[0m' into Target..."
                print " |-> -------------------------------------------- "
                print " ||-> Old Values: " + str(ot.attributes)
                print " ||-> New Values: " + str(ob.attributes)
                print " |-> -------------------------------------------- "
                # Remove & Add in order to add new attributes:
                try:
                    # Remove:
                    self.target.delete(objectTemplate, ob)
                    # Add
                    self.target.create(objectTemplate, ob)
                    # Synced:
                    changes = {}
                    changes['status'] = OBJECT_STATE_SYNCED
                    changes['changes'] = {}
                    changes['changes']['set'] = {}
                    changes['changes']['type'] = -1
                    changes['synced_at'] = django.utils.timezone.now()
                    self.backend.updateObject(objectTemplate, ob, changes)
                except BaseException as e:
                    print e
            elif objectTemplate.reconciliation_object_different_policy == BACKEND:
                print " |-> Upgrade Object '\033[35m" + ob.displayName + "\033[0m' into Backend..."
                print " |-> -------------------------------------------- "
                print " ||-> Old Values: " + str(ob.attributes)
                print " ||-> New Values: " + str(ot.attributes)
                print " |-> -------------------------------------------- "
                try:
                    self.backend.updateObject(objectTemplate, ob, ot)
                except BaseException as e:
                    print e

    def start(self):
        print " Upgrade Server..."
        for objectTemplate in LBEObjectTemplate.objects.all():
            print " |-> \033[91m" + objectTemplate.name + '\033[0m:'
            objHelper = LBEObjectInstanceHelper(objectTemplate)
            try:
                scope = objHelper.callScriptClassMethod("search_scope")
            except BaseException:
                scope = 0
            objTarget = self.target.searchObjects(objectTemplate, scope)
            objBackend = self.backend.searchObjects(objectTemplate)
            # Target to Backend:
            for ot in objTarget:
                exist = False
                for ob in objBackend:
                    if ot.name == ob.name:
                        self._upgradeObject(objectTemplate, objHelper, ot, ob)
                        exist = True
                        break
                if not exist:
                    self._deleteORCreate(objectTemplate, ot)
            # Synced object:
            objectTemplate.synced_at = django.utils.timezone.now()
            objectTemplate.save()
        print " End."

