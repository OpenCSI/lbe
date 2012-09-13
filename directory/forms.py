from django import forms
from django.forms import ModelForm, ModelChoiceField
from directory.models import *
from django.forms.util import ErrorList

class LBEModelChoiceField(ModelChoiceField):
	def label_from_instance(self, obj):
		return obj.name

class LBEObjectTemplateForm(ModelForm):
	rdnAttribute =  forms.CharField(max_length=100)
	#rdnAttribute =  LBEAttributeChoiceField(queryset = LBEAttribute.objects.all())
	class Meta:
		model = LBEObjectTemplate
		exclude = ( 'attributes', 'objectClasses', 'version' )
	# Implements validator for approval field (must >= 0)
	def clean_approval(self):
		approval = self.cleaned_data['approval']
		if (approval < 0):
			raise forms.ValidationError("This field must be null or positive.")
		return approval
	# Validator and replace value to his reference class value:
	def clean_rdnAttribute(self):
		value = self.cleaned_data['rdnAttribute']
		try:
			rdnAttribute = LBEAttribute.objects.get(name__iexact=value)
		except BaseException:
			raise forms.ValidationError("This field must be a valid attribute.")
		return rdnAttribute

class LBEAttributeInstanceForm(ModelForm):
	lbeAttribute = LBEModelChoiceField(queryset = LBEAttribute.objects.all())
	class Meta:
		model = LBEAttributeInstance
		exclude = ( 'lbeObjectTemplate' )

class LBEScriptForm(ModelForm):
	class Meta:
		model = LBEScript
		
# Following forms are not used at the moment
class LBEObjectInstanceForm(forms.Form):
	def __init__(self, lbeObjectTemplate, *args, **kwargs):
		super(forms.Form, self).__init__(*args, **kwargs)
		for attributeInstance in lbeObjectTemplate.lbeattributeinstance_set.all():
			# TODO: There is probably a better way than exec
			exec 'self.fields[attributeInstance.lbeAttribute.displayName] = ' + attributeInstance.widget + '(' + attributeInstance.widgetArgs + ')'
			try:
				print bool(attributeInstance.mandatory)
				self.fields[attributeInstance.lbeAttribute.displayName].required = bool(attributeInstance.mandatory)
			except BaseException as e:
				print e
	
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
