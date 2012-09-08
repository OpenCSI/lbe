from pymongo import Connection, errors
from django.conf import settings

class MongoService:
	def __init__(self):
		self.handler = Connction.(settings.MONGODB_SERVER['HOST'], settings.MONGODB_SERVER['PORT'])[settings.MONGODB_SERVER['DATABASE']]
	
	def search(self):
		pass

