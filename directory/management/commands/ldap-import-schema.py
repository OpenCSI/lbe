from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
        def handle(self, *args, **options):
                print 'LDAP:' + settings.LDAP_SERVER['baseDN']