# -*- coding: utf-8 -*-
from django.db import models

class language(models.Model):
	name = models.CharField(max_length=30)

class ACL(models.Model):
	object = models.CharField(max_length=25)
	type = models.CharField(max_length=10)
	attribut = models.CharField(max_length=35)
	condition = models.CharField(max_length=100)
	language = models.ForeignKey(language)

class LDAP(models.Model):
	hostname = models.CharField(max_length=50)
	user = models.CharField(max_length=30)
	pwd = models.CharField(max_length=30)
	port = models.IntegerField()
	base = models.CharField(max_length=30)
	
class MONGO(models.Model):
	hostname = models.CharField(max_length=50)
	port = models.IntegerField()
	db = models.CharField(max_length=30)
	
class Format(models.Model):
	name = models.CharField(max_length=64)
	value = models.CharField(max_length=128,null = True, default = None)
	file = models.CharField(max_length=32,null = True, default = None)

class messageError(models.Model):
	username = models.CharField(max_length=64)
	type = models.CharField(max_length=32)# ldap, mongo, crypto, template, ...
	message = models.CharField(max_length=1024)
	date = models.DateTimeField(auto_now=True)
