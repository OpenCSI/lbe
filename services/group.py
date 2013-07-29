# -*- coding: utf-8 -*-
from directory.models import LBEGroupInstance
from directory.forms import LBEGroupInstanceForm
from services.object import LBEObjectInstanceHelper


class GroupInstanceHelper(LBEObjectInstanceHelper):
    def __init__(self, lbeGroupTemplate, lbeGroupInstance=None):
        super(GroupInstanceHelper, self).__init__(lbeGroupTemplate, lbeGroupInstance)
        if lbeGroupInstance is not None:
            self.instance = lbeGroupInstance
        else:
            self.instance = LBEGroupInstance(self.template)

    def _compress(self, data):
        if len(data) == 1:
            return {u'uniqueMember': data[0]}
        else:
            return {u'uniqueMember': '\0'.join(str(val) for val in data)}

    def _decompress(self, data):
        return data.split('\0')

    def _getValues(self):
        self._backend()
        self.instance = self.backend.searchObjectsByPattern(self.template,self.template.displayName)[0]

    def get(self):
        self._backend()
        return self.backend.searchObjectsByPattern(self.template,self.template.displayName)[0]

    def createTemplate(self):
        self._backend()
        self.instance.changes['set']['uniqueMember'] = []
        self.instance.changes['set']['cn'] = ''
        return self.backend.createObject(self.template, self.instance)

    def modifyTemplate(self, oldObjectTemplate, oldNameObjectTemplate):
        self._backend()
        return self.backend.modifyGroup(self.template, self.instance, oldObjectTemplate, oldNameObjectTemplate)

    def form(self, values=None):
        data = dict()
        data[u'uniqueMember'] = ''
        # get values
        if values is not None:
            self.instance.changes['set']['uniqueMember'] = values.getlist('uniqueMember')
            data[u'uniqueMember'] = self.instance.changes['set']['uniqueMember']
        else:
            self._getValues()
            try:
                if not self.instance.changes['set'] == {}:
                    data[u'uniqueMember'] = self.instance.changes['set']['uniqueMember']
                else:
                    data[u'uniqueMember'] = self.instance.attributes['uniqueMember']
            except BaseException:
                pass
        # remove empty value
        try:
            data[u'uniqueMember'].remove('')
        except BaseException:
            pass
        # compress values
        data = self._compress(data[u'uniqueMember'])
        # form
        return LBEGroupInstanceForm(self.template.objectTemplate, data)

    def save(self):
        self._backend()
        self.backend.modifyObject(self.template, self.instance.name, self.instance.changes['set'], self.instance.name)

    def remove(self):
        self._backend()
        return self.backend.removeObject(self.template, self.template.displayName)

    def changeIDObjects(self):
        self.instance = self.get()
        listOldObjects = self.instance.changes['set']['uniqueMember'] or self.instance.attributes['uniqueMember']
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
            self.instance.changes['set']['uniqueMember'] = listObjects
            self.save()