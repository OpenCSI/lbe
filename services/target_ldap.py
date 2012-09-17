# -*- coding: utf-8 -*-
import ldap, logging, datetime, base64
from ldap import modlist

from dao.LdapDao import LDAPDAO
from directory.models import LBEObjectTemplate, LBEObjectInstance, OBJECT_STATE_IMPORTED
from services.object import LBEObjectInstanceHelper

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
    attributes = lbeObjectInstance.changes['set']
    # For each mono valued, drop the list
    encodedAttributes = {}
    for key, value in attributes.items():
        if len(value) == 1:
            encodedAttributes[key.encode('utf-8')] = value[0].encode('utf-8')
        else:
            # TODO: probably need to decode each value
            encodedAttributes[key.encode('utf-8')] = value
    # objectClasses are not unicode objects
    encodedAttributes['objectClass'] = objectClasses
    print encodedAttributes
    return ldap.modlist.addModlist(encodedAttributes)

def lbeObjectInstanceToModifyModList(lbeObjectInstance):
    print lbeObjectInstance.name
    print lbeObjectInstance.changes['set']
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
        for dn,entry in self.schema:
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
        for dn,entry in self.schema:
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

    def searchNewObjects(self, lbeObjectTemplate, start = 0, page = 0):
        objectHelper = LBEObjectInstanceHelper(lbeObjectTemplate)
        filter = '(&(createTimeStamp>=' + self._ldap_date(lbeObjectTemplate.imported_at) + ')'
        for oc in objectHelper.callScriptClassMethod('object_classes'):
            filter += '(objectClass=' + oc + ')'
        filter += ')'

        return self.searchObjects(lbeObjectTemplate, filter, start, page)

    # TODO: add a parameter to get all ldap attributes, used for reconciliation task
    def searchObjects(self, lbeObjectTemplate, filter = None, start = 0, page = 0):
        result_set = []
        # Call methods from object's script to get basedn and objectClass
        objectHelper = LBEObjectInstanceHelper(lbeObjectTemplate)
        if filter is None:
            filter = '(&'
            for oc in objectHelper.callScriptClassMethod('object_classes'):
                filter += '(objectClass=' + oc + ')'
            filter += ')'

        # Search in object's basedn TODO: let administrator define the scope in the object script
        for dn, entry in self.handler.search(objectHelper.callScriptClassMethod('base_dn'), filter, ldap.SCOPE_SUBTREE, ['*', '+']):
            # Create an empty instance
            objectInstance = LBEObjectInstance(lbeObjectTemplate, name = entry[lbeObjectTemplate.instanceNameAttribute.name][0])
            # Add attributes defined in the template. Other ones are ignored
            for attributeInstance in lbeObjectTemplate.lbeattributeinstance_set.all():
                try:
                    objectInstance.attributes[attributeInstance.lbeAttribute.name] = entry[attributeInstance.lbeAttribute.name]
                except KeyError, e:
                    logger.warning('The attribute ' + attributeInstance.lbeAttribute.name + ' does not exist in LDAP object: '  + dn)
            # Set displayName
            objectInstance.displayName = entry[lbeObjectTemplate.instanceDisplayNameAttribute.name][0]
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
        dn =  rdnAttributeName + '=' + lbeObjectInstance.attributes[rdnAttributeName][0]  + ',' + objectHelper.callScriptClassMethod('base_dn')

        self.handler.add(dn, lbeObjectInstanceToAddModList(lbeObjectInstance, objectHelper.callScriptClassMethod('object_classes')))
