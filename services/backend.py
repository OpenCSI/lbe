# -*- coding: utf-8 -*-
from services.backend_mongo import BackendMongoImpl


class BackendObjectAlreadyExist(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BackendHelper(BackendMongoImpl):
    pass
