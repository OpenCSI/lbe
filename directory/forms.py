from django import forms
from django.forms import ModelForm, ModelChoiceField
from directory.models import *
from django.forms.util import ErrorList

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
		exclude = ( 'attributes', 'objectClasses', 'version' )
	# Implements validator for approval field (must >= 0)
	def clean_approval(self):
		approval = self.cleaned_data['approval']
		if (approval < 0):
			raise forms.ValidationError("This field must be null or positive.")
		return approval

class LBEAttributeInstanceForm(ModelForm):
	lbeAttribute = LBEAttributeChoiceField(queryset = LBEAttribute.objects.all())
	lbeObject = LBEObjectChoiceField(queryset = LBEObject.objects.all())
	class Meta:
		model = LBEAttributeInstance
		exclude = ( 'lbeObject' )

class LBEScriptForm(ModelForm):
	class Meta:
		model = LBEScript
		
# Following forms are not used at the moment
class LBEObjectInstanceForm(forms.Form):
	displayName = forms.CharField()
	attributes = forms.MultiValueField()

class LBEObjectInstanceAttributeForm(forms.Form):
	name = forms.CharField()
	values = forms.MultiValueField()

