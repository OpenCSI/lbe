# -*- coding: utf-8 -*-
import re
from django.db.models import Q
from services.backend import BackendHelper
from directory.models import LBEObjectTemplate, LBEDirectoryACL

class ACLHelper:
	def __init__(self,LBEObjectTemplate,query=""):
		self.backend = BackendHelper
		self.lbeObjectTemplate = LBEObjectTemplate
		self.query=query+ " "
		self.word = []
		self.attribute = ""
		self.operator = ""
		self.numberFrom = self.numberTo = self.number = None # default value
		self.object = None
		self.objectName = ""
		self.traceback = ""
		
	def setQuery(self,query):
		self.query = query + " "
		
	def log(self):
		return self.traceback
	
	"""
		Fonction enables to check if the syntax is correct.
		The query begins by : select from.
		after, it depends on the query:
		-FROM [obect((,object)+)], example: select from RH,secretary [1]
		-object(<type>)=[username((,username)+)], example: select from <object>(<type>)=cjoron,bbonfils [2]
		-Error : [-1]
	"""
	def check(self):
		res = -1
		# Split the query:
		self.word = self.query.split(' ')
		# Check if the two world are 'select' and 'from':
		if self.word[0].lower() == "select":
			if self.word[1].lower() == 'from':
				self.objectName = re.match("^[a-zA-Z]+\(",self.word[2].lower())
				if self.objectName:
					self.objectName = self.objectName.group()[:-1]
					# check if the Object exists:
					if not self.__checkObjectName():
						self.traceback  = "The object '"+ self.objectName + "' does not exist."
						return -1
					res = self.__checkPerson()
				else:
					res = self.__checkOU()
			else:
				self.traceback = "-The second word must be 'from'"
		else:
			self.traceback = "-The first word must be 'select'"
		return res
	
	def __checkObjectName(self):
		try:
			obj = LBEObjectTemplate.objects.filter(Q(name=self.objectName) | Q(displayName=self.objectName) )
			self.object = obj[0]
			return True
		except BaseException:
			return False
	"""
		-FROM [LBEObject((,LBEObject)+)], example: select from RH,secretary
	"""
	def __checkOU(self): 
		if self.word[2] != '' and len(self.word[2].split(',')) > 0:
			# test the object LBE Name:
			try:
				for V in self.word[2].split(','):
					self.object = LBEObjectTemplate.objects.filter(Q(name=V) | Q(displayName=V) )[0]
			except BaseException:
				self.traceback = "The Object " + V + " does not exist."
				return -1
			return 1
		else:
			self.traceback += "You need word(s) after 'from', such as RH,secretary, (Object LBE Name or displayName)..."
			return -1
	
	def __checkPerson(self):
		# check (and get) the attribute into the ():
		attr = re.match(r".+[(]\D+[)].+$",self.word[2])
		if attr:
			# get attribute:
			attrValue = self.word[2].split('(')
			# check now the operator and values:
			attr = re.match(r"(.+)[)](!=|>=|<=){?[a-zA-Z0-9](.*)",attrValue[1])
			if attr:
				attrValue = attrValue[1].split(attr.group(2))
			else:
				attr = re.match(r"(.+)[)](=|>|<){?[a-zA-Z0-9](.*)",attrValue[1])
				if attr:
					attrValue = attrValue[1].split(attr.group(2))
				else:
					self.traceback += 'You need an operator like =, !=, <, <=, >=, > with value(s) after person(...)'
					return -1
			# checking for the >,>=,<,<= operators:
			if self.__checkOperator(attr.group(2),attrValue[1]):
				self.attribute =  attrValue[0][:-1]
				# get values:
				val = self.word[2].split(attr.group(2))
				self.word.append(val[1])
				return 3
			else:
				self.traceback += "You need to have numeric or specific format after >,>=,<,<=,=,!= operators."
				return -1
		else:
			self.traceback += "You need to specify after 'person' an attribute into () with an operator. Example person(uid)=<values>. (=,<,<=,>,>=,!=)"
			return -1
	
	def __checkOperator(self,op,values):
		if op == '>' or op == '<' or op == '<=' or op == '>=':
			number = re.match(r'^\d+$',values)
			if number:
				self.operator = op
				self.number = int(number.group())
				return True
			else:
				return False
		elif op == '=' or op == '!=':
			number = re.match(r'^{[0-9]+\.\.[0-9]+}$',values)
			if number:
				self.operator = op
				# get values:
				val =  number.group().split('..')
				if int(val[0][1:]) > int(val[1][:-1]):
					self.numberFrom = int(val[0][1:])
					self.numberTo = int(val[1][:-1])
				else:
					self.numberTo = int(val[0][1:])
					self.numberFrom = int(val[1][:-1])
				return True
			else:
				chars = re.match(r'^(\D\d?)+$',values) # characters (with integers or not) for the '=' operator
				if chars:
					self.operator = op
					self.word.insert(3,chars.group())
					return True
				else:
					number = re.match(r'(\d,?)+$',values) # integer value for the '=' operator
					if number:
						self.operator = op
						self.number = (number.group())
						return True
			self.operator = ""
			return False # Wrong syntax
			
	""" Return True if the user is conform to the query else False """
	""" user refers to the current user name [connected]"""
	def execute(self,userID):
		# syntax:
		state = self.check()
		if state == 1: # OU
			# [split the word[2] from the ',' car and execute it]
			return self.__executeOU(userID)
		elif state == 2: # objectClass [DEPRECIATE]
			return True
		elif state == 3: # Person
			# [ split the word[3] from the ',' car or depending if the values are numbers and execute it]
			return self.__executePerson(userID)
		return False # default
		
	def __executeOU(self,userID):
		# backend db:
		backend = BackendHelper()
		values = self.word[2].split(',')
		for objectName in values:
			self.object = LBEObjectTemplate.objects.filter(Q(name=objectName) | Q(displayName=objectName) )[0]
			if backend.getObjectByName(self.object,userID):
				return True
		# No value:
		return False
	
	# user: user class
	def __executePerson(self,userID):
		# backend db:
		backend = BackendHelper()
		obj = backend.getObjectByName(self.object,userID)
		# check if characters:
		if self.word[3] != '':
			# split ',' values:
			val = self.word[3].split(',')
			try:
				for value in obj['attributes'][self.attribute]:
					for attrValue in val:
						if self.operator == '=':
							if attrValue == value:
								return True
						elif self.operator == '!=':
							if attrValue == value:
								return False
			except BaseException as e:
				print e
				# attribute does not exist for user:
				pass
			return self.operator == '!='
		# only a number:
		elif self.number:
			try:
				if self.operator == '=':
					number = self.number.split(',')
					for nb in number:
						if int(nb) == int(obj['attributes'][self.attribute][0]):
							return True
					return False
				elif self.operator == '!=':
					number = self.number.split(',')
					for nb in number:
						if int(nb) == int(obj['attributes'][self.attribute][0]):
							return False
					return True
				elif self.operator == '>':
					return int(obj['attributes'][self.attribute][0]) > self.number
				elif self.operator == '<':
					return int(obj['attributes'][self.attribute][0]) < self.number
				elif self.operator == '<=':
					return int(obj['attributes'][self.attribute][0]) <= self.number
				elif self.operator == '>=':
					return int(obj['attributes'][self.attribute][0]) >= self.number
			except:
				# wrong key
				self.traceback = "The key " + self.attribute + "does not exist to the Backend Server for " + userUID + "."
				return False
		# number range:
		elif self.numberTo and self.numberFrom:
			try:
				if self.operator == '=':
					return self.numberTo <= int(obj['attributes'][self.attribute][0]) and \
					self.numberFrom >= int(obj['attributes'][self.attribute][0])
				elif self.operator == '!=':
					return self.numberTo <= int(obj['attributes'][self.attribute][0]) and \
					self.numberFrom >= int(obj['attributes'][self.attribute][0])
			except:
				# wrong key
				self.traceback = "The key " + self.attribute + "does not exist to the Backend Server for " + userUID + "."
				return False
		# not necessary:
		return False

	# remove T from attributes function 'apply_acl' use them from kwargs attribute?
	# How to use this function:
	#@ACLHelper.apply_acl("create")
	#def Myview(request,obj_id,(type_acl)?,...): # with type_acl : create/read/update/...
	#	...
	@staticmethod
	def apply_acl(T=None):
		# function:
		def decorate(func):
			# function's arguments
			def wrapper(*args,**kwargs):
				try:
					lbeOT = LBEObjectTemplate.objects.get(id=kwargs['obj_id'])
					if T != None:
						lbeacls = LBEDirectoryACL.objects.filter(lbeObjectTemplate=lbeOT,type=T)
					else:
						lbeacls = LBEDirectoryACL.objects.filter(lbeObjectTemplate=lbeOT,type=kwargs['type_acl'])
				except BaseException:
					raise Http404
				for lbeacl in lbeacls:
					acl = ACLHelper(lbeOT,lbeacl.query)
					# execute the function if correct (test)
					if acl.execute("userID[_id from backend]"):
						response = func(*args,**kwargs)
						return response
				return HttpResponse(status=403)
			return wrapper
		return decorate
