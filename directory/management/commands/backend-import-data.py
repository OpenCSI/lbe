# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from directory.models import LBEObjectTemplate
from services.target import TargetHelper
from services.backend import BackendHelper
from django.utils.timezone import utc

import logging, datetime
import sys

logger = logging.getLogger(__name__)

class Command(BaseCommand):
        def handle(self, *args, **options):
            try:
                backend = BackendHelper()
                target = TargetHelper()
            except Exception as e:
                print >> sys.stderr, e
                sys.exit (1)
            for lbeObjectTemplate in LBEObjectTemplate.objects.all():
                now = datetime.datetime.now(utc)
                # the searchNewObjectcs methods search for backend object where createTimestamp > objectTemplate.imported_at
                for lbeObject in target.searchNewObjects(lbeObjectTemplate):
                    #
                    # TODO: take care about virtual/reference attributes
                    # Example: an object where uid is computed as 'bbonfils', but backend value is 'asyd'
                    lbeObject.synced_at = now
                    backend.createObject(lbeObjectTemplate, lbeObject)
                lbeObjectTemplate.imported_at = now
                lbeObjectTemplate.save()