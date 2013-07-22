# -*- coding: utf-8 -*-
import django

from directory.models import LBEObjectTemplate, OBJECT_CHANGE_DELETE_OBJECT, \
    OBJECT_STATE_DELETED, OBJECT_STATE_SYNCED
from services.backend import BackendHelper
from services.target import TargetHelper


class ReinitTarget():
    def __init__(self):
        self.backend = BackendHelper()
        self.target = TargetHelper()

    def _remove(self, objectTemplate, objectInstance):
        try:
            self.target.delete(objectTemplate, objectInstance)
        except BaseException:
            # do not care if Target object does not exist
            pass

    def _create(self, objectTemplate, objectInstance):
        # replace attributes by changes set if exist
        if not objectInstance.changes['set'] == {}:
            # replace the _id value if needed:
            rdnAttributeName = objectTemplate.instanceNameAttribute.name
            if not objectInstance.attributes[rdnAttributeName][0] == objectInstance.changes['set'][rdnAttributeName][0]:
                self.backend.update_id(objectTemplate, objectInstance,
                                       objectInstance.changes['set'][rdnAttributeName][0])
            # Replace changes['set'] to attributes
            objectInstance.attributes = objectInstance.changes['set']
        self.target.create(objectTemplate, objectInstance)
        changes = {}
        changes['status'] = OBJECT_STATE_SYNCED
        changes['changes'] = {}
        changes['changes']['set'] = {}
        changes['changes']['type'] = -1
        changes['synced_at'] = django.utils.timezone.now()
        self.backend.updateObject(objectTemplate, objectInstance, changes)


    def start(self):
        for objectTemplate in LBEObjectTemplate.objects.all():
            print "    |-> Remove & recreate all objects from \033[91m'" + objectTemplate.name + "'\033[0m :"
            for objectInstance in self.backend.searchObjects(objectTemplate):
                # do not care about deleted (or in progress deleted) object
                if not objectInstance.status == OBJECT_CHANGE_DELETE_OBJECT and \
                        not objectInstance.status == OBJECT_STATE_DELETED:
                    print "      |->  \033[95m'" + objectInstance.displayName + "\033[0m' ..."
                    self._remove(objectTemplate, objectInstance)
                    self._create(objectTemplate, objectInstance)
