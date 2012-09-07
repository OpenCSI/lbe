# -*- coding: utf-8 -*-
from django.db import models
from django.forms import ModelForm, ModelChoiceField
from django import forms

class LBEAttribute(models.Model):
	displayName       = models.CharField(unique = True, max_length=64)
	name         	  = models.CharField(unique = True, max_length=64)
	# some fields (like syntax, max size) will be added later
	def __unicode__(self):
		return str(self.displayName + ":" + self.name)

class LBEObjectClass(models.Model):
	name        	  = models.CharField(unique = True, max_length=64)
	def __unicode__(self):
		return str(self.name)

class LBEScript(models.Model):
	name      = models.CharField(max_length=64)
	file      = models.FileField(upload_to='script')
	# Probablement à supprimer, juste avoir une référence vers le nom du fichier
	#value     = models.CharField(max_length=64)
	#tab       = models.CharField(max_length=64)
	def __unicode__(self):
		return str(self.name)
	
class LBEObject(models.Model):
	displayName  	  = models.CharField(unique = True, max_length=32)
	name         	  = models.CharField(unique = True, max_length=32)
	baseDN       	  = models.CharField(max_length=256)
	rdnAttribute  	  = models.ForeignKey(LBEAttribute, related_name = 'rdnattribute')
	approval		  = models.SmallIntegerField() # If > 0, this object need approvals
	attributes        = models.ManyToManyField(LBEAttribute, through = 'LBEAttributeInstance',null = True, default = None)
	objectClasses     = models.ManyToManyField(LBEObjectClass, null = True, default = None)
	# get attribut class:
	def __unicode__(self):
		return str(self.displayName)

class LBEReference(models.Model):
	name              = models.CharField(max_length=24)
	LBEObject         = models.ForeignKey(LBEObject,null = True)
	value             = models.CharField(max_length=32) # LDAP attribute

class LBEAttributeInstance(models.Model):
	lbeAttribute      = models.ForeignKey(LBEAttribute)
	lbeObject         = models.ForeignKey(LBEObject)
	defaultValue      = models.CharField(max_length=64, default='', blank = True, null = True)
	mandatory         = models.BooleanField(default = 0)
	multivalue        = models.BooleanField(default = 0)
	reference         = models.ForeignKey(LBEReference, null = True, blank = True, default = None)
	script         	  = models.ForeignKey(LBEScript, null = True, blank = True, default = None)
	# If true, this attribute will be stored crypted (by a key defined in LBE/settings.py)
	crypt		      = models.BooleanField(default = 0)

class LBEDirectoryACL(models.Model):
	object = models.CharField(max_length=25) # Why it's not a foreign key?
	type = models.CharField(max_length=10) # TO DOCUMENT
	attribut = models.CharField(max_length=35) # Why it's not a foreign key?
	condition = models.CharField(max_length=100)

class LBEAttributeChoiceField(ModelChoiceField):
	def label_from_instance(self, obj):
		return obj.name

class LBEObjectChoiceField(ModelChoiceField):
	def label_from_instance(self, obj):
		return obj.name

class LBEObjectForm(ModelForm):
	rdnAttribute =  LBEAttributeChoiceField(queryset = LBEAttribute.objects.all())
	class Meta:
		model = LBEObject
		exclude = ( 'attributes', 'objectClasses' )

class LBEAttributeInstanceForm(ModelForm):
	lbeAttribute = LBEAttributeChoiceField(queryset = LBEAttribute.objects.all())
	lbeObject = LBEObjectChoiceField(queryset = LBEObject.objects.all())
	class Meta:
		model = LBEAttributeInstance

class LBEScriptForm(ModelForm):
	class Meta:
		model = LBEScript
