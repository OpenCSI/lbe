from django.core.management.base import BaseCommand, CommandError
from directory.models import LBEAttribute, LBEObjectClass
from django.db.utils import IntegrityError
from services.target import TargetDao, TargetConnectionError, TargetInvalidCredentials

import sys

error = 0
success = 0

def addAttribute(name):
	global error, success
	name = name.replace("'", '')
	try:
		attr = LBEAttribute(name = name, displayName = name)
		attr.save()
		success += 1
	except IntegrityError,e:
		error += 1
	
def addOC(name):
	global error, success
	name = name.replace("'", '')
	try:
		attr = LBEObjectClass(name = name)
		attr.save()
		success += 1
	except IntegrityError,e:
		error += 1

class Command(BaseCommand):
        def handle(self, *args, **options):
			global error, success
			try:
				# TargetSchema is a service to access to the backend schema (cn=schema for LDAP)
				target = TargetDao()
			except ConnectionError:
				print >> sys.stderr, 'Connecting to backend failed, check lbe/settings.py'
				sys.exit (1)
			for attribute in target.getAttributes():
				addAttribute(attribute)
			print success, " attributes added. ", error, " errors (duplicateEntry)"
			success = 0
			error = 0
			for objectClass in target.getObjectClasses():
				addOC(objectClass)
			print success, " objectclasses added. ", error, " errors (duplicateEntry)"
	
