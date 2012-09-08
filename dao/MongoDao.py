from pymongo import Connection, errors
from django.conf import settings

class MongoService:
	def __init__(self):
		try:
			self.handler = Connection(settings.MONGODB_SERVER['HOST'], settings.MONGODB_SERVER['PORT'])[settings.MONGODB_SERVER['DATABASE']]
		except:
			pass
		
	def search(self):
		pass
	
	def create(self, document):
		pass