import datetime
from directory.models import LBEObjectTemplate
from services.backend import BackendHelper
from services.target import TargetHelper
from django.core.management.base import BaseCommand, CommandError
import logging

logger = logging.getLogger(__name__)
#
# Algoritm used for reconciliation:
#
# last_sync = now()
# Foreach object in target:
#   - check if object exists in backend
#   - if no:
#       - Delete object if RECONCILIATION_OBJECT_MODE = 'DELETE'
#       - Create object if RECONCILIATION_OBJECT_MODE = 'CREATE'
#   - else:
#       - apply changeset defined in backend for this object
#       - if RECONCILIATION_ATTRIBUTES_MODE = 'DELETE':
#               - delete target attributes not defined in object template
#
#
# Looking for all object to create:
# foreach object in backend where _synced_at < last_sync
#   - create object in target

#
# TODO: Must be use modifiersDate from target
#
#

def compare_object(lbeObjectTemplate, first, second):
    pass

def update_object(lbeObjectTemplate, fromObject, toObject):
    pass

class Reconciliation():
    def __init__(self):
        self.backend = BackendHelper()
        self.target = TargetHelper()
        self.startDate = datetime.datetime.now()

    def start(self):
        for objectTemplate in LBEObjectTemplate.objects.all():
            # Search objects in backend (by default LDAP)
            for object in self.target.searchObjects(objectTemplate):
                logger.debug('Target object found: ' + object.name)

            # Search existing objects in backend but not found in target


class Command(BaseCommand):
    def handle(self, *args, **options):
        reconciliation = Reconciliation()
        reconciliation.start()