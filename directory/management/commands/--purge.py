# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from services.backend import BackendHelper

from directory.models import LBEObjectTemplate, OBJECT_STATE_DELETED


class Purge():
    def __init__(self):
        self.backend = BackendHelper()

    def start(self, *objects):
        for obj in objects[0]:
            print '   |-> Purging \033[90m' + obj + '\033[0m Object...'
            try:
                o = LBEObjectTemplate.objects.get(name=obj)
                for objectInstance in self.backend.searchObjects(o):
                    if objectInstance.status == OBJECT_STATE_DELETED:
                        print '   ||-> Removing \033[94m' + objectInstance.name + '\033[0m instance object...'
                        self.backend.deleteObject(o, objectInstance.name)
            except BaseException:
                print '   |-> \033[91mThe object "' + obj + '" does not exist.\033[0m'
                pass
        return 0


class Command(BaseCommand):
    def handle(self, *args, **options):
        print "Begin:"
        purge = Purge()
        if len(args) == 0:
            print "   \033[91mYou need to specify at least one ObjectTemplate.\033[0m"
        else:
            purge.start(args)
        print "End."
