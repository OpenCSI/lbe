# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from directory.management.commands.cli.group import CLIGroup

class Command(BaseCommand):
    def handle(self, *args, **options):
        if 'create-group' in args:
            cGroup = CLIGroup()
            cGroup.create()