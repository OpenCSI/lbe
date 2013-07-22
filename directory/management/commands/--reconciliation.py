# -*- coding: utf-8 -*-
import logging

from django.core.management.base import BaseCommand

from directory.management.commands.reconciliation.upgradeTarget import UpgradeTarget
from directory.management.commands.reconciliation.upgradeBT import UpgradeBT
from directory.management.commands.reconciliation.debug import DebugTarget
from directory.management.commands.reconciliation.reinitTarget import ReinitTarget


logger = logging.getLogger(__name__)


class Reconciliation():
    def __init__(self):
        self.upTarget = UpgradeTarget()
        self.upBT = UpgradeBT()
        self.debugTarget = DebugTarget()
        self.reinitTarget = ReinitTarget()

    def upgradeTarget(self):
        self.upTarget.start()

    def upgrade(self):
        self.upBT.start()

    def debug(self):
        self.debugTarget.start()

    def erase(self):
        self.reinitTarget.start()


class Command(BaseCommand):
    def handle(self, *args, **options):
        print "Begin:"
        reconciliation = Reconciliation()
        if 'debug' in args:
            reconciliation.debug()
        elif 'erase' in args:
            reconciliation.erase()
        else:
            reconciliation.upgradeTarget()
            print ""
            reconciliation.upgrade()
        print "End."
