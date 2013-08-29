# -*- coding: utf-8 -*-

#
# This file is an example of script called after group creation
#
class GROUPPostConfig:
    # These methods are used only for LDAP target. Must be class methods
    # instanceNameAttribute will be used as RDN attribute
    @classmethod
    def base_dn(cls):
        return 'ou=Groups,dc=opencsi,dc=com'

    # Note this method must return a list
    @classmethod
    def object_classes(cls):
        return ['top', 'groupOfUniqueNames']

    @classmethod
    def search_scope(cls):
        return 2

    # The group's attribute name for the groupOfUniqueNames class
    @classmethod
    def attribute_name(cls):
        return 'uniqueMember'
