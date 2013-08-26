# -*- coding: utf-8 -*-
import ldap
import calendar
import logging
import datetime
from ldap import modlist

from dao.LdapDao import LDAPDAO
from directory.models import LBEObjectInstance, OBJECT_STATE_IMPORTED, LBEGroup
from services.object import LBEObjectInstanceHelper
from services.group import GroupInstanceHelper

logger = logging.getLogger(__name__)

# TODO: Think to use same exceptions than backend?
class TargetConnectionError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TargetInvalidCredentials(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TargetObjectInstance():
    def __init__(self):
        self.dn = ''


def lbeObjectInstanceToAddModList(lbeObjectInstance, objectClasses):
    # Append objectClasses
    try:
        if not lbeObjectInstance.changes['set']:
            attributes = lbeObjectInstance.attributes
        else:
            attributes = lbeObjectInstance.changes['set']
    except KeyError:
        attributes = lbeObjectInstance.attributes
        # For each mono valued, drop the list
    encodedAttributes = {}
    for key, values in attributes.items():
        if len(values) == 1:
            encodedAttributes[key.encode('utf-8')] = values[0].encode('utf-8')
        else:
            encodedAttributes[key.encode('utf-8')] = []
            for value in values:
                encodedAttributes[key.encode('utf-8')].append(value.encode('utf-8'))
        # objectClasses are not unicode objects
    encodedAttributes['objectClass'] = objectClasses
    return ldap.modlist.addModlist(encodedAttributes)


def lbeObjectInstanceToModifyModList(lbeObjectInstance):
    return ldap.modlist.modifyModlist(lbeObjectInstance.changesSet, lbeObjectInstance.changesSet, [], 1)


class TargetLDAPImplementation():
    def __init__(self):
        try:
            self.handler = LDAPDAO()
            self.schema_loaded = False
        except ldap.INVALID_CREDENTIALS:
            raise TargetInvalidCredentials('LDAP invalid credentials')
        except ldap.SERVER_DOWN:
            raise TargetConnectionError("LDAP server is down")

    def __load_schema(self):
        if self.schema_loaded == False:
            self.schema = self.handler.search('cn=schema', '(objectClass=*)', ldap.SCOPE_BASE, ['+'])
            self.schema_loaded = True

    def getAttributes(self):
        self.__load_schema()
        # Ugly way to parse a schema entry...
        result_set = []
        for dn, entry in self.schema:
            for attribute in entry['attributeTypes']:
                # Skip aliases to prevent schema violations
                aBuffer = attribute.rsplit(' ')
                if aBuffer[3] != '(':
                    result_set.append(aBuffer[3].replace('\'', ''))
                else:
                    result_set.append(aBuffer[4].replace('\'', ''))
        return result_set

    def getObjectClasses(self):
        self.__load_schema()
        result_set = []
        for dn, entry in self.schema:
            for attribute in entry['objectClasses']:
                # Skip aliases to prevent schema violations
                aBuffer = attribute.rsplit(' ')
                if aBuffer[3] != '(':
                    result_set.append(aBuffer[3].replace('\'', ''))
                else:
                    result_set.append(aBuffer[4].replace('\'', ''))
        return result_set

    @classmethod
    def _ldap_date(cls, date):
        return date.strftime('%Y%m%d%H%M%SZ')

    def searchNewObjects(self, lbeObjectTemplate, start=0, page=0):
        objectHelper = LBEObjectInstanceHelper(lbeObjectTemplate)
        filter = '(&(createTimeStamp>=' + self._ldap_date(lbeObjectTemplate.imported_at) + ')'
        for oc in objectHelper.callScriptClassMethod('object_classes'):
            filter += '(objectClass=' + oc + ')'
        filter += ')'

        return self.searchObjects(lbeObjectTemplate, filter, start, page)

    # TODO: add a parameter to get all ldap attributes, used for reconciliation task
    def searchObjects(self, lbeObjectTemplate, filter=None, start=0, page=0):
        result_set = []
        # Call methods from object's script to get basedn and objectClass
        objectHelper = LBEObjectInstanceHelper(lbeObjectTemplate)
        if filter is None:
            filter = '(&'
            for oc in objectHelper.callScriptClassMethod('object_classes'):
                filter += '(objectClass=' + oc + ')'
            filter += ')'#(modifyTimestamp>'+str(calendar.timegm(lbeObjectTemplate.synced_at.utctimetuple()))+'Z))'
        
        # Search in object's basedn TODO: let administrator define the scope in the object script
        for dn, entry in self.handler.search(objectHelper.callScriptClassMethod('base_dn'), filter, ldap.SCOPE_SUBTREE,
                                             ['*', '+']):
            # Create an empty instance
            objectInstance = LBEObjectInstance(lbeObjectTemplate,
                                               name=entry[lbeObjectTemplate.instanceNameAttribute.name][0])
            # Add attributes defined in the template. Other ones are ignored
            try:  # Object
                for attributeInstance in lbeObjectTemplate.lbeattributeinstance_set.all():
                    try:
                        objectInstance.attributes[attributeInstance.lbeAttribute.name] = entry[
                            attributeInstance.lbeAttribute.name]
                    except KeyError, e:
                        logger.warning(
                            'The attribute ' + attributeInstance.lbeAttribute.name + ' does not exist in LDAP object: ' + dn)
                    # Set displayName and few others attributes
                objectInstance.displayName = entry[lbeObjectTemplate.instanceDisplayNameAttribute.name][0]
                objectInstance.status = OBJECT_STATE_IMPORTED
                objectInstance.created_at = datetime.datetime.strptime(entry['createTimestamp'][0], '%Y%m%d%H%M%SZ')
                try:
                    objectInstance.updated_at = datetime.datetime.strptime(entry['modifyTimestamp'][0], '%Y%m%d%H%M%SZ')
                except KeyError:
                    objectInstance.updated_at = datetime.datetime.strptime(entry['createTimestamp'][0], '%Y%m%d%H%M%SZ')
                result_set.append(objectInstance)
            except AttributeError:  # Group:
                groupInstance = GroupInstanceHelper(lbeObjectTemplate)
                objectInstance.displayName = entry['cn'][0]
                objectInstance.attributes[u'cn'] = entry['cn']
                if groupInstance.attributeName in entry:
                    objectInstance.attributes[groupInstance.attributeName] = entry[groupInstance.attributeName]
                else:
                    objectInstance.attributes[groupInstance.attributeName] = []
                objectInstance.status = OBJECT_STATE_IMPORTED
                objectInstance.created_at = datetime.datetime.strptime(entry['createTimestamp'][0], '%Y%m%d%H%M%SZ')
                try:
                    objectInstance.updated_at = datetime.datetime.strptime(entry['modifyTimestamp'][0], '%Y%m%d%H%M%SZ')
                except KeyError:
                    objectInstance.updated_at = datetime.datetime.strptime(entry['createTimestamp'][0], '%Y%m%d%H%M%SZ')
                result_set.append(objectInstance)
        return result_set

    def create(self, lbeObjectTemplate, lbeObjectInstance):
        objectHelper = LBEObjectInstanceHelper(lbeObjectTemplate)

        rdnAttributeName = lbeObjectTemplate.instanceNameAttribute.name
        dn = rdnAttributeName + '=' + lbeObjectInstance.attributes[rdnAttributeName][
            0] + ',' + objectHelper.callScriptClassMethod('base_dn')

        return self.handler.add(dn, lbeObjectInstanceToAddModList(lbeObjectInstance,
                                                                  objectHelper.callScriptClassMethod('object_classes')))

    def createParent(self, base_dn, modlist):
        return self.handler.add(base_dn, modlist)

    def delete(self, lbeObjectTemplate, lbeObjectInstance):
        objectHelper = LBEObjectInstanceHelper(lbeObjectTemplate)

        rdnAttributeName = lbeObjectTemplate.instanceNameAttribute.name
        dn = rdnAttributeName + '=' + lbeObjectInstance.attributes[rdnAttributeName][
            0] + ',' + objectHelper.callScriptClassMethod('base_dn')

        return self.handler.delete(dn)

    def changeRDN(self, lbeObjectTemplate, lbeObjectInstance, oldRDNAttribute, oldRDNValue):
        objectHelper = LBEObjectInstanceHelper(lbeObjectTemplate)
        # Old RDN:
        dn = oldRDNAttribute + '=' + oldRDNValue + ',' + objectHelper.callScriptClassMethod('base_dn')
        # New RDN:
        rdnAttributeName = lbeObjectTemplate.instanceNameAttribute.name
        newDN = rdnAttributeName + '=' + lbeObjectInstance.attributes[rdnAttributeName][0]
        self.handler.changeRDN(dn, newDN.encode("utf-8"))

    def update(self, lbeObjectTemplate, lbeObjectInstance):
        objectHelper = LBEObjectInstanceHelper(lbeObjectTemplate)
        if not isinstance(lbeObjectTemplate, LBEGroup):
            ignore_attributes = objectHelper.callScriptClassMethod("ignore_attributes")
        else:
            ignore_attributes = []
        # RDN Attribute:
        rdnAttributeName = lbeObjectTemplate.instanceNameAttribute.name
        dn = rdnAttributeName + '=' + lbeObjectInstance.attributes[rdnAttributeName][
            0] + ',' + objectHelper.callScriptClassMethod('base_dn')
        LDAPValues = self.searchObjects(lbeObjectTemplate,
                                        rdnAttributeName + '=' + lbeObjectInstance.attributes[rdnAttributeName][0])[
            0].attributes
        # Need to check if the RDN changed:
        if not lbeObjectInstance.attributes[rdnAttributeName][0] == lbeObjectInstance.changes['set'][rdnAttributeName][
            0] and not lbeObjectInstance.changes['set'][rdnAttributeName][0] == '':
            newDN = rdnAttributeName + '=' + lbeObjectInstance.changes['set'][rdnAttributeName][0]
            self.handler.changeRDN(dn, newDN.encode("utf-8"))
            dn = newDN + ',' + objectHelper.callScriptClassMethod('base_dn')
            # Update:
        for key, value in lbeObjectInstance.changes['set'].items():
            if key in ignore_attributes:
                continue
            noKey = not LDAPValues.has_key(key)# key exists into the object target?
            if noKey or not value == LDAPValues[key] and not value[0] == '':
                # 1 value: Replace
                if len(value) == 1:
                    if noKey:
                        # ADD:
                        modList = [(ldap.MOD_ADD, key.encode("utf-8"), value[0].encode("utf-8") )]
                    else:
                        # REPLACE:
                        modList = [(ldap.MOD_REPLACE, key.encode("utf-8"), value[0].encode("utf-8") )]
                    self.handler.update(dn, modList)
                else: # MultiValue:
                    if noKey:
                        # ADD:
                        for val in value:
                            modList = [(ldap.MOD_ADD, key.encode("utf-8"), val.encode("utf-8") )]
                            self.handler.update(dn, modList)
                    else:
                        # REMOVE:
                        for val in LDAPValues[key]:
                            modList = [(ldap.MOD_DELETE, key.encode("utf-8"), val.encode("utf-8") )]
                            self.handler.update(dn, modList)
                        # ADD:
                        for val in value:
                            modList = [(ldap.MOD_ADD, key.encode("utf-8"), val.encode("utf-8") )]
                            self.handler.update(dn, modList)

    def upgrade(self, lbeObjectTemplate, lbeObjectInstance):
        objectHelper = LBEObjectInstanceHelper(lbeObjectTemplate)
        if not isinstance(lbeObjectTemplate, LBEGroup):
            ignore_attributes = objectHelper.callScriptClassMethod("ignore_attributes")
        else:
            ignore_attributes = []
        # RDN Attribute:
        rdnAttributeName = lbeObjectTemplate.instanceNameAttribute.name
        dn = rdnAttributeName + '=' + lbeObjectInstance.attributes[rdnAttributeName][
            0] + ',' + objectHelper.callScriptClassMethod('base_dn')
        LDAPValues = self.searchObjects(lbeObjectTemplate,
                                        rdnAttributeName + '=' + lbeObjectInstance.attributes[rdnAttributeName][0])[
            0].attributes
        # Update:
        for key, value in lbeObjectInstance.attributes.items():
            if key in ignore_attributes:
                continue
            noKey = not LDAPValues.has_key(key)# key exists into the object target?
            if noKey or not value == LDAPValues[key]:
                # 1 value: Replace
                if len(value) == 1:
                    if noKey:
                        # ADD:
                        modList = [(ldap.MOD_ADD, key.encode("utf-8"), value[0].encode("utf-8") )]
                    else:
                        # REPLACE:
                        modList = [(ldap.MOD_REPLACE, key.encode("utf-8"), value[0].encode("utf-8") )]
                    self.handler.update(dn, modList)
                else: # MultiValue:
                    if noKey:
                        # ADD:
                        for val in value:
                            modList = [(ldap.MOD_ADD, key.encode("utf-8"), val.encode("utf-8") )]
                            self.handler.update(dn, modList)
                    else:
                        # REMOVE:
                        for val in LDAPValues[key]:
                            modList = [(ldap.MOD_DELETE, key.encode("utf-8"), val.encode("utf-8") )]
                            self.handler.update(dn, modList)
                        # ADD:
                        for val in value:
                            modList = [(ldap.MOD_ADD, key.encode("utf-8"), val.encode("utf-8") )]
                            self.handler.update(dn, modList)
