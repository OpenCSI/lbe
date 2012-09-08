from django.core.management.base import BaseCommand, CommandError
from services.LDAPTool import LDAPService
from directory.models import LBEAttribute, LBEObjectClass
from django.db.utils import IntegrityError

import ldap, sys

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
			# Create a DAO 
			try:
				ldaph = LDAPService()
			except ldap.SERVER_DOWN:
				print >> sys.stderr, "Can't reach LDAP server"
				sys.exit(1)
			except ldap.INVALID_CREDENTIALS:
				print >> sys.stderr, "Invalid credentials"
				sys.exit(2)
			for dn,entry in ldaph.search('cn=schema', '(objectClass=*)', ldap.SCOPE_BASE, ['+']):
				# Ugly way to parse a schema entry...
				for attribute in entry['attributeTypes']:
					i = 3
					line = attribute.rsplit(' ') 
					buf = line[i]
					i += 1
					if buf != "(":
						addAttribute(buf)
					else:
						buf = line[i]
						while (buf != ")"):
							addAttribute(buf)
							i += 1
							buf = line[i]
				global error, success
				print success, " attributes added. ", error, " errors (duplicateEntry)"
				error = 0
				success = 0
				for attribute in entry['objectClasses']:
					i = 3
					line = attribute.rsplit(' ') 
					buf = line[i]
					i += 1
					if buf != "(":
						addOC(buf)
					else:
						buf = line[i]
						while (buf != ")"):
							addOC(buf)
							i += 1
							buf = line[i]
				print success, " objectClasses added. ", error, " errors (duplicateEntry)"
				
