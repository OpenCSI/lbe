# -*- coding: utf-8 -*-
#from directory.models import LBEObjectTemplate, LBEObjectInstance
from django import forms

from directory.forms import LBEObjectInstanceForm


#
# This file is an example of script called after object creation
#

# TODO: Probably use a better suffix than PostConfig
class BASEPostConfig(LBEObjectInstanceForm):
    # BEGINNING OF REQUIRED SECTION ----------------------------------------------
    def __init__(self, lbeObjectTemplate, lbeObjectInstance=None, *args, **kwargs):
        self.template = lbeObjectTemplate
        self.instance = lbeObjectInstance
        super(BASEPostConfig, self).__init__(self.template, *args, **kwargs)

        # END OF REQUIRED SECTION ----------------------------------------------------

    # These methods are used only for LDAP target. Must be class methods
    # instanceNameAttribute will be used as RDN attribute
    @classmethod
    def base_dn(cls):
        return 'ou=BASE,ou=People,dc=opencsi,dc=com'

    # Note this method must return a list
    @classmethod
    def object_classes(cls):
        return ['top', 'person', 'organizationalPerson', 'inetOrgPerson']

        # END OF REQUIRED SECTION ----------------------------------------------------

    # Validators methods are used to alter, verify, compute the values of an attribute
    # IMPORTANT: Remembers all attributes are store in a list, even mono valued. Therefore, you must return a list

    # Prototype:
    # def clean_<attributeName>(self): (NOT the displayName) for FINAL attributes [django form template]
    # def compute_<attributeName>(self): (NOT the displayName) for VIRTUAL attributes

    def clean_givenName(self):
        try:
            # Multi value:
            tab = []
            i = 0
            for value in self.cleaned_data['givenName'].split('\0'):
                if not value == "":
                    tab.append(value.capitalize())
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
