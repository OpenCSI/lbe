class ScriptFile:
	def __init__(self,filename,f):
		self.name = filename
		self.f = f
		
	# save scripf file:
	def save(self):
		try:
			with open(str(self.name),'wb+') as dest:
				for chunk in self.f.chunks():
					dest.write(chunk)
				dest.close()
			return True
		except BaseException as e:
			print e
			return False

	# test script file:
	def test(self,arg):
		#try:
			tab = self.f.name.split('/')
			exec 'from '+ tab[0]+' import ' + tab[1][:-3]
			exec 'T = ' + F.file+'.'+F.file+'()'
			return ''
		#except BaseException as e:
		#	return e
