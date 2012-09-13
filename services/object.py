import sys
from directory.models import LBEObjectInstance, OBJECT_TYPE_FINAL, OBJECT_TYPE_VIRTUAL, OBJECT_TYPE_REFERENCE

class LBEObjectInstanceHelper():
	def __init__(self, lbeObjectTemplate):
		self.template = lbeObjectTemplate
		self.instance = None
		
	def saveObject():
		# TODO: Inject Target method here
		return True
	
	def applyCustomScript(self, moduleName, className):
		# Import specified class from module
		__import__(moduleName)
		module = sys.modules[moduleName]
		postClass = getattr(module, className)
		
		# Call constructor
		postClassInstance = postClass(self.template, self.instance)
		
		# Apply functions
		for attributeInstance in self.template.lbeattributeinstance_set.all():
			# Apply clean_<attribute> methods on final attributes
			attributeName = attributeInstance.lbeAttribute.name
			try:
				prefix = ''
				if attributeInstance.objectType == OBJECT_TYPE_FINAL:
					prefix = 'clean_'
				elif attributeInstance.objectType == OBJECT_TYPE_VIRTUAL:
					prefix = 'compute_'
				method = getattr(postClassInstance, prefix + attributeName)
				self.instance.attributes[attributeName] = method()
			except AttributeError, e:
				# No method is implement for this attribute, do nothing
				print e
				pass
		
	def createFromDict(self, postData):
		attributes = {}
		for attributeInstance in self.template.lbeattributeinstance_set.all():
			# Only fetch real attributes from the request
			if attributeInstance.objectType == OBJECT_TYPE_FINAL:
				attributeName = attributeInstance.lbeAttribute.name
				# TODO: manage multivalue heres
				attributes[attributeName] = [ postData[attributeName] ]
		# Finally, create the objecte
		# Hard code dn for the moment
		objectDN = 'cn=test,dc=opencsi,dc=com'
		# objectDN = self.template.rdnAttribute.name + '=' + postData[self.template.rdnAttribute.name] + ',' + self.template.baseDN
		# Add objectClasses
		# TODO: Need refactoring
		ocList = []
		for objectClass in self.template.objectClasses.all():
			ocList.append(objectClass.name)
		attributes['objectClass'] = ocList
		# FIXME: Grr, how to manage the rdn attribute well..
		self.instance = LBEObjectInstance(objectDN, self.template, 'blah', attributes)
#		self.instance = LBEObjectInstance(objectDN, self.template, postData[self.template.rdnAttribute.name], attributes)
		print 'Initial attributes:', self.instance.attributes
		self.applyCustomScript('custom.employee', 'EmployeePostConfig')
		print 'Computed attributes:', self.instance.attributes
		return self.instance