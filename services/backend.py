from dao.MongoDao imports MongoService

class BackendDaoMongo:
	def __init__(self):
		self.handler = MongoService()

class BackendObject():
	pass