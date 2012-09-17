# -*- coding: utf-8 -*-
from django.conf import settings
import ldap, logging

logger = logging.getLogger(__name__)

class LDAPDAO:
    def __init__(self):
        self.handler = ldap.open(settings.LDAP_SERVER['HOST'], settings.LDAP_SERVER['PORT'])
        self.handler.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        self.handler.simple_bind_s(settings.LDAP_SERVER['BIND_DN'], settings.LDAP_SERVER['BIND_PWD'])

    # TODO: Implement VLV if supported by the LDAP server
    def search(self, basedn, filter = ('(objectClass=*)'), scope = ldap.SCOPE_SUBTREE, attributes = None, start = 0, page = 0):
        logger.debug('Performing LDAP search with basedn: ' + basedn + ', filter: ' + filter)
        return self.handler.search_s(basedn, scope, filter, attributes)

    def add(self, basedn, modlist):
        return self.handler.add_s(basedn, modlist)

    def update(self, basedn, modlist):
        return self.handler.modify_s(basedn, modlist)
