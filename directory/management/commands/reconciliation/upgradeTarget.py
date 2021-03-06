# -*- coding: utf-8 -*-
import ldap
from ldap import modlist

import django
from django.conf import settings # LDAP settings

from directory.models import LBEObjectTemplate, OBJECT_CHANGE_CREATE_OBJECT, OBJECT_CHANGE_DELETE_OBJECT, \
    OBJECT_CHANGE_UPDATE_OBJECT, OBJECT_STATE_SYNCED, OBJECT_STATE_DELETED, LBEGroup
from services.backend import BackendHelper
from services.target import TargetHelper
from services.object import LBEObjectInstanceHelper
from services.group import GroupInstanceHelper



class UpgradeTarget():
    def __init__(self):
        self.backend = BackendHelper()
        self.target = TargetHelper()
        self.start_date = django.utils.timezone.now()

    def _changeClass(self, objectTemplate):
        objHelper = LBEObjectInstanceHelper(objectTemplate)
        try:
            scope = objHelper.callScriptClassMethod("scope_search")
        except BaseException:
            scope = 0

        ob = self.backend.searchObjects(objectTemplate)
        for objectInstance in ob:
            try:
                oldClasses = self.target.getInstanceObjectClasses(objectTemplate, objectInstance, scope)
            except ldap.NO_SUCH_OBJECT:
                continue
            newClasses = objHelper.callScriptClassMethod("object_classes")

            if not sorted(oldClasses) == sorted(newClasses):
                print "    |-> The object classes have changed for '\033[35m" + objectInstance.displayName + "\033[0m'"
                try:
                    self.target.changeClass(objectTemplate, objectInstance, oldClasses, newClasses)
                except ldap.OBJECT_CLASS_VIOLATION as e:
                    print "    *\033[91mError to modify the object class " + str(newClasses) + ", skip it.\033[0m"
                    print "    *\033[91m" + e[0]['info'] + "\033[0m"



    def _changeRDN(self, objectTemplate):
        if objectTemplate.needReconciliationRDN:
            print "    |-> Upgrade the RDN Target server for \033[35m" + objectTemplate.name + "\033[0m..."
            # Change the RDN Attribute to the Target Server
            ob = self.backend.searchObjects(objectTemplate)
            for o in ob:
                try:
                    self.target.changeRDN(objectTemplate, o, objectTemplate.instanceNameBeforeAttribute.name,
                                          o.attributes[objectTemplate.instanceNameBeforeAttribute.name][0])
                except BaseException:
                    # if object does not exists into the Target Server
                    pass
                self.backend.updateStatus(objectTemplate, o.name)
            # Update values for changing RDN attribute
            objectTemplate.instanceNameBeforeAttribute = None
            objectTemplate.needReconciliationRDN = False
            objectTemplate.save()
            print "    |-> Done."

    def _createParent(self, lbeObjectTemplate, objService):
        base_dn = objService.callScriptClassMethod("base_dn")
        objectToCreate = base_dn.replace(settings.LDAP_SERVER['BASE_DN'], '')[:-1].split(',')
        objectToCreate.reverse()
        for i in range(0, len(objectToCreate)):
            dn = objectToCreate[i] + ','
            for j in range(0, i):
                dn = dn + objectToCreate[j] + ','
            dn = dn + settings.LDAP_SERVER['BASE_DN']
            attrs = {}
            attrs['objectclass'] = ['top', 'organizationalUnit']
            # do not care if the ou already exists
            try:
                self.target.createParent(dn, modlist.addModlist(attrs))
            except BaseException:
                pass

    def _createObject(self, objectTemplate, objectInstance):
        self.target.create(objectTemplate, objectInstance)
        # Ok, the object is added, empty changes set, and update object status
        changes = {}
        changes['status'] = OBJECT_STATE_SYNCED
        changes['changes'] = {}
        changes['changes']['set'] = {}
        changes['changes']['type'] = -1
        changes['synced_at'] = django.utils.timezone.now()
        self.backend.updateObject(objectTemplate, objectInstance, changes)

    def _modifyObject(self, objectTemplate, objectInstance, SCOPE):
        rdnAttributeName = objectTemplate.instanceNameAttribute.name
        self.target.update(objectTemplate, objectInstance, SCOPE)
        if not objectInstance.attributes[rdnAttributeName][0] == objectInstance.changes['set'][rdnAttributeName][0]:
            self.backend.update_id(objectTemplate, objectInstance, objectInstance.changes['set'][rdnAttributeName][0])
            # Update Backend value:
        changes = {}
        changes['status'] = OBJECT_STATE_SYNCED
        changes['changes'] = {}
        changes['changes']['set'] = {}
        changes['changes']['type'] = -1
        changes['synced_at'] = django.utils.timezone.now()
        self.backend.updateObject(objectTemplate, objectInstance, changes)

    def _deleteObject(self, objectTemplate, objectInstance):
        self.target.delete(objectTemplate, objectInstance)
        # Update Backend value:
        changes = {}
        changes['status'] = OBJECT_STATE_DELETED
        changes['changes'] = {}
        changes['changes']['set'] = {}
        changes['changes']['type'] = -1
        changes['synced_at'] = django.utils.timezone.now()
        self.backend.updateObject(objectTemplate, objectInstance, changes)

    def _getRDN(self, objectTemplate, listID):
        objectHelper = LBEObjectInstanceHelper(objectTemplate)
        baseDN = objectHelper.callScriptClassMethod('base_dn')
        listObjectID = []
        for ID in listID:
            dn = objectTemplate.instanceNameAttribute.name + '=' + ID + ',' + baseDN
            listObjectID.append(dn)
        return listObjectID

    def _getID(self, listRDN):
        listID = []
        for rdn in listRDN:
            listID.append(rdn.split('=')[1].split(',')[0])
        return listID

    def start(self):
        print "   Upgrade the Target server with the Backend server..."
        for objectTemplate in LBEObjectTemplate.objects.all():
            # need to check if we need to change (before making reconciliation) the RDN attribute
            self._changeRDN(objectTemplate)
            # And the objects class
            self._changeClass(objectTemplate)
            # We're looking for all objects with state = OBJECT_STATE_AWAITING_SYNC
            for objectInstance in self.backend.searchObjectsToUpdate(objectTemplate):
            # First of all, applies all changes stored in backend [ such Virtual attributes ]
            # & create the parent DN if not exist:
                obj = LBEObjectInstanceHelper(objectTemplate, objectInstance)
                try:
                    scope = obj.callScriptClassMethod("search_scope")
                except BaseException:
                    scope = 0
                self._createParent(objectTemplate, obj)
                #obj.compute(objectInstance)
                # then, upgrade:
                if objectInstance.changes['type'] == OBJECT_CHANGE_CREATE_OBJECT:
                    try:
                        print "    |-> Object '\033[35m" + objectInstance.displayName + "\033[0m' is \033[34mcreating\033[0m..."
                        self._createObject(objectTemplate, objectInstance)
                    # TODO: We should have a target exception rather ldap
                    except ldap.ALREADY_EXISTS:
                        print "    |-> Object '\033[35m" + objectInstance.displayName + "'\033[0m already exists"
                        changes = {}
                        changes['status'] = OBJECT_STATE_SYNCED
                        changes['changes'] = {}
                        changes['changes']['set'] = {}
                        changes['changes']['type'] = -1
                        changes['synced_at'] = django.utils.timezone.now()
                        self.backend.updateObject(objectTemplate, objectInstance, changes)
                        pass
                elif objectInstance.changes['type'] == OBJECT_CHANGE_DELETE_OBJECT:
                    try:
                        print "    |-> Object '\033[35m" + objectInstance.displayName + "' is \033[33mdeleting\033[0m..."
                        self._deleteObject(objectTemplate, objectInstance)
                    except BaseException as e:
                        print "    |-> Object '\033[35m" + objectInstance.displayName + "'\033[0m does not exist."
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
                        print "    |-> Object '\033[35m" + objectInstance.displayName + "'\033[0m is \033[36mupdating\033[0m..."
                        # Group
                        for group in LBEGroup.objects.all():
                            if group.objectTemplate.id == objectTemplate.id:
                                GroupInstanceHelper(group).updateMember(obj.getObject(obj.instance.name))
                        self._modifyObject(objectTemplate, objectInstance, scope)
                    except BaseException as e:
                        print e
                        print "    |-> Object '\033[35m" + objectInstance.displayName + "' does not exist, being \033[34mcreated\033[0m..."
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
        print ''
        print "   Upgrade Groups Objects:"
        for groupTemplate in LBEGroup.objects.all():
            for groupInstance in self.backend.searchObjectsToUpdate(groupTemplate):
                grp = GroupInstanceHelper(groupTemplate, groupInstance)
                try:
                    scope = grp.callScriptClassMethod("search_scope")
                except BaseException:
                    scope = 0
                self._createParent(groupTemplate, grp)
                if groupInstance.changes['type'] == OBJECT_CHANGE_CREATE_OBJECT:
                    print "    |-> Group '\033[35m" + groupInstance.displayName + "\033[0m' is \033[34mcreating\033[0m..."
                    try:
                        groupInstance.changes['set'][grp.attributeName] = self._getRDN(groupTemplate.objectTemplate, groupInstance.changes['set'][grp.attributeName])
                        self._createObject(groupTemplate, groupInstance)
                        ###############################################
                        if not groupInstance.changes['set'] == {}:
                            groupInstance.changes['set'][grp.attributeName] = self._getID(groupInstance.changes['set'][grp.attributeName])
                            groupInstance.attributes['cn'] = groupInstance.changes['set']['cn']
                            self.backend.updateObject(groupTemplate, groupInstance, {'changes': {'set': {'cn': [groupInstance.displayName]}, 'type': -1}})
                        ###############################################
                    except ldap.ALREADY_EXISTS:
                        print "    |-> Group '\033[35m" + groupInstance.displayName + "'\033[0m already exists"
                elif groupInstance.changes['type'] == OBJECT_CHANGE_UPDATE_OBJECT:
                    try:
                        print "    |-> Group '\033[35m" + groupInstance.displayName + "'\033[0m is \033[36mupdating\033[0m..."
                        groupInstance.changes['set'][grp.attributeName] = self._getRDN(groupTemplate.objectTemplate, groupInstance.changes['set'][grp.attributeName])
                        self._modifyObject(groupTemplate, groupInstance, scope)
                        ###############################################
                        groupInstance.changes['set'][grp.attributeName] = self._getID(groupInstance.changes['set'][grp.attributeName])
                        groupInstance.attributes['cn'] = groupInstance.changes['set']['cn']
                        self.backend.updateObject(groupTemplate, groupInstance, {'changes': {'set': {'cn': [groupInstance.displayName]}, 'type': -1}})
                        ###############################################
                    except BaseException as e:
                        print e
                        print "    |-> Group '\033[35m" + groupInstance.displayName + "' does not exist, being \033[34mcreated\033[0m..."
                        groupInstance.changes['set'][grp.attributeName] = self._getRDN(groupTemplate.objectTemplate, groupInstance.changes['set'][grp.attributeName])
                        self._createObject(groupTemplate, groupInstance)
                        ###############################################
                        groupInstance.changes['set'][grp.attributeName] = self._getID(groupInstance.changes['set'][grp.attributeName])
                        groupInstance.attributes['cn'] = groupInstance.changes['set']['cn']
                        self.backend.updateObject(groupTemplate, groupInstance, {'changes': {'set': {'cn': [groupInstance.displayName]}, 'type': -1}})
                        ###############################################
                elif groupInstance.changes['type'] == OBJECT_CHANGE_DELETE_OBJECT:
                    print "    |-> Group '\033[35m" + groupInstance.displayName + "' is \033[33mdeleting\033[0m..."
                    self._deleteObject(groupTemplate, groupInstance)
        print "   End."
