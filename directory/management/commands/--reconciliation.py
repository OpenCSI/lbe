# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import logging

from directory.management.commands.reconciliation.upgradeTarget import UpgradeTarget
from directory.management.commands.reconciliation.upgradeBT import UpgradeBT
from directory.management.commands.reconciliation.debug import DebugTarget

logger = logging.getLogger(__name__)

class Reconciliation():
    def __init__(self):
        self.upTarget = UpgradeTarget()
        self.upBT = UpgradeBT()
        self.debugTarget = DebugTarget()
     		
    def upgradeTarget(self):
        self.upTarget.start()
        
    def upgrade(self):
		self.upBT.start()
		
    def debug(self):
		self.debugTarget.start()
	
		
class Command(BaseCommand):
	def handle(self, *args, **options):
		print "Begin:"
		reconciliation = Reconciliation()
		if 'debug' in args:
			reconciliation.debug()
		else:
			reconciliation.upgradeTarget()
			print ""
			reconciliation.upgrade()
		print "End."
