# -*- coding: utf-8 -*-
#from directory.models import LBEObjectTemplate, LBEObjectInstance
from django import forms
 
from directory.forms import LBEObjectInstanceForm
 
#from django.forms.formsets import formset_factory
 
#
# This file is an example of script called after object creation
#
 
# TODO: Probably use a better suffix than PostConfig
# use formset_factory
class EmployeePostConfig(LBEObjectInstanceForm):
    # BEGINNING OF REQUIRED SECTION ----------------------------------------------
    def __init__(self, lbeObjectTemplate, lbeObjectInstance=None, *args, **kwargs):
        self.template = lbeObjectTemplate
        self.instance = lbeObjectInstance
        super(EmployeePostConfig, self).__init__(self.template, *args, **kwargs)
 
        # END OF REQUIRED SECTION ----------------------------------------------------
 
    # REQUIRED SECTION FOR LDAP BACKEND ------------------------------------------    
 
    # These methods are used only for LDAP target. Must be class methods
    # instanceNameAttribute will be used as RDN attribute
    @classmethod
    def base_dn(cls):
        return 'ou=people,dc=opencsi,dc=com'
 
    # Note this method must return a list
    @classmethod
    def object_classes(cls):
        return ['top', 'person', 'organizationalPerson', 'inetOrgPerson']

    @classmethod
    def search_scope(cls):
        return 2
 
        # END OF REQUIRED SECTION ----------------------------------------------------
 
    # This method enables to ignore some attributes into reconciliation part
    @classmethod
    def ignore_attributes(cls):
        return ['title']
 
    # TODO: Think about implements is_valid method here to be called by LBEObjectInstanceForm if possible    
    # def is_valid():
 
    # Validators methods are used to alter, verify, compute the values of an attribute
    # IMPORTANT: Remembers all attributes are store in a list, even mono valued. Therefore, you must return a list
 
    # Prototype:
    # def clean_<attributeName>(self): (NOT the displayName) for FINAL attributes [django form template]
    # def compute_<attributeName>(self): (NOT the displayName) for VIRTUAL attributes
 
    def clean_givenName(self):
        try:
            # Mono value:
            return [self.cleaned_data['givenName'].capitalize()]
        except:
            raise forms.ValidationError("The field must be a valid attribute.")
 
    def clean_telephoneNumber(self):
        try:
            # Multi value:
            tab = []
            i = 0
            for value in self.cleaned_data['telephoneNumber'].split('\0'):
                if not value == "":
                    tab.append(value)
                i = i + 1
            return tab
        except:
            raise forms.ValidationError("The field #" + str(i) + " must be a valid attribute.")
 
    def clean_sn(self):
        try:
            # modify attribut object:
            # for multi-value: just create an list to set and return it.
            return [self.cleaned_data['sn'].capitalize()]
        except BaseException:
            raise forms.ValidationError("This field must be a valid attribute.")
 
    def compute_cn(self):
        return [self.instance.attributes['givenName'][0] + ' ' + self.instance.attributes['sn'][0]]
 
    def compute_uid(self):
        # TODO: Provide an example to use two letters of the givenName if the uid already exists in the backend
        return [
            (self.instance.attributes['givenName'][0][0] + self.instance.attributes['sn'][0].replace(' ', '')).lower()]
 
    def compute_mail(self):
        return [self.compute_uid()[0] + '@opencsi.com']
