# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm, ModelChoiceField
from directory.models import *
from django.forms.util import ErrorList

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
        exclude = ( 'lbeObjectTemplate' )

class LBEScriptForm(ModelForm):
    class Meta:
        model = LBEScript
        
class LBEObjectInstanceForm(forms.Form):
    def __init__(self, lbeObjectTemplate, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        for attributeInstance in lbeObjectTemplate.lbeattributeinstance_set.all():
            # Display only finals attributes
            if attributeInstance.attributeType == ATTRIBUTE_TYPE_FINAL:
                # TODO: Find a better way than exec
                exec 'self.fields[attributeInstance.lbeAttribute.name] = ' + attributeInstance.widget + '(' + attributeInstance.widgetArgs + ')'
                try:
                    self.fields[attributeInstance.lbeAttribute.name].label = attributeInstance.lbeAttribute.displayName
                    self.fields[attributeInstance.lbeAttribute.name].required = bool(attributeInstance.mandatory)
                except BaseException, e:
                    pass

class LBEObjectInstanceAttributeForm(forms.Form):
    name = forms.CharField()
    values = forms.MultiValueField()

class LBEAttributeForm(ModelForm):
    class Meta:
        model = LBEAttribute
        
class LBEAttributeSingle(forms.Form):
	def __init__(self,lbeAttribute,defaultValue,event, js, *args, **kwargs):
		super(forms.Form, self).__init__(*args, **kwargs)
		# Display only finals attributes
		if lbeAttribute.attributeType == ATTRIBUTE_TYPE_FINAL:
			# TODO: Find a better way than exec
			exec 'self.fields[lbeAttribute.lbeAttribute.name] = ' + lbeAttribute.widget + '(' + lbeAttribute.widgetArgs +')'
			# default Value:
			self.fields[lbeAttribute.lbeAttribute.name].initial= defaultValue
			# add special attribute tag for js: [AJAX]
			self.fields[lbeAttribute.lbeAttribute.name].widget.attrs[event]= js
			try:
				self.fields[lbeAttribute.lbeAttribute.name].label = lbeAttribute.lbeAttribute.displayName
				self.fields[lbeAttribute.lbeAttribute.name].required = bool(lbeAttribute.mandatory)
			except BaseException, e:
				pass

