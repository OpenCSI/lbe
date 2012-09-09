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
	# TODO: Probablement à supprimer, juste avoir une référence vers le nom du fichier
	#value     = models.CharField(max_length=64)
	#tab       = models.CharField(max_length=64)
	def __unicode__(self):
		return str(self.name)

# Use lbeobject.lbeattributeinstance_set.all() to get all attributes instance for a LBEObject
class LBEObject(models.Model):
	displayName  	  = models.CharField(unique = True, max_length=32)
	name         	  = models.CharField(unique = True, max_length=32)
	baseDN       	  = models.CharField(max_length=256)
	rdnAttribute  	  = models.ForeignKey(LBEAttribute, related_name = 'rdnattribute')
	approval		  = models.SmallIntegerField() # If > 0, this object need approvals. Must be positive
	objectClasses     = models.ManyToManyField(LBEObjectClass, null = True, default = None)
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
	object = models.CharField(max_length=25) # TODO: Why it's not a foreign key?
	type = models.CharField(max_length=10) # TODO: DOCUMENT probably use constants
	attribut = models.CharField(max_length=35) # TODO: Why it's not a foreign key?
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
	def clean_approval(self):
		approval = self.cleaned_data['approval']
		if (approval < 0):
			raise forms.ValidationError("This field must be positive")
		return approval

class LBEAttributeInstanceForm(ModelForm):
	lbeAttribute = LBEAttributeChoiceField(queryset = LBEAttribute.objects.all())
	lbeObject = LBEObjectChoiceField(queryset = LBEObject.objects.all())
	class Meta:
		model = LBEAttributeInstance

class LBEScriptForm(ModelForm):
	class Meta:
		model = LBEScript
		
# Fake model class, doesn't exists in the database. Used for abstraction
class LBEObjectInstance:
	def __init__(self, dn, name, attributes = {}):
		self.dn = dn
		self.object_type = name
		self.attributes = {}
		# Attributes will be stored a { cn: ['Bruno Bonfils'], mail: [ 'bruno@opencsi.com', 'bbonfils@opencsi.com' ] }

	def addAttribute(self, name, values):
		self.attributes[name] = values
			