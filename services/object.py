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
        else:
            logging.error('This object does not have an associate script')

    def _create_script_instance(self):
        self._load_script()
        if self.scriptInstance is not None:
            return
        self.scriptInstance = self.scriptClass(self.template, self.instance)

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
                logger.info('LBEObjectInstanceHelper: Method ' + methodPrefix + attributeName + ' not found or AttributeError exception. ' + e.__str__())
    
    def applyCustomScript(self):
        # Clean attributes before manage virtuals attributes
        self.callAttributeScriptMethod(ATTRIBUTE_TYPE_FINAL, 'clean_')
        # Now, compute virtual attributes
        self.callAttributeScriptMethod(ATTRIBUTE_TYPE_VIRTUAL, 'compute_')
        
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
		# TODO:
		# replace all attribute key (without the number) [dict(key:{ value, position })] (ex: dict(cn:{Cédric,0}) )
		# check for multivalues attributes.
		# if multivalues:
		# 	 get values and replace the new one. (or add it)
		# else:
		#	 replace value.
		# get backend values for changes.set:
        self._backend()
        backendValues = self.backend.getObjectByName(self.template,ID)
		# Get values; attr; pos:
        qDict = QueryDict('')
        qDict = qDict.copy()# make it mutable
        for keyB,valB in backendValues['changes']['set'].items():
            #dic = {}
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
