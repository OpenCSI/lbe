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
			global error, success
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
					# Skip aliases to prevend schema violations
					aBuffer = attribute.rsplit(' ')
					if aBuffer[3] != '(':
						addAttribute(aBuffer[3])
					else:
						addAttribute(aBuffer[4])
				print success, " attributes added. ", error, " errors (duplicateEntry)"
				error = 0
				success = 0
				for attribute in entry['objectClasses']:
					# Skip aliases to prevend schema violations
					aBuffer = attribute.rsplit(' ')
					if aBuffer[3] != '(':
						addAttribute(aBuffer[3])
					else:
						addAttribute(aBuffer[4])
				print success, " objectClasses added. ", error, " errors (duplicateEntry)"
				
