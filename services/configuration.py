from directory.models import *
from dao.LdapDao import LDAPService

import ldap

class ConnectionError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class InvalidCredentials(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


class BackendSchemaLDAP:
	def __init__(self):
		try:
			self.handler = LDAPService()
			self.schema = self.handler.search('cn=schema', '(objectClass=*)', ldap.SCOPE_BASE, ['+'])
		except ldap.INVALID_CREDENTIALS:
			raise InvalidCredentials('LDAP invalid credentials')
		except ldap.SERVER_DOWN:
			raise ConnectionError("LDAP server is down")
	
	def getAttributes(self):
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


class BackendSchema(BackendSchemaLDAP):
	pass
	