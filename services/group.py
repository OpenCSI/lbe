# -*- coding: utf-8 -*-
from services.backend import BackendHelper


class GroupInstanceHelper():
    def __init__(self, lbeGroupTemplate, lbeGroupInstance=None):
        self.template = lbeGroupTemplate
        self.instance = lbeGroupInstance
        self.backend = None

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