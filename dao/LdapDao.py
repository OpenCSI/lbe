# -*- coding: utf-8 -*-
from django.conf import settings
import ldap, logging

logger = logging.getLogger(__name__)

class LDAPDAO:
    def __init__(self):
        self.handler = ldap.initialize(str(settings.LDAP_SERVER['PROTOCOL']) + str(settings.LDAP_SERVER['HOST']) + ':' + str(settings.LDAP_SERVER['PORT']))
        #self.handler =  ldap.open(settings.LDAP_SERVER['HOST'], settings.LDAP_SERVER['PORT'])
        self.handler.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        self.handler.simple_bind_s(settings.LDAP_SERVER['BIND_DN'], settings.LDAP_SERVER['BIND_PWD'])

    def changeRDN(self,oldRDN,newRDN):
        logger.debug('LDAP changing RDN ' + oldRDN +' to '+ newRDN)
        return self.handler.modrdn_s(oldRDN,newRDN,False)
		
    # TODO: Implement VLV if supported by the LDAP server
    def search(self, basedn, filter = ('(objectClass=*)'), scope = ldap.SCOPE_SUBTREE, attributes = None, start = 0, page = 0):
        logger.debug('LDAP search with basedn: ' + basedn + ', filter: ' + filter)
        return self.handler.search_s(basedn, scope, filter, attributes)

    def add(self, basedn, modlist):
        logger.debug('LDAP Adding ' + basedn + ' object')
        return self.handler.add_s(basedn, modlist)

    def update(self, basedn, modlist):
        logger.debug('LDAP update ' + basedn + ' object')
        return self.handler.modify_s(basedn, modlist)
        
    def delete(self,basedn):
		logger.debug('LDAP delete ' + basedn + ' object')
		return self.handler.delete_s(basedn)
