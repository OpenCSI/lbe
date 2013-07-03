# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm, ModelChoiceField
from directory.models import *
from services.backend import BackendHelper
from django.forms.util import ErrorList
import os, sys
from services.ACL import ACLHelper

# All this forms but ObjectInstanceForm should be in config/forms.py
class LBEModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class LBEObjectTemplateForm(ModelForm):
    instanceNameAttribute =  forms.CharField(max_length=100)
    class Meta:
        model = LBEObjectTemplate
        exclude = ( 'attributes', 'imported_at', 'synced_at' 'version' )
    # Implements validator for approval field (must >= 0)
    def clean_approval(self):
        approval = self.cleaned_data['approval']
        if approval < 0:
            raise forms.ValidationError("This field must be null or positive.")
        return approval

    # Validator and replace value to his reference class value:
    def clean_instanceNameAttribute(self):
        value = self.cleaned_data['instanceNameAttribute']
        try:
            instanceNameAttribute = LBEAttribute.objects.get(name__iexact=value)
        except BaseException:
            raise forms.ValidationError("This field must be a valid attribute.")
        return instanceNameAttribute

class LBEAttributeInstanceForm(ModelForm):
    lbeAttribute = LBEModelChoiceField(queryset = LBEAttribute.objects.all())
    class Meta:
        model = LBEAttributeInstance
        exclude = ('widget','widgetArgs')
        def clean_attributeType(self):
			if self.cleaned_data['attributeType'] < 0:
				raise forms.ValidationError("This field must be null or positive.")
			print self.cleaned_data
			#if self.cleaned_data['attributType'] 

class LBEScriptForm(ModelForm):
	class Meta:
		model = LBEScript
	# test if the name already exists:
	def clean_name(self):
		value = self.cleaned_data['name']
		exist = False
		try:
			if LBEScript.objects.filter(name__iexact='custom.'+value):
				exist = True
		except BaseException:
			pass
		if exist:
			raise forms.ValidationError("This name is already used, change it.")
		return 'custom.' + value
	# test if a filename already exists:
	def clean_file(self):
		value = self.cleaned_data['file']
		exist = False
		try:
			if LBEScript.objects.filter(file__iexact='custom.'+value):
				exist = True
		except BaseException:
			pass
		if exist:
			raise forms.ValidationError("The file already exists, change its name and class name too.")
		return 'custom.'+value
	
	def clean_fileUpload(self):
		value = self.cleaned_data['fileUpload']
		# file already exists?:
		if os.path.exists("custom/" + str(value)):
			raise forms.ValidationError("The file already exists, change its name and class name too.")
		return value

class LBEScriptManageForm(forms.Form):
	script = LBEModelChoiceField(queryset = LBEScript.objects.all())
	test = forms.CharField(max_length=64)
	# script selected exists:
	def clean_script(self):
		value = self.cleaned_data['script']
		try:
			script = LBEScript.objects.get(name__iexact=value)
		except BaseException:
			raise forms.ValidationError("This field must be a valid script.")
		return script
		
# Following forms are not used at the moment
class LBEObjectInstanceForm(forms.Form):
    def __init__(self, lbeObjectTemplate, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        for attributeInstance in lbeObjectTemplate.lbeattributeinstance_set.all():
            # Display finals attributes
            if attributeInstance.attributeType == ATTRIBUTE_TYPE_FINAL:
                # TODO: Find a better way than exec
                exec 'self.fields[attributeInstance.lbeAttribute.name] = ' + attributeInstance.widget + '(' + attributeInstance.widgetArgs + ')'
                try:
                    self.fields[attributeInstance.lbeAttribute.name].label = attributeInstance.lbeAttribute.displayName
                    self.fields[attributeInstance.lbeAttribute.name].required = bool(attributeInstance.mandatory)
                except BaseException:
                    pass
            # Manage & Show references attributes
            elif attributeInstance.attributeType == ATTRIBUTE_TYPE_REFERENCE:
				backend = BackendHelper()
				values =  backend.searchObjects(attributeInstance.reference.objectTemplate)
				print values

class LBEObjectInstanceAttributeForm(forms.Form):
    name = forms.CharField()
    values = forms.MultiValueField()

class LBEAttributeForm(ModelForm):
	class Meta:
		model = LBEAttribute
		
class LBEReferenceForm(ModelForm):
	class Meta:
		model = LBEReference
	def clean_objectAttribute(self):
		try:
			objectAttribute = self.cleaned_data['objectAttribute']
			# test if attribut is in the object:
			LBEAttributeInstance.objects.get(lbeAttribute = objectAttribute,lbeObjectTemplate = self.cleaned_data['objectTemplate'])
		except BaseException:
			raise forms.ValidationError("This field must be an attribute own by the object.")
		return objectAttribute

class LBEReferenceSelectForm(forms.Form):
	reference = LBEModelChoiceField(queryset = LBEReference.objects.all())

class LBEACLForm(ModelForm):
	class Meta:
		model = LBEDirectoryACL
		exclude = ('attribut')
	def clean_condition(self):
		acl = ACLHelper(None,self.cleaned_data["condition"])
		if acl.check() == -1:
			raise forms.ValidationError(acl.traceback)
		return self.cleaned_data['condition']
