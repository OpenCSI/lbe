from dao.LdapDao import LDAPService
from directory.models import LBEObjectTemplate, LBEObjectInstance

import ldap

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
	
	def searchObjects(self, LBEObjectTemplate, start = 0, page = 0):
		result_set = []
		# Include all objectClass in LDAP filter
		filter = '(&'
		for oc in LBEObjectTemplate.objectClasses.all():
			filter += '(objectClass=' + oc.name + ')'
		filter += ')'
		# Search in object's basedn TODO: add a scope property to LBEObject
		for dn, entry in self.handler.search(LBEObjectTemplate.baseDN, filter, ldap.SCOPE_SUBTREE):
			objectInstance = LBEObjectInstance(dn, LBEObjectTemplate.name, entry[LBEObjectDefinition.rdnAttribute.name][0])
			# Add objectClasses
			objectClasses = []
			for oc in LBEObjectTemplate.objectClasses.all():
				objectClasses.append(oc.name)
			objectInstance.addAttribute('objectClass', objectClasses)
			# Fetch only attributes defined in the Template, other all are ignored
			for attributeInstance in LBEObjectTemplate.lbeattributeinstance_set.all():
				objectInstance.addAttribute(attributeInstance.lbeAttribute.name, entry[attributeInstance.lbeAttribute.name] )
			result_set.append(objectInstance)
		return result_set
	
class TargetDao(TargetDaoLDAP):
	pass
	
