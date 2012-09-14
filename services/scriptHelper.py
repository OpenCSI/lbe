class ScriptFile:
	def __init__(self,filename,f):
		self.name = filename
		self.f = f

	# test script file:
	def execute(self,arg):
		tab = self.f.name.split('/')
		exec 'from '+ tab[0]+' import ' + tab[1][:-3]
		exec 'T = ' + tab[1][:-3]+'.'+tab[1][:-3]+'()'
		exec 'T.main("' +arg + '")' 
		return T.getValue()
