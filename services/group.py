# -*- coding: utf-8 -*-
from directory.models import LBEGroupInstance
from directory.forms import LBEGroupInstanceForm
from services.backend import BackendHelper
from django.http import QueryDict


class GroupInstanceHelper():
    def __init__(self, lbeGroupTemplate, lbeGroupInstance=None):
        self.template = lbeGroupTemplate
        if lbeGroupInstance is not None:
            self.instance = lbeGroupInstance
        else:
            self.instance = LBEGroupInstance(self.template)
        self.backend = None

    def _compress(self, data):
        return {'uniqueMember': '\0'.join(str(val) for val in data)}

    def _decompress(self, data):
        return data.split('\0')

    def _getValues(self):
        self._backend()
        values = self.backend.getGroup(self.template)
        self.instance.status = values['status']
        self.instance.attributes = values['attributes']
        self.instance.changes = values['changes']

    def _backend(self):
        if self.backend is not None:
            return
        self.backend = BackendHelper()

    def get(self):
        self._backend()
        return self.backend.getGroup(self.template)

    def saveTemplate(self):
        self._backend()
        return self.backend.createGroup(self.template)

    def modifyTemplate(self):
        self._backend()
        return self.backend.modifyGroup(self.template)

    def form(self, values=None):
        data = {}
        # get values
        if values is not None:
            self.instance.changes['set']['uniqueMember'] = values.getlist('uniqueMember')
            data[u'uniqueMember'] = self.instance.changes['set']['uniqueMember'][0]
        else:
            self._getValues()
            if not self.instance.changes['set'] == {}:
                data[u'uniqueMember'] = self.instance.changes['set']['uniqueMember']
            else:
                data[u'uniqueMember'] = self.instance.attributes['uniqueMember']
        return LBEGroupInstanceForm(self.template.objectTemplate, data)

    def save(self):
        self._backend()
        self.backend.saveGroup(self.template,self.instance)