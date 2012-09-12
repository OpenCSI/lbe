from directory.models import LBEObjectInstance, OBJECT_TYPE_FINAL

class LBEObjectInstanceHelper():
	def __init__(self, lbeObjectTemplate):
		self.template = lbeObjectTemplate
		self.instance = None
		
	def saveObject():
		# TODO: Inject Target method here
		return True
		
	def createFromDict(postData):
		# First of all, compute DN for this object
		objectDN = self.template.rdnAttribute.name + '=' + postData[template.rdnAttribute.name] + ',' + self.template.baseDN
		self.instance = LBEObjectInstance(objectDN, self.template, postData[template.rdnAttribute.name]) 
		for attributeInstance in self.template.lbeattributeinstance_set.all():
			# Only fetch real attributes from the request
			if attributeInstance.objectType == OBJECT_TYPE_FINAL:
				attributeName = attributeInstance.lbeattribute.name
				# TODO: manage multivalue heres
				self.instance.addAttribute(attributeName, [ postData[attributeName] ] )
				print self.instance.attributes
			# Compute virtual attributes
			elif attribute.objectType == OBJECT_TYPE_VIRTUAL:
				pass
			#Compute reference attributes
			elif attribute.objectType == OBJECT_TYPE_REFERENCE:
				pass
