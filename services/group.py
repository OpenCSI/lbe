# -*- coding: utf-8 -*-
from directory.models import LBEGroupInstance, OBJECT_CHANGE_CREATE_OBJECT
from directory.forms import LBEGroupInstanceForm
from services.object import LBEObjectInstanceHelper


class GroupInstanceHelper(LBEObjectInstanceHelper):
    def __init__(self, lbeGroupTemplate, lbeGroupInstance=None):
        super(GroupInstanceHelper, self).__init__(lbeGroupTemplate, lbeGroupInstance)
        if lbeGroupInstance is not None:
            self.instance = lbeGroupInstance
        else:
            self._backend()
            try:
                self.instance = self.get()
            except BaseException:
                self.instance = LBEGroupInstance(self.template)
        self.attributeName = self.callScriptClassMethod("attribute_name")

    def _compress(self, data):
        if len(data) == 1:
            return {self.attributeName: data[0]}
        else:
            return {self.attributeName: '\0'.join(str(val) for val in data)}

    def _decompress(self, data):
        return data.split('\0')

    def _getValues(self):
        self._backend()
        self.instance = self.backend.searchObjectsByPattern(self.template,self.template.displayName)[0]

    def get(self):
        self._backend()
        return self.backend.searchObjectsByPattern(self.template, self.template.displayName)[0]

    def createTemplate(self, Import=False):
        self._backend()
        self.instance.changes['set'][self.attributeName] = []
        self.instance.changes['set']['cn'] = [self.instance.name]
        self.instance.attributes['cn'] = [self.instance.name]
        if not Import:
            self.instance.changes['type'] = OBJECT_CHANGE_CREATE_OBJECT
        else:
            self.instance.changes['type'] = -1
        return self.backend.createObject(self.template, self.instance, Import)

    def modifyTemplate(self, oldObjectTemplate, oldNameObjectTemplate):
        self._backend()
        return self.backend.modifyGroup(self, oldObjectTemplate, oldNameObjectTemplate)

    def form(self, values=None):
        data = dict()
        data[self.attributeName] = []
        # get values
        if values is not None:
            self.instance.changes['set'][self.attributeName] = values.getlist(self.attributeName)
            data[self.attributeName] = self.instance.changes['set'][self.attributeName]
        else:
            self._getValues()
            try:
                if self.attributeName in self.instance.changes['set'] and not self.instance.changes['set'][self.attributeName] == []:
                    data[self.attributeName] = self.instance.changes['set'][self.attributeName]
                else:
                    data[self.attributeName] = self.instance.attributes[self.attributeName]
            except BaseException:
                pass
        if not 'cn' in self.instance.changes['set'] or self.instance.changes['set']['cn'] == '':
            self.instance.changes['set']['cn'] = [self.instance.displayName]
        # remove empty value
        try:
            data[self.attributeName].remove('')
        except BaseException:
            pass
        # compress values
        data = self._compress(data[self.attributeName])
        # form
        return LBEGroupInstanceForm(self, self.template.objectTemplate, data)

    def save(self):
        self._backend()
        self.backend.modifyObject(self.template, self.instance.name, self.instance.changes['set'], self.instance.name)

    def remove(self):
        self._backend()
        return self.backend.removeObject(self.template, self.template.displayName)

    def changeIDObjects(self):
        self.instance = self.get()
        listOldObjects = self.instance.changes['set'][self.attributeName] or self.instance.attributes[self.attributeName]
        listObjects = []
        for object in listOldObjects:
            try:
                object = self.backend.searchObjectsBy(self.template.objectTemplate, self.template.objectTemplate.instanceNameAttribute.name,
                                            object)[0]
                if object.attributes[self.template.objectTemplate.instanceNameAttribute.name][0] in listOldObjects:
                    listObjects.append(object.name)
            except BaseException:
                pass
        if listObjects:
            self.instance.changes['set'][self.attributeName] = listObjects
            self.save()