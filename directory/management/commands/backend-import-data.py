from django.core.management.base import BaseCommand, CommandError
from pymongo import Connection, errors
from services.Mongo import MongoService
from directory.models import LBEObject
from django.conf import settings
from services.target import TargetDao
from services.backend import BackendDao

import sys

class Command(BaseCommand):
        def handle(self, *args, **options):
			try:
				backend = BackendDao()
				target = TargetDao()
			except Exception as e:
				print >> sys.stderr, e
				sys.exit (1)
			for lbeObjectDefinition in LBEObject.objects.all():
				for lbeObject in target.searchObjects(lbeObjectDefinition):
					print lbeObject
					backend.addObject(lbeObject)