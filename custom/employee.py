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
	
	# # We use a virtual attribute to inject LDAP objectClasses required by this object
	# def compute_objectClass():
	# 	return [ 'top', 'person', 'organizationalPerson', 'inetOrgPerson' ]
		
	# Compute the virtual attribute dn
	def compute_cn(self):
		# You may raise an exception here too
		# IMPORTANT: Remember than every attribute are stored in a list
		return [self.instance.attributes['firstname'][0] + ' ' + self.instance.attributes['lastname'][0]]
	
	# Validators, only called for real attributes, the returned value will override the one given in the form
	def clean_givenName(self):
		print 'clean_givenName method called'
		# You may raise a Validator exception, for example to ensure an uniquess of a computed attribute (like uidNumber)
		return [self.instance.attributes['givenName'][0].capitalize()]
	
	def clean_sn(self):
		return [self.instance.attributes['sn'][0].capitalize()]