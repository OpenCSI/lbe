# -*- coding: utf-8 -*-
import sys, logging
from services.backend import BackendHelper
logger = logging.getLogger(__name__)
from django.contrib import messages
from django.http import QueryDict
from directory.models import LBEObjectInstance, LBEAttributeInstance, LBEAttribute, ATTRIBUTE_TYPE_FINAL, ATTRIBUTE_TYPE_VIRTUAL, ATTRIBUTE_TYPE_REFERENCE, OBJECT_STATE_AWAITING_SYNC, OBJECT_CHANGE_CREATE_OBJECT
from services.backend import BackendObjectAlreadyExist

class LBEObjectInstanceHelper():
    def __init__(self, lbeObjectTemplate):
        self.template = lbeObjectTemplate
        self.ID = None
        self.instance = None
        self.scriptInstance = None
        self.backend = None
		
    def _backend(self):
        if self.backend is not None:
            return
        self.backend = BackendHelper()

    def _load_script(self):
        if self.scriptInstance is not None:
            return
        
        # if lbeObjectTemplate.script is defined, create an instance
        scriptName = self.template.script.name
        if scriptName is not None :
            # the scriptName is like 'custom.employee.EmployeePostConfig', so we need to extract the module, aka custom.employee
            moduleName = '.'.join(scriptName.split('.')[:-1])
            # and the classname, EmployeePostConfig
            className = scriptName.split('.')[-1]
            __import__(moduleName)
            module = sys.modules[moduleName]
            self.scriptClass = getattr(module, className)
            # Create an instance
            #self.scriptInstance = self.scriptClass(self.template,self.instance)
        else:
            logging.error('This object does not have an associate script')

    def _create_script_instance(self,data = None):
        self._load_script()
        if self.scriptInstance is not None:
            return
        if data is not None:
			self.instance = LBEObjectInstance(self.instance,data)
        print self.instance.attributes
        self.scriptInstance = self.scriptClass(self.template, self.instance,data)

    def save(self, ):
        self._backend()
        # Search for an existing object
        searchResult = self.backend.getObjectByName(self.template, self.instance.name)
        if searchResult is None:
            return self.backend.createObject(self.template, self.instance)
        else:
            raise BackendObjectAlreadyExist('Already exists')

    def update(self):
        self._backend()
        self.backend.createObject(self.template, self.instance)
        
    def modify(self):
		self._backend()
		self.backend.modifyObject(self.template,self.ID,self.instance)
		
    def form(self,uid,data=None):
        if data is None:
            data = self.getValues(uid)
        self._create_script_instance(data)
        return self.scriptInstance

    def callScriptMethod(self, methodName):
        self._create_script_instance()
        method = getattr(self.scriptInstance, methodName)
        return method()

    def callScriptClassMethod(self, methodName):
        self._load_script()
        method = getattr(self.scriptClass, methodName)
        return method()

    def callAttributeScriptMethod(self, attributeType, methodPrefix):
        for attributeInstance in self.template.lbeattributeinstance_set.filter(attributeType= attributeType):
            attributeName = attributeInstance.lbeAttribute.name
            try:
                self.instance.attributes[attributeName] = self.callScriptMethod(methodPrefix + attributeName)
            except AttributeError as e:
                try:
                    self.instance[attributeName] = self.callScriptMethod(methodPrefix + attributeName)
                except AttributeError as e:
                    logger.info('LBEObjectInstanceHelper: Method ' + methodPrefix + attributeName + ' not found or AttributeError exception. ' + e.__str__())
			
    def applyCustomScript(self):
		# Clean attributes before manage virtuals attributes
		self.callAttributeScriptMethod(ATTRIBUTE_TYPE_FINAL, 'clean_')
		# Now, compute virtual attributes
		self.callAttributeScriptMethod(ATTRIBUTE_TYPE_VIRTUAL, 'compute_')
    
    def applyCustomScriptAttribute(self,attribute):
		try:
			attributeInstance = self.template.lbeattributeinstance_set.get(attributeType= ATTRIBUTE_TYPE_FINAL, lbeAttribute= LBEAttribute.objects.get(name__iexact=attribute))
			self.instance[attributeInstance.lbeAttribute.name] = self.callScriptMethod("clean_" + attributeInstance.lbeAttribute.name)
		except BaseException as e:
			print e
	
    def getValues(self,UID):
        """
		Fonction enables to get values from attributes fields and
		changes.set fields, return the new values (changes.set > attributes)
        """
        self._backend()
        valuesUser = self.backend.getObjectByName(self.template, UID)
        # Get all attributes from objects:
        attributes = LBEAttributeInstance.objects.filter(lbeObjectTemplate = self.template)
        d = dict()
        for attribute in attributes:
			if valuesUser['changes']['set'].has_key(attribute.lbeAttribute.name):
				d[attribute.lbeAttribute.name] = valuesUser['changes']['set'][attribute.lbeAttribute.name][0]
			else:
				d[attribute.lbeAttribute.name] = valuesUser['attributes'][attribute.lbeAttribute.name][0] or ""
        return d
	
    def createFromDict(self, request):
        attributes = {}
        for attributeInstance in self.template.lbeattributeinstance_set.all():
            # Only fetch real attributes from the request
            if attributeInstance.attributeType == ATTRIBUTE_TYPE_FINAL:
                attributeName = attributeInstance.lbeAttribute.name
                # TODO: manage multivalue here
                attributes[attributeName] = [ request.POST[attributeName] ]
        # IMPORTANT: We need to create an instance without the uniqueBecause because it may be a computed attribute, for example uid (compute from firstname/name)
        self.instance = LBEObjectInstance(self.template, attributes = attributes)
        # TODO: Maybe check here if the object need approvals
        self.instance.status = OBJECT_STATE_AWAITING_SYNC
        self.applyCustomScript()
        # Set uniqueName and displayName
        try:
            self.instance.name = self.instance.attributes[self.template.instanceNameAttribute.name][0]
            self.instance.displayName = self.instance.attributes[self.template.instanceDisplayNameAttribute.name][0]
            # It's a new object, the changesSet apply to all attributes
            self.instance.changes['type'] = OBJECT_CHANGE_CREATE_OBJECT
            self.instance.changes['set'] = self.instance.attributes
        except BaseException as e:
            print e.__str__()
            # TODO: Remove technical message, use another handler to send message to administrator
            messages.add_message(request, messages.ERROR, 'nameAttribute or displayNameAttribute does not exist in object attributes')
        print self.instance.attributes

	# IMPROVE:
    def updateFromDict(self,ID,values):
        self._backend()
        backendValues = self.backend.getObjectByName(self.template,ID)
		# Get values; attr; pos:
        qDict = QueryDict('')
        qDict = qDict.copy()# make it mutable
        for keyB,valB in backendValues['changes']['set'].items():
            for key,val in values.items():
                if keyB == key.split('_')[0]:
                    # is multivalues?:
                    attribute = LBEAttributeInstance.objects.get(lbeObjectTemplate = self.template,lbeAttribute=LBEAttribute.objects.get(name__iexact=keyB))
                    if attribute.multivalue:
                        pos = int(key.split('_')[1])
                        cur = 0
                        tabValue = list()
                        added = False
                        for value in valB:
                            if pos == cur:
							    tabValue.append(val)
							    added = True
                            else:
                                tabValue.append(value)
                            cur += 1
                        if not added:# new value
							tabValue.append(val)
                        qDict[keyB] = tabValue
                    else:
					    qDict[keyB] = [val]
        self.instance = qDict
        self.ID = ID
        for key in values:
			self.applyCustomScriptAttribute(key.split('_')[0])
        #return self.instance
        
    def removeFromDict(self,ID,values):
        self._backend()
        backendValues = self.backend.getObjectByName(self.template,ID)
        qDict = QueryDict('')
        qDict = qDict.copy()# make it mutable
        for keyV, attrV in values.items():
			# get the attribute position:
			key, pos = keyV.split('_')
			# check if this value exists on attributes field, if not:
			# we can remove it, else set it empty.
			replace = backendValues['attributes'].has_key(key) and len(backendValues['attributes'][key]) >= int(pos)+1 # boolean
			num = 0
			tabValue = list()
			for val in backendValues['changes']['set'][key]:
				if num == int(pos):
					if replace:
						tabValue.append("")
				else:
					tabValue.append(val)
				num += 1
			qDict[key] = tabValue
        self.instance = qDict
        self.ID = ID
        return not replace # remove
