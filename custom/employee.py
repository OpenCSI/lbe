from directory.models import LBEObjectTemplate, LBEObjectInstance

#
# This file is an example of script called after object creation
#

# TODO: Probably use a better suffix than PostConfig
class EmployeePostConfig:
	def __init__(self, lbeObjectTemplate, lbeObjectInstance):
		self.template = lbeObjectTemplate
		self.instance = lbeObjectInstance
	
	# TODO: Think about implements is_valid method here to be called by LBEObjectInstanceForm if possible	
	# def is_valid():
	
	# Validators, only called for final attributes, attributes will be overridden
	def clean_givenName(self):
		# TODO: Try to implement a uidNumber
		return [self.instance.attributes['givenName'][0].capitalize()]
	
	def clean_sn(self):
		return [self.instance.attributes['sn'][0].capitalize()]

	# Compute the virtual attribute cn
	def compute_cn(self):
		# IMPORTANT: Remember than attributes are stored in a list, even mono valued
		return [ self.instance.attributes['givenName'][0] + ' ' + self.instance.attributes['sn'][0] ]
	
	def compute_uid(self):
		return [ (self.instance.attributes['givenName'][0][0] + self.instance.attributes['sn'][0]).lower() ]

	def compute_mail(self):
		return [ self.compute_uid()[0] + '@opencsi.com' ]
		
	# These methods are used only for LDAP target. Must be class methods
	@classmethod
	def base_dn(className):
		return 'ou=Employee,ou=People,dc=opencsi,dc=com'
	
	@classmethod
	def object_classes(className):
		return ['top', 'person', 'organizationalPerson','inetOrgPerson']
