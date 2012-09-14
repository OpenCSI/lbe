# -*- coding: utf-8 -*-
from dao.LdapDao import LDAPDAO
from directory.models import LBEObjectTemplate, LBEObjectInstance

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
		result_set = []
		# Include all objectClass in LDAP filter
		# TODO: Refactoring to get objectClasses and basedn from the template script
		filter = '(&'
		for oc in lbeObjectTemplate.objectClasses.all():
			filter += '(objectClass=' + oc.name + ')'
		filter += ')'

		# Search in object's basedn TODO: let administrator define the subTree somewhere
		for dn, entry in self.handler.search(lbeObjectTemplate.baseDN, filter, ldap.SCOPE_SUBTREE):
			# Create an empty instance
			objectInstance = LBEObjectInstance(lbeObjectTemplate, name = entry[lbeObjectTemplate.instanceNameAttribute.name][0])
			# Add attributes defined in the template. Other ones are ignored
			for attributeInstance in lbeObjectTemplate.lbeattributeinstance_set.all():
				try:
					objectInstance.add_attribute(attributeInstance.lbeAttribute.name, entry[attributeInstance.lbeAttribute.name] )
				except KeyError, e:
					logging.warning('The attribute ' + attributeInstance.lbeAttribute.name + ' does not exist in the LDAP object: '  + dn)
			# Set displayName
			objectInstance.displayName = entry[lbeObjectTemplate.instanceDisplayNameAttribute.name][0]
			result_set.append(objectInstance)
		return result_set
