# -*- coding: utf-8 -*-
import sys, logging
from services.backend import BackendHelper
logger = logging.getLogger(__name__)

from directory.models import LBEObjectInstance, ATTRIBUTE_TYPE_FINAL, ATTRIBUTE_TYPE_VIRTUAL, ATTRIBUTE_TYPE_REFERENCE

class LBEObjectInstanceHelper():
    def __init__(self, lbeObjectTemplate):
        self.template = lbeObjectTemplate
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
            scriptClass = getattr(module, className)
        
            # Create an instance
            self.scriptInstance = scriptClass(self.template, self.instance)
        else:
            logging.error('This object does not have an associate script')
    
    def save(self):
        self._backend()
        self.backend.createObject(self.template, self.instance)

    def callScriptMethod(self, methodName):
        self._load_script()
        method = getattr(self.scriptInstance, methodName)
        return method()

    def callAttributeScriptMethod(self, attributeType, methodPrefix):
        self._load_script()
        
        for attributeInstance in self.template.lbeattributeinstance_set.filter(attributeType= attributeType):
            attributeName = attributeInstance.lbeAttribute.name
            try:
                self.instance.attributes[attributeName] = self.callScriptMethod(methodPrefix + attributeName)
            except AttributeError as e:
                logger.info('LBEObjectInstanceHelper: Method ' + methodPrefix + attributeName + ' not found or AttributeError exception. ' + e.message)
    
    def applyCustomScript(self):
        # Clean attributes before manage virtuals attributes
        self.callAttributeScriptMethod(ATTRIBUTE_TYPE_FINAL, 'clean_')
        # Now, compute virtual attributes
        self.callAttributeScriptMethod(ATTRIBUTE_TYPE_VIRTUAL, 'compute_')
        
    def createFromDict(self, postData):
        attributes = {}
        for attributeInstance in self.template.lbeattributeinstance_set.all():
            # Only fetch real attributes from the request
            if attributeInstance.attributeType == ATTRIBUTE_TYPE_FINAL:
                attributeName = attributeInstance.lbeAttribute.name
                # TODO: manage multivalue here
                attributes[attributeName] = [ postData[attributeName] ]
        # IMPORTANT: We need to create an instance without the name because the unique attribut may be a computed attribute, for example uid (compute from firstname/name)
        self.instance = LBEObjectInstance(self.template, attributes = attributes)
        self.applyCustomScript()
        # Set uniqueName and displayName
        self.instance.name = self.instance.attributes[self.template.instanceNameAttribute.name][0]
        self.instance.displayName = self.instance.attributes[self.template.instanceDisplayNameAttribute.name][0]
        print self.instance.attributes