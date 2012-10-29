# -*- coding: utf-8 -*-
from django.db import models
from django import forms
import datetime
from django.utils.timezone import utc
# Object status
OBJECT_STATE_INVALID = -256
OBJECT_STATE_SYNC_ERROR = -1
OBJECT_STATE_SYNCED = 0
OBJECT_STATE_AWAITING_SYNC = 1
OBJECT_STATE_AWAITING_APPROVAL = 2
OBJECT_STATE_IMPORTED = 0

OBJECT_CHANGE_CREATE_OBJECT = 0
OBJECT_CHANGE_UPDATE_OBJECT = 1
OBJECT_CHANGE_DELETE_OBJECT = 2
OBJECT_CHANGE_CREATE_ATTR   = 3
OBJECT_CHANGE_UPDATE_ATTR   = 4
OBJECT_CHANGE_DELETE_ATTR   = 5

ATTRIBUTE_TYPE_FINAL = 0
ATTRIBUTE_TYPE_VIRTUAL = 1
ATTRIBUTE_TYPE_REFERENCE = 2

class LBEAttribute(models.Model):
    displayName       = models.CharField(unique = True, max_length=64)
    name               = models.CharField(unique = True, max_length=64)
    # some fields (like syntax, max size) will be added later
    def __unicode__(self):
        return str(self.displayName + ":" + self.name)

class LBEScript(models.Model):
    name      = models.CharField(max_length=64)
    file      = models.FileField(upload_to='script')
    # TODO: Probablement à supprimer, juste avoir une référence vers le nom du fichier
    #value     = models.CharField(max_length=64)
    #tab       = models.CharField(max_length=64)
    def __unicode__(self):
        return str(self.name)

# Use lbeobject.lbeattributeinstance_set.all() to get all attributes instance for a LBEObject
class LBEObjectTemplate(models.Model):
    name               = models.CharField(unique = True, max_length=32)
    displayName        = models.CharField(unique = True, max_length=32)
    # Used as name for an objectInstance
    instanceNameAttribute   = models.ForeignKey(LBEAttribute, related_name = 'instance_name_attribute')
    # Used as displayName for an objectInstance
    instanceDisplayNameAttribute   = models.ForeignKey(LBEAttribute, related_name = 'instance_displayname_attribute')
     # If > 0, this object need approvals. Must be positive
    approval          = models.SmallIntegerField(default = 0)
    # To increment each time an object is changed
    version           = models.SmallIntegerField(default = 0)
    # Every template must be associated to a class provided by the administrator
    script               = models.ForeignKey(LBEScript, null = True, blank = True, default = None)
    # Date of last import. Used to detect new objects in target by searching on createTimestamp (for LDAP) > last import
    imported_at     = models.DateTimeField(default=datetime.datetime.fromtimestamp(0, utc))
    # Date of last sync
    synced_at       = models.DateTimeField(default=datetime.datetime.fromtimestamp(0, utc))
    def __unicode__(self):
        return str(self.displayName)

class LBEReference(models.Model):
    name              = models.CharField(max_length=24)

class LBEAttributeInstance(models.Model):
    lbeAttribute      = models.ForeignKey(LBEAttribute)
    lbeObjectTemplate = models.ForeignKey(LBEObjectTemplate)
    defaultValue      = models.CharField(max_length=64, default='', blank = True, null = True)
    mandatory         = models.BooleanField(default = False)
    multivalue        = models.BooleanField(default = True)
    reference         = models.ForeignKey(LBEReference, null = True, blank = True, default = None)
    # If true, this attribute will be stored enciphered (by a symmetric key defined in LBE/settings.py) TODO: implement
    secure              = models.BooleanField(default = False)
    attributeType        = models.SmallIntegerField(default = ATTRIBUTE_TYPE_FINAL)
    # The HTML widget used to display/edit attribute. We'll inject classname
    widget            = models.CharField(max_length=64, default = 'forms.CharField', blank = True)
    widgetArgs        = models.CharField(max_length=255, default = 'None')

class LBEDirectoryACL(models.Model):
    object = models.CharField(max_length=25) # TODO: Why it's not a foreign key?
    type = models.CharField(max_length=10) # TODO: DOCUMENT probably use constants
    attribute = models.CharField(max_length=35) # TODO: Why it's not a foreign key?
    condition = models.CharField(max_length=100)

# Fake model class, doesn't exists in the database. Used for abstraction
class LBEObjectInstance: 
    def __init__(self, lbeObjectTemplate, *args, **kwargs):
        # List of fields (useful for completion too)
        self.template = lbeObjectTemplate
        self.attributes = {}
        self.status = OBJECT_STATE_INVALID
        now = datetime.datetime.now(utc)
        self.created_at = now
        self.updated_at = now
        self.synced_at = datetime.datetime.fromtimestamp(0, utc)
        # TODO: document usage  of changes
        self.changes = {
            'type': -1,
            'set': { },
        }
        self.name = None
        self.displayName = None

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    # TODO: implement
    def is_valid(self,request):
		# import the class from module:
		#ex: (current) custom.employee.EmployeePostConfig by EmployeePostConfig.
        mod = __import__(str(self.template.script.file),fromlist=[ self.template.script.name.split('.')[2] ])# 2-> 0: dir; 1: file; 2: class
        # get the class type:
        cl = getattr(mod,self.template.script.name.split('.')[2])
        # instance the class:
        instance = cl(self.template)
        # execute the is_valid() method:
        return instance.is_valid(request)
    
    def search(self, filter):
        pass
        
    def save(self):
        pass
    
    def __unicode__(self):
        return 'name: ' + self.name + ', displayName: ' + self.displayName + ', attributes: ' + self.attributes
