# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'LBEGroup.instanceNameAttribute'
        db.add_column(u'directory_lbegroup', 'instanceNameAttribute',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.LBEAttribute']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'LBEGroup.instanceNameAttribute'
        db.delete_column(u'directory_lbegroup', 'instanceNameAttribute_id')


    models = {
        u'directory.lbeattribute': {
            'Meta': {'object_name': 'LBEAttribute'},
            'displayName': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'directory.lbeattributeinstance': {
            'Meta': {'object_name': 'LBEAttributeInstance'},
            'attributeType': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'defaultValue': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lbeAttribute': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directory.LBEAttribute']"}),
            'lbeObjectTemplate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directory.LBEObjectTemplate']"}),
            'mandatory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'multivalue': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'reference': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['directory.LBEReference']", 'null': 'True', 'blank': 'True'}),
            'secure': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unique': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'widget': ('django.db.models.fields.CharField', [], {'default': "'forms.CharField'", 'max_length': '64'}),
            'widgetArgs': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'})
        },
        u'directory.lbedirectoryacl': {
            'Meta': {'object_name': 'LBEDirectoryACL'},
            'attribut': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['directory.LBEAttributeInstance']", 'null': 'True'}),
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directory.LBEObjectTemplate']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'select'", 'max_length': '10'})
        },
        u'directory.lbegroup': {
            'Meta': {'object_name': 'LBEGroup'},
            'approval': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'displayName': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)'}),
            'instanceNameAttribute': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directory.LBEAttribute']"}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'groups'", 'max_length': '10'}),
            'objectTemplate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directory.LBEObjectTemplate']"}),
            'reconciliation_object_different_policy': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'reconciliation_object_missing_policy': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'script': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['directory.LBEScript']"}),
            'synced_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)'}),
            'version': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        u'directory.lbeobjecttemplate': {
            'Meta': {'object_name': 'LBEObjectTemplate'},
            'approval': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'displayName': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)'}),
            'instanceDisplayNameAttribute': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'instance_displayname_attribute'", 'to': u"orm['directory.LBEAttribute']"}),
            'instanceNameAttribute': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'instance_name_attribute'", 'to': u"orm['directory.LBEAttribute']"}),
            'instanceNameBeforeAttribute': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'instance_name_before_attribute'", 'null': 'True', 'blank': 'True', 'to': u"orm['directory.LBEAttribute']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'needReconciliationRDN': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reconciliation_object_different_policy': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'reconciliation_object_missing_policy': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'script': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['directory.LBEScript']"}),
            'synced_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)'}),
            'version': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        u'directory.lbereference': {
            'Meta': {'object_name': 'LBEReference'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'objectAttribute': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directory.LBEAttribute']"}),
            'objectTemplate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directory.LBEObjectTemplate']"})
        },
        u'directory.lbescript': {
            'Meta': {'object_name': 'LBEScript'},
            'file': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'fileUpload': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'directory.log': {
            'Meta': {'object_name': 'log'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['directory']