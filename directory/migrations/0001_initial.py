# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Adding model 'LBEAttribute'
        db.create_table(u'directory_lbeattribute', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('displayName', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
        ))
        db.send_create_signal(u'directory', ['LBEAttribute'])

        # Adding model 'LBEScript'
        db.create_table(u'directory_lbescript', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('file', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('fileUpload', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'directory', ['LBEScript'])

        # Adding model 'LBEObjectTemplate'
        db.create_table(u'directory_lbeobjecttemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('displayName', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('instanceNameBeforeAttribute', self.gf('django.db.models.fields.related.ForeignKey')(default=None,
                                                                                                  related_name='instance_name_before_attribute',
                                                                                                  null=True, blank=True,
                                                                                                  to=orm[
                                                                                                      'directory.LBEAttribute'])),
            ('instanceNameAttribute',
             self.gf('django.db.models.fields.related.ForeignKey')(related_name='instance_name_attribute',
                                                                   to=orm['directory.LBEAttribute'])),
            ('instanceDisplayNameAttribute',
             self.gf('django.db.models.fields.related.ForeignKey')(related_name='instance_displayname_attribute',
                                                                   to=orm['directory.LBEAttribute'])),
            ('approval', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('version', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('script', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['directory.LBEScript'])),
            ('imported_at',
             self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(1970, 1, 1, 0, 0))),
            (
            'synced_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(1970, 1, 1, 0, 0))),
            ('needReconciliationRDN', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reconciliation_object_missing_policy', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('reconciliation_object_different_policy', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'directory', ['LBEObjectTemplate'])

        # Adding model 'LBEReference'
        db.create_table(u'directory_lbereference', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=24)),
            ('objectTemplate',
             self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.LBEObjectTemplate'])),
            (
            'objectAttribute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.LBEAttribute'])),
        ))
        db.send_create_signal(u'directory', ['LBEReference'])

        # Adding model 'LBEAttributeInstance'
        db.create_table(u'directory_lbeattributeinstance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lbeAttribute', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.LBEAttribute'])),
            ('lbeObjectTemplate',
             self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.LBEObjectTemplate'])),
            ('defaultValue',
             self.gf('django.db.models.fields.CharField')(default='', max_length=64, null=True, blank=True)),
            ('mandatory', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('multivalue', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('reference',
             self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['directory.LBEReference'],
                                                                   null=True, blank=True)),
            ('secure', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('unique', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('attributeType', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('widget', self.gf('django.db.models.fields.CharField')(default='forms.CharField', max_length=64)),
            ('widgetArgs', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
        ))
        db.send_create_signal(u'directory', ['LBEAttributeInstance'])

        # Adding model 'LBEDirectoryACL'
        db.create_table(u'directory_lbedirectoryacl', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.LBEObjectTemplate'])),
            ('type', self.gf('django.db.models.fields.CharField')(default='select', max_length=10)),
            ('attribut', self.gf('django.db.models.fields.related.ForeignKey')(default=None,
                                                                               to=orm['directory.LBEAttributeInstance'],
                                                                               null=True)),
            ('condition', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'directory', ['LBEDirectoryACL'])

        # Adding model 'log'
        db.create_table(u'directory_log', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('level', self.gf('django.db.models.fields.CharField')(max_length=24)),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'directory', ['log'])


    def backwards(self, orm):
        # Deleting model 'LBEAttribute'
        db.delete_table(u'directory_lbeattribute')

        # Deleting model 'LBEScript'
        db.delete_table(u'directory_lbescript')

        # Deleting model 'LBEObjectTemplate'
        db.delete_table(u'directory_lbeobjecttemplate')

        # Deleting model 'LBEReference'
        db.delete_table(u'directory_lbereference')

        # Deleting model 'LBEAttributeInstance'
        db.delete_table(u'directory_lbeattributeinstance')

        # Deleting model 'LBEDirectoryACL'
        db.delete_table(u'directory_lbedirectoryacl')

        # Deleting model 'log'
        db.delete_table(u'directory_log')


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
            'defaultValue': ('django.db.models.fields.CharField', [],
                             {'default': "''", 'max_length': '64', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lbeAttribute': (
            'django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directory.LBEAttribute']"}),
            'lbeObjectTemplate': (
            'django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directory.LBEObjectTemplate']"}),
            'mandatory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'multivalue': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'reference': ('django.db.models.fields.related.ForeignKey', [],
                          {'default': 'None', 'to': u"orm['directory.LBEReference']", 'null': 'True', 'blank': 'True'}),
            'secure': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unique': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'widget': ('django.db.models.fields.CharField', [], {'default': "'forms.CharField'", 'max_length': '64'}),
            'widgetArgs': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'})
        },
        u'directory.lbedirectoryacl': {
            'Meta': {'object_name': 'LBEDirectoryACL'},
            'attribut': ('django.db.models.fields.related.ForeignKey', [],
                         {'default': 'None', 'to': u"orm['directory.LBEAttributeInstance']", 'null': 'True'}),
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directory.LBEObjectTemplate']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'select'", 'max_length': '10'})
        },
        u'directory.lbeobjecttemplate': {
            'Meta': {'object_name': 'LBEObjectTemplate'},
            'approval': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'displayName': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imported_at': (
            'django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)'}),
            'instanceDisplayNameAttribute': ('django.db.models.fields.related.ForeignKey', [],
                                             {'related_name': "'instance_displayname_attribute'",
                                              'to': u"orm['directory.LBEAttribute']"}),
            'instanceNameAttribute': ('django.db.models.fields.related.ForeignKey', [],
                                      {'related_name': "'instance_name_attribute'",
                                       'to': u"orm['directory.LBEAttribute']"}),
            'instanceNameBeforeAttribute': ('django.db.models.fields.related.ForeignKey', [],
                                            {'default': 'None', 'related_name': "'instance_name_before_attribute'",
                                             'null': 'True', 'blank': 'True', 'to': u"orm['directory.LBEAttribute']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'needReconciliationRDN': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reconciliation_object_different_policy': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'reconciliation_object_missing_policy': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'script': (
            'django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['directory.LBEScript']"}),
            'synced_at': (
            'django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1970, 1, 1, 0, 0)'}),
            'version': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'})
        },
        u'directory.lbereference': {
            'Meta': {'object_name': 'LBEReference'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'objectAttribute': (
            'django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directory.LBEAttribute']"}),
            'objectTemplate': (
            'django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directory.LBEObjectTemplate']"})
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