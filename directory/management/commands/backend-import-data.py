# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from pymongo import Connection, errors
from services.Mongo import MongoService
from directory.models import LBEObjectTemplate
from django.conf import settings
from services.target import TargetHelper
from services.backend import BackendHelper

import sys

class Command(BaseCommand):
        def handle(self, *args, **options):
			try:
				backend = BackendHelper()
				target = TargetHelper()
			except Exception as e:
				print >> sys.stderr, e
				sys.exit (1)
			for lbeObjectTemplate in LBEObjectTemplate.objects.all():
				for lbeObject in target.searchObjects(lbeObjectTemplate):
					backend.createObject(lbeObjectTemplate, lbeObject)
