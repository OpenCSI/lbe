from django.conf import settings
import ldap

class LDAPService:
	def __init__(self):
		self.name = 'LBEService'
		self.handler = ldap.open(settings.LDAP_SERVER['HOST'], settings.LDAP_SERVER['PORT'])
		self.handler.simple_bind_s(settings.LDAP_SERVER['BIND_DN'], settings.LDAP_SERVER['BIND_PWD'])	

	def search(self, basedn = settings.LDAP_SERVER['BASE_DN'], filters = ('(objectClass=*)'), scope = ldap.SCOPE_SUBTREE, attributes = None):
		return self.handler.search_s(basedn, scope, filters, attributes)
		
