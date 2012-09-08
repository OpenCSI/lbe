from directory.models import *
from dao.LdapDao import LDAPService

import ldap

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

class TargetDaoLDAP():
	def __init__(self):
		try:
			self.handler = LDAPService()
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
				# Skip aliases to prevend schema violations
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
				# Skip aliases to prevend schema violations
				aBuffer = attribute.rsplit(' ')
				if aBuffer[3] != '(':
					result_set.append(aBuffer[3].replace('\'', ''))
				else:
					result_set.append(aBuffer[4].replace('\'', ''))
		return result_set

class TargetDao(TargetDaoLDAP):
	pass
	