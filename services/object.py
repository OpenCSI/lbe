# -*- coding: utf-8 -*-
import sys, logging

from directory.models import LBEObjectInstance, OBJECT_TYPE_FINAL, OBJECT_TYPE_VIRTUAL, OBJECT_TYPE_REFERENCE

class LBEObjectInstanceHelper():
	def __init__(self, lbeObjectTemplate):
		self.template = lbeObjectTemplate
		self.instance = None
		self.scriptInstance = None
			
	def __load_script(self):
		# if lbeObjectTemplate.script is defined, create an instance
		scriptName = self.template.script.name
		if ( scriptName != None ):
			# Explanation: the scriptName is like 'custom.employee.EmployeePostConfig', so we need to extract the module, aka custom.employee
			moduleName = '.'.join(scriptName.split('.')[:-1])
			# and the classname, EmployeePostConfig
			className = scriptName.split('.')[-1]
			try:
				__import__(moduleName)
				module = sys.modules[moduleName]
				scriptClass = getattr(module, className)
		
				# Create an instance
				self.scriptInstance = scriptClass(self.template, self.instance)
			except BaseException, e:
				logging.error('Error while loading script: ' + scriptName)
		else:
			logging.error('This object does not have an associate script')
	

	def saveObject(self):
		# TODO: Inject backend method here
		return True
	
	def applyCustomScript(self):
		if (self.scriptInstance == None):
			self.__load_script()
		
		# Clean attributes before manage virtuals attributes
		for attributeInstance in self.template.lbeattributeinstance_set.filter(objectType= OBJECT_TYPE_FINAL):
			attributeName = attributeInstance.lbeAttribute.name
			try:
				method = getattr(self.scriptInstance, 'clean_' + attributeName)
				self.instance.attributes[attributeName] = method()
			except AttributeError, e:
				# No method is implement for this attribute, do nothing
				print e
		# Now, compute virtual attributes
		for attributeInstance in self.template.lbeattributeinstance_set.filter(objectType= OBJECT_TYPE_VIRTUAL):
			attributeName = attributeInstance.lbeAttribute.name
			try:
				method = getattr(self.scriptInstance, 'compute_' + attributeName)
				self.instance.attributes[attributeName] = method()
			except AttributeError, e:
				# No method is implement for this attribute, do nothing
				pass
		print self.instance.attributes
		
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
		# objectDN = self.template.uniqueAttribute.name + '=' + postData[self.template.uniqueAttribute.name] + ',' + self.template.baseDN
		# Add objectClasses
		# TODO: Need refactoring
		ocList = []
		for objectClass in self.template.objectClasses.all():
			ocList.append(objectClass.name)
		attributes['objectClass'] = ocList
		# FIXME: Grr, how to manage the rdn attribute well..
		self.instance = LBEObjectInstance(objectDN, self.template, 'blah', attributes)
		print self.instance.attributes
#		self.instance = LBEObjectInstance(objectDN, self.template, postData[self.template.uniqueAttribute.name], attributes)
		self.applyCustomScript()
		print self.instance.attributes
		return self.instance
