from django.core.management.base import BaseCommand, CommandError
from pymongo import Connection, errors
from services.Mongo import MongoService
from directory.models import LBEObject
from django.conf import settings
import sys
class Command(BaseCommand):
        def handle(self, *args, **options):
			try:
				mongo = MongoService()
			except errors.AutoReconnect:
				print >> sys.stderr, "Can't connect to MongoDB server (", settings.MONGODB_SERVER['HOST'], ' ',  settings.MONGODB_SERVER['PORT'], " )"
				sys.exit (1)
			for lbeObject in LBEObject.objects.all():
				print lbeObject.baseDN