# -*- coding: utf-8 -*-
from django.db import models

# class language(models.Model):
# 	name = models.CharField(max_length=30)
# 
# class ACL(models.Model):
# 	object = models.CharField(max_length=25)
# 	type = models.CharField(max_length=10)
# 	attribut = models.CharField(max_length=35)
# 	condition = models.CharField(max_length=100)
# 	language = models.ForeignKey(language)
# 
# class messageError(models.Model):
# 	username = models.CharField(max_length=64)
# 	type = models.CharField(max_length=32)# ldap, mongo, crypto, template, ...
# 	message = models.CharField(max_length=1024)
# 	date = models.DateTimeField(auto_now=True)
