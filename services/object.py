from directory.models import LBEObjectInstance, OBJECT_TYPE_FINAL, OBJECT_TYPE_VIRTUAL, OBJECT_TYPE_REFERENCE

class LBEObjectInstanceHelper():
	def __init__(self, lbeObjectTemplate):
		self.template = lbeObjectTemplate
		self.instance = None
		
	def saveObject():
		# TODO: Inject Target method here
		return True
		
	def createFromDict(self, postData):
		attributes = {}
		for attributeInstance in self.template.lbeattributeinstance_set.all():
			# Only fetch real attributes from the request
			if attributeInstance.objectType == OBJECT_TYPE_FINAL:
				attributeName = attributeInstance.lbeAttribute.name
				# TODO: manage multivalue heres
				attributes[attributeName] = [ postData[attributeName] ]
			# Compute virtual attributes
			elif attributeInstance.objectType == OBJECT_TYPE_VIRTUAL:
				# TODO:
				pass
			#Compute reference attributes
			elif attributeInstance.objectType == OBJECT_TYPE_REFERENCE:
				# TODO:
				pass
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
		print attributes
		self.instance = LBEObjectInstance(objectDN, self.template, postData[self.template.rdnAttribute.name], attributes) 
		return self.instance