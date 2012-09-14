# -*- coding: utf-8 -*-
import logging
import directory

# TODO
# more info about logging classes : http://docs.python.org/dev/library/logging.handlers.html
# code: http://fossies.org/dox/Python-3.2.3/dir_b7b2ef979433e3b4acfa31016e12ce11.html
class log(logging.StreamHandler):
	
	"""
		Function to save execute queries into DB.
		record : logging.LogRecord <class>
	"""
	def emit(self,record):
		print record.name
		print record.levelname
		print record.getMessage()
		#log(type=record.name, level=record.levelname, message=record.getMessage()).save()

	"""
	def flush(self):
		loggin.StreamHandler.flush()
	"""
