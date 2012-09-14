# -*- coding: utf-8 -*-
from dao.LdapDao import LDAPDAO
from directory.models import LBEObjectTemplate, LBEObjectInstance
from services.object import LBEObjectInstanceHelper

import ldap, logging

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
	
	def searchObjects(self, lbeObjectTemplate, start = 0, page = 0):
		objectHelper = LBEObjectInstanceHelper(lbeObjectTemplate)
		result_set = []
		# Include all objectClass in LDAP filter
		filter = '(&'
		for oc in lbeObjectTemplate.objectClasses.all():
			filter += '(objectClass=' + oc.name + ')'
		filter += ')'
		# Search in object's basedn TODO: add a scope property to LBEObject
		for dn, entry in self.handler.search(lbeObjectTemplate.baseDN, filter, ldap.SCOPE_SUBTREE):
			objectInstance = LBEObjectInstance(lbeObjectTemplate, name = entry[lbeObjectTemplate.uniqueAttribute.name][0])
			# TODO: Refactoring to get objectClasses and basedn from the template script
			# Add objectClasses
			objectClasses = []
			for oc in lbeObjectTemplate.objectClasses.all():
				objectClasses.append(oc.name)
			objectInstance.add_attribute('objectClass', objectClasses)
			# Fetch only attributes defined in the Template, other all are ignored
			for attributeInstance in lbeObjectTemplate.lbeattributeinstance_set.all():
				try:
					objectInstance.add_attribute(attributeInstance.lbeAttribute.name, entry[attributeInstance.lbeAttribute.name] )
				except KeyError, e:
					logging.warning('The attribute ' + attributeInstance.lbeAttribute.name + ' does not exist in the LDAP object: '  + dn)
			objectInstance.displayName = entry[objectHelper.callScriptMethod('display_name_attribute')][0]
			result_set.append(objectInstance)
		return result_set
