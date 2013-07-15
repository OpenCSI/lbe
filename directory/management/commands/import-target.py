from django.core.management.base import BaseCommand, CommandError
from services.backend import BackendHelper
from services.target import TargetHelper
import datetime

from directory.models import LBEObjectTemplate

class ImportTarget():
	def __init__(self):
		self.backend = BackendHelper()
		self.target = TargetHelper()
		self.start_date = datetime.datetime.now()
        
	def save(self):
		print 'Checking for Objects which do not exist into LBE but in LDAP Server:'
		for objectTemplate in LBEObjectTemplate.objects.all():
			print '\033[91m' + objectTemplate.name + '\033[0m:'
			objTarget = self.target.searchObjects(objectTemplate)
			objBackend = self.backend.searchObjects(objectTemplate)
			number = 0
			for ot in objTarget:
				exist = False
				for ob in objBackend:
					if ot.name == ob.name:
						exist = True
						break
				if not exist:
					number += 1
					print 'Adding \033[95m' + ot.name + '\033[0m object into LBE Backend... '
					try:
						self.backend.createObject(objectTemplate,ot,True)
						print "\033[92mDone.\033[0m"
					except BaseException as e:
						print "\033[91mFail.\033[0m"
						print "''''''''"
						print e
						print "''''''''"
			if number == 0:
				print '<None>'
			# Synced object:
			objectTemplate.synced_at = datetime.datetime.now()
			objectTemplate.save()
			print '.........................'
		
class Command(BaseCommand):
	def handle(self, *args, **options):
		importTarget = ImportTarget()
		importTarget.save()
