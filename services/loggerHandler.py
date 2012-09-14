# -*- coding: utf-8 -*-
import logging
import directory

# Signal: https://docs.djangoproject.com/en/dev/topics/signals/ (#connecting-to-signals-sent-by-specific-senders)
# different signal send by Django: https://docs.djangoproject.com/en/dev/ref/signals/
# TODO
# more info about logging classes : http://docs.python.org/dev/library/logging.handlers.html
# code: http://fossies.org/dox/Python-3.2.3/dir_b7b2ef979433e3b4acfa31016e12ce11.html
class logDB(logging.StreamHandler):
	
	"""
		Function to save execute queries into DB.
		record : logging.LogRecord <class>
	"""
	def emit(self,record):
		print record.name
		print record.levelname
		print record.getMessage()
		#directory.models.log(type=record.name, level=record.levelname, message=record.getMessage()).save()

	"""
	def flush(self):
		loggin.StreamHandler.flush()
	"""

class logRequest(logging.StreamHandler):
	
	"""
		Function to save execute queries into DB.
		record : logging.LogRecord <class>
	"""
	def emit(self,record):
		directory.models.log(type=record.name, level=record.levelname, message=record.getMessage()).save()

	"""
	def flush(self):
		loggin.StreamHandler.flush()
	"""
