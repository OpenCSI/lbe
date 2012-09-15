from django.conf import settings
import ldap

class LDAPDAO:
    def __init__(self):
        self.handler = ldap.open(settings.LDAP_SERVER['HOST'], settings.LDAP_SERVER['PORT'])
        self.handler.simple_bind_s(settings.LDAP_SERVER['BIND_DN'], settings.LDAP_SERVER['BIND_PWD'])    

    def search(self, basedn, filters = ('(objectClass=*)'), scope = ldap.SCOPE_SUBTREE, attributes = None):
        return self.handler.search_s(basedn, scope, filters, attributes)
    
    # TODO: Implement VLV if supported by the LDAP server
    def search_page(self, basedn, filters = ('(objectClass=*)'), scope = ldap.SCOPE_SUBTREE, attributes = None, start = 0, page = 0):
        pass
        
