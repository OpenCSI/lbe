# -*- coding: utf-8 -*-
from directory.models import LBEObjectTemplate, LBEObjectInstance
import re

#
# This file is an example of script called after object creation
#

# TODO: Probably use a better suffix than PostConfig
class EmployeePostConfig:
    # BEGINNING OF REQUIRED SECTION ----------------------------------------------
    def __init__(self, lbeObjectTemplate, lbeObjectInstance = None):
        self.template = lbeObjectTemplate
        self.instance = lbeObjectInstance
    # END OF REQUIRED SECTION ----------------------------------------------------
    
    # REQUIRED SECTION FOR LDAP BACKEND ------------------------------------------    

    # These methods are used only for LDAP target. Must be class methods
    # instanceNameAttribute will be used as RDN attribute
    @classmethod
    def base_dn(cls):
        return 'ou=Employees,ou=People,dc=opencsi,dc=com'

    # Note this method must return a list
    @classmethod
    def object_classes(cls):
        return ['top', 'person', 'organizationalPerson','inetOrgPerson']

    # END OF REQUIRED SECTION ----------------------------------------------------

    
    # TODO: Think about implements is_valid method here to be called by LBEObjectInstanceForm if possible    
    # def is_valid():
    def is_valid(self,request):
		valid = True
		for key,val in request.items():
			if re.match('givenName',key):
				print 'TODO'# valid = False or True
		return valid
    
    # Validators methods are used to alter, verify, compute the values of an attribute
    # IMPORTANT: Remembers all attributes are store in a list, even mono valued. Therefore, you must return a list
    
    # Prototype:
    # def clean_<attributeName>(self): (NOT the displayName) for FINAL attributes
    # def compute_<attributeName>(self): (NOT the displayName) for VIRTUAL attributes

    def clean_givenName(self):
		try:
			# TODO: Try to implement a uidNumber
			return [ self.instance.attributes['givenName'][0].capitalize() ]
		except:
			return [ self.instance['givenName'][0].capitalize() ]
    
    def clean_sn(self):
		try:
			return [ self.instance.attributes['sn'][0].capitalize() ]
		except:
			return [ self.instance['sn'][0].capitalize() ]

    def compute_cn(self):
		return [ self.instance.attributes['givenName'][0] + ' ' + self.instance.attributes['sn'][0] ]
    
    def compute_uid(self):
		# TODO: Provide an example to use two letters of the givenName if the uid already exists in the backend
		return [ (self.instance.attributes['givenName'][0][0] + self.instance.attributes['sn'][0].replace(' ', '')).lower() ]

    def compute_mail(self):
        return [ self.compute_uid()[0] + '@opencsi.com' ]
