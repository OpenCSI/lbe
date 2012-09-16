# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from directory.models import LBEObjectTemplate
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
                    # TODO: Whe probably should care about virtual/reference attributes
                    # Example: an object where uid is computed as 'bbonfils', but backend value is 'asyd'
                    backend.createObject(lbeObjectTemplate, lbeObject)
