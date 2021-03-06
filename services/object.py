# -*- coding: utf-8 -*-
import sys
import logging
from services.backend import BackendHelper
import re

logger = logging.getLogger(__name__)
from django.contrib import messages
from django.http import QueryDict
from directory.models import LBEObjectInstance, LBEAttributeInstance, LBEAttribute, ATTRIBUTE_TYPE_FINAL, \
    ATTRIBUTE_TYPE_VIRTUAL, OBJECT_STATE_AWAITING_SYNC, OBJECT_CHANGE_CREATE_OBJECT, \
    OBJECT_STATE_AWAITING_RECONCILIATION
from services.backend import BackendObjectAlreadyExist


class LBEObjectInstanceHelper(object):
    def __init__(self, lbeObjectTemplate, lbeObjectInstance=None):
        self.template = lbeObjectTemplate
        self.instance = lbeObjectInstance
        self.scriptInstance = None
        self.backend = None

    def _backend(self):
        if self.backend is not None:
            return
        self.backend = BackendHelper()

    """
		LOAD Script
	"""

    def _load_script(self):
        if self.scriptInstance is not None:
            return

        # if lbeObjectTemplate.script is defined, create an instance
        scriptName = self.template.script.name
        if scriptName is not None:
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

    def _create_script_instance(self, data=None):
        self._load_script()
        if self.scriptInstance is not None:
            return
        self.scriptInstance = self.scriptClass(self.template, self.instance, data)
        """
            END LOAD Script
        """

    """
		DE/COMPRESS Datas:
	"""

    def _compress_data(self, data):
        query = {}
        for key in data:
            if len(data.getlist(key)) == 1:
                query[key] = data[key]
            else:  # compress MultiValue:
                query[key] = '\0'.join(str(val) for val in data.getlist(key))
        return query

    def decompress_data(self, data):
        query = {}
        for key in data:
            if len(data.getlist(key)) == 1:
                query[key] = data[key]
            else: # decompress MultiValue:
                query[key] = data[key].split('\0')
        return query

    """
		END DE/COMPRESS Datas
	"""

    """
		MANAGE Object/Values:
	"""

    def save(self, ):
        self._checkUnique()
        # Search for an existing object
        searchResult = self.backend.getUserForObject(self.template, self.instance.name)
        if searchResult is None:
            return self.backend.createObject(self.template, self.instance)
        else:
            raise BackendObjectAlreadyExist('Already exists')

    def update(self):
        self._checkUnique()
        self.backend.createObject(self.template, self.instance.changes['set'])

    def getStatus(self, objectName):
        self._backend()
        return self.backend.getStatus(self.template, objectName)

    def modify(self):
        self._checkUnique()
        if not self.backend.getStatus(self.template, self.instance.name) == OBJECT_STATE_AWAITING_RECONCILIATION:
            self.backend.modifyObject(self.template, self.instance.name, self.instance.changes['set'],
                                  self.instance.displayName)
        else:
            raise TypeError("In order to change the Object, Your administrator needs to launch reconciliation first.")

    def remove(self, uid):
        self._backend()
        return self.backend.removeObject(self.template, uid)

    def approval(self, uid):
        self._backend()
        return self.backend.approvalObject(self.template, uid)

    def form(self, uid, data=None):
        if data is None:
            data = self.getValues(uid)
        else:
            data = self._compress_data(data)
        self._create_script_instance(data)
        return self.scriptInstance

    """
		END MANAGE Object/Values:
	"""

    """
		CALL Script
    """

    def callScriptMethod(self, methodName):
        self._create_script_instance()
        method = getattr(self.scriptInstance, methodName)
        return method()

    def callScriptClassMethod(self, methodName):
        self._load_script()
        method = getattr(self.scriptClass, methodName)
        return method()

    def callAttributeScriptMethod(self, attributeType, methodPrefix):
        for attributeInstance in self.template.lbeattributeinstance_set.filter(attributeType=attributeType):
            attributeName = attributeInstance.lbeAttribute.name
            try:
                if not self.instance.changes['set'] == {}:
                    self.instance.changes['set'][attributeName] = self.callScriptMethod(methodPrefix + attributeName)
                else:
                    self.instance.attributes[attributeName] = self.callScriptMethod(methodPrefix + attributeName)
            except AttributeError as e:
                try:
                    self.instance[attributeName] = self.callScriptMethod(methodPrefix + attributeName)
                except AttributeError as e:
                    logger.info(
                        'LBEObjectInstanceHelper: Method ' + methodPrefix + attributeName + ' not found or AttributeError exception. ' + e.__str__())
                    print (
                    'LBEObjectInstanceHelper: Method ' + methodPrefix + attributeName + ' not found or AttributeError exception. ' + e.__str__())

    def applyCustomScript(self):
        # Clean attributes before manage virtuals attributes
        #self.callAttributeScriptMethod(ATTRIBUTE_TYPE_FINAL, 'clean_')
        # Now, compute virtual attributes
        self.callAttributeScriptMethod(ATTRIBUTE_TYPE_VIRTUAL, 'compute_')

    def applyCustomScriptAttribute(self, attribute):
        try:
            attributeInstance = self.template.lbeattributeinstance_set.get(attributeType=ATTRIBUTE_TYPE_FINAL,
                                                                           lbeAttribute=LBEAttribute.objects.get(
                                                                               name__iexact=attribute))
            self.instance[attributeInstance.lbeAttribute.name] = self.callScriptMethod(
                "clean_" + attributeInstance.lbeAttribute.name)
        except BaseException as e:
            print e

    """
		END CALL Script
    """

    def _checkUnique(self):
        self._backend()
        attributesInstance = LBEAttributeInstance.objects.filter(lbeObjectTemplate=self.template, unique=True)
        objectInstances = self.backend.searchObjects(self.template)
        for attribute in attributesInstance:
            for obj in objectInstances:
                if not obj.changes['set'] == {}:
                    if obj.changes['set'].has_key(attribute.lbeAttribute.name) and self.instance.changes['set'].has_key(
                            attribute.lbeAttribute.name) \
                        and not self.instance.name == obj.name:
                        # MultiValue:
                        for objAttribute in obj.changes['set'][attribute.lbeAttribute.name]:
                            for instanceAttribute in self.instance.changes['set'][attribute.lbeAttribute.name]:
                                if objAttribute == instanceAttribute:
                                    raise ValueError("The value '" + str(
                                        self.instance.changes['set'][attribute.lbeAttribute.name][
                                            0]) + "' from the '" + attribute.lbeAttribute.name + "' attribute must be unique.\nPlease change its value or their computed values.")
                else:
                    if obj.attributes.has_key(attribute.lbeAttribute.name) and self.instance.changes['set'].has_key(
                            attribute.lbeAttribute.name) \
                        and not self.instance.name == obj.name:
                        # MultiValue:
                        for objAttribute in obj.attributes[attribute.lbeAttribute.name]:
                            for instanceAttribute in self.instance.changes['set'][attribute.lbeAttribute.name]:
                                if objAttribute == instanceAttribute:
                                    raise ValueError("The value '" + str(
                                        self.instance.changes['set'][attribute.lbeAttribute.name][
                                            0]) + "' from the '" + attribute.lbeAttribute.name + "' attribute must be unique.\nPlease change its value or their computed values.")

    def getValues(self, UID):
        """
		Function enables to get values from attributes fields and
		changes.set fields, return the new values (changes.set > attributes)
        """
        try:
            self._backend()
            valuesUser = self.backend.getUserForObject(self.template, UID)
            # Get all attributes from objects:
            attributes = LBEAttributeInstance.objects.filter(lbeObjectTemplate=self.template)
            d = dict()
            for attribute in attributes:
                # Only FINAL Attributes:
                if attribute.attributeType == 0:
                    try:
                        if valuesUser['changes']['set'].has_key(attribute.lbeAttribute.name):
                            q = QueryDict(attribute.lbeAttribute.name + '=' +
                                          valuesUser['changes']['set'][attribute.lbeAttribute.name][0])
                            q = q.copy()
                            for value in valuesUser['changes']['set'][attribute.lbeAttribute.name][1:]:
                                q.update({attribute.lbeAttribute.name: value})
                            d[attribute.lbeAttribute.name] = self._compress_data(q)[attribute.lbeAttribute.name]
                        else:
                            q = QueryDict(attribute.lbeAttribute.name + '=' +
                                          valuesUser['attributes'][attribute.lbeAttribute.name][0])
                            q = q.copy()
                            for value in valuesUser['attributes'][attribute.lbeAttribute.name][1:]:
                                q.update({attribute.lbeAttribute.name: value})
                            d[attribute.lbeAttribute.name] = self._compress_data(q)[attribute.lbeAttribute.name]
                    except BaseException:
                        d[attribute.lbeAttribute.name] = attribute.defaultValue
            return d
        except BaseException:
            # Create part:
            return None

    def getObject(self, UID):
        self._backend()
        return self.backend.searchObjectsByPattern(self.template, UID)[0]

    def searchPattern(self, pattern):
        self._backend()
        objects = self.backend.searchObjects(self.template)
        tabResult = []

        prog = re.compile(pattern, re.I)

        for object in objects:
            # check the status object & get its values
            if object.status == OBJECT_STATE_AWAITING_SYNC:
                objectValues = object.changes['set']
            else:
                objectValues = object.attributes
            # check values and pattern corresponding
            correspond = ''
            for key, values in objectValues.items():
                for cel in values:
                    if prog.search(cel):
                        attributeDisplayName = LBEAttribute.objects.get(name__iexact=key).displayName
                        correspond += cel.lower().replace(pattern, '<b>' + pattern + '</b>') + ' (<i>' + attributeDisplayName + '</i>) '
            if correspond:
                tabResult.append({'object': self.template.id, "name": object.name, 'displayName': object.displayName,
                                  "values": correspond})
        return tabResult

    def getValuesDecompressed(self, UID):
        """
		Function enables to get values from attributes fields and
		changes.set fields, return the new values (changes.set > attributes)
        """
        self._backend()
        valuesUser = self.backend.getUserForObject(self.template, UID)
        # Get all attributes from objects:
        attributes = LBEAttributeInstance.objects.filter(lbeObjectTemplate=self.template).order_by('position')
        d = dict()
        for attribute in attributes:
            try:
                if valuesUser['changes']['set'].has_key(attribute.lbeAttribute.name):
                    d[attribute.lbeAttribute.name] = valuesUser['changes']['set'][attribute.lbeAttribute.name]
                else:
                    d[attribute.lbeAttribute.name] = valuesUser['attributes'][attribute.lbeAttribute.name]
            except KeyError:
                # if no values, just set the default value:
                d[attribute.lbeAttribute.name] = attribute.defaultValue
        return d

    def createFromDict(self, request):
        # Reinit script configuration file:
        self.scriptInstance = None
        # attributes:
        attributes = {}
        for attributeInstance in self.template.lbeattributeinstance_set.all():
            # Only fetch real attributes from the request (mono and/or multi values)
            if attributeInstance.attributeType == ATTRIBUTE_TYPE_FINAL:
                attributeName = attributeInstance.lbeAttribute.name
                if len(request.POST[attributeName].split('�')) > 1:
                    attributes[attributeName] = request.POST[attributeName].split('�')
                else:
                    attributes[attributeName] = [request.POST[attributeName]]
            # IMPORTANT: We need to create an instance without the uniqueBecause because it may be a computed attribute, for example uid (compute from firstname/name)
        self.instance = LBEObjectInstance(self.template, attributes=attributes)
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
            messages.add_message(request, messages.ERROR,
                                 'nameAttribute or displayNameAttribute does not exist in object attributes')


    def updateFromDict(self, ID, values):
        self.scriptInstance = None
        self.instance = LBEObjectInstance(self.template, attributes=None)
        self.instance.changes['set'] = values
        self.instance.attributes = values
        # compute attributes:
        self._create_script_instance()
        self.applyCustomScript()
        # set them (if not been yet) to array:
        for key in self.instance.attributes:
            if isinstance(self.instance.attributes[key], str) or isinstance(self.instance.attributes[key], unicode):
                self.instance.attributes[key] = [self.instance.attributes[key]]
            # change the displayName value:
        self.instance.displayName = self.instance.changes['set'][self.template.instanceDisplayNameAttribute.name][0]
        # ID object:
        self.instance.name = ID

    def compute(self, lbeObjectInstance):
        self.instance = lbeObjectInstance
        self._create_script_instance()
        # Do not make change if changes.set is empty:
        if not lbeObjectInstance.changes['set'] == {}:
            self.applyCustomScript()
