# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from uuid import UUID


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'tatianastore_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'tatianastore', ['User'])

        # Adding M2M table for field groups on 'User'
        m2m_table_name = db.shorten_name(u'tatianastore_user_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'tatianastore.user'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'User'
        m2m_table_name = db.shorten_name(u'tatianastore_user_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'tatianastore.user'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'permission_id'])

        # Adding model 'Store'
        db.create_table(u'tatianastore_store', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from='name')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(default='USD', max_length=5)),
            ('store_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal(u'tatianastore', ['Store'])

        # Adding M2M table for field operators on 'Store'
        m2m_table_name = db.shorten_name(u'tatianastore_store_operators')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('store', models.ForeignKey(orm[u'tatianastore.store'], null=False)),
            ('user', models.ForeignKey(orm[u'tatianastore.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['store_id', 'user_id'])

        # Adding model 'Album'
        db.create_table(u'tatianastore_album', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('store', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tatianastore.Store'])),
            ('uuid', self.gf('django.db.models.fields.CharField')(default=UUID('bbe7a447-9f96-4df4-9f71-a5c4ae17e5be'), max_length=64, blank=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from='name')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('fiat_price', self.gf('django.db.models.fields.DecimalField')(default='0', max_digits=16, decimal_places=8)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('cover', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('download_zip', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'tatianastore', ['Album'])

        # Adding model 'Song'
        db.create_table(u'tatianastore_song', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('store', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tatianastore.Store'])),
            ('uuid', self.gf('django.db.models.fields.CharField')(default=UUID('2d918b1d-4004-48a9-a267-20aa9bb48476'), max_length=64, blank=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from='name')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('fiat_price', self.gf('django.db.models.fields.DecimalField')(default='0', max_digits=16, decimal_places=8)),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tatianastore.Album'], null=True)),
            ('download_mp3', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('prelisten_mp3', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('prelisten_vorbis', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'tatianastore', ['Song'])

        # Adding model 'DownloadTransaction'
        db.create_table(u'tatianastore_downloadtransaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer_email', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('session_id', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(default=UUID('43a0fa31-0952-4f62-aa41-20d99fc62215'), max_length=64, blank=True)),
            ('store', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tatianastore.Store'], null=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('user_currency', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('btc_address', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('btc_amount', self.gf('django.db.models.fields.DecimalField')(default='0', max_digits=16, decimal_places=8)),
            ('fiat_amount', self.gf('django.db.models.fields.DecimalField')(default='0', max_digits=16, decimal_places=8)),
            ('payment_source', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('btc_received_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('manually_confirmed_received_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('received_transaction_hash', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('cancelled_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('expires_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('expired_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
        ))
        db.send_create_signal(u'tatianastore', ['DownloadTransaction'])

        # Adding model 'DownloadTransactionItem'
        db.create_table(u'tatianastore_downloadtransactionitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transaction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tatianastore.DownloadTransaction'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'tatianastore', ['DownloadTransactionItem'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'tatianastore_user')

        # Removing M2M table for field groups on 'User'
        db.delete_table(db.shorten_name(u'tatianastore_user_groups'))

        # Removing M2M table for field user_permissions on 'User'
        db.delete_table(db.shorten_name(u'tatianastore_user_user_permissions'))

        # Deleting model 'Store'
        db.delete_table(u'tatianastore_store')

        # Removing M2M table for field operators on 'Store'
        db.delete_table(db.shorten_name(u'tatianastore_store_operators'))

        # Deleting model 'Album'
        db.delete_table(u'tatianastore_album')

        # Deleting model 'Song'
        db.delete_table(u'tatianastore_song')

        # Deleting model 'DownloadTransaction'
        db.delete_table(u'tatianastore_downloadtransaction')

        # Deleting model 'DownloadTransactionItem'
        db.delete_table(u'tatianastore_downloadtransactionitem')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'tatianastore.album': {
            'Meta': {'object_name': 'Album'},
            'cover': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'download_zip': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'fiat_price': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '16', 'decimal_places': '8'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name'"}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tatianastore.Store']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "UUID('c74abac4-4a63-47f0-9d27-0382ae3e51d4')", 'max_length': '64', 'blank': 'True'})
        },
        u'tatianastore.downloadtransaction': {
            'Meta': {'object_name': 'DownloadTransaction'},
            'btc_address': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'btc_amount': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '16', 'decimal_places': '8'}),
            'btc_received_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'cancelled_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'customer_email': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'expired_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'expires_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fiat_amount': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '16', 'decimal_places': '8'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'manually_confirmed_received_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'payment_source': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'received_transaction_hash': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'session_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tatianastore.Store']", 'null': 'True'}),
            'user_currency': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "UUID('c145b555-3d43-450c-8ea3-e42180b0d715')", 'max_length': '64', 'blank': 'True'})
        },
        u'tatianastore.downloadtransactionitem': {
            'Meta': {'object_name': 'DownloadTransactionItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'transaction': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tatianastore.DownloadTransaction']"})
        },
        u'tatianastore.song': {
            'Meta': {'object_name': 'Song'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tatianastore.Album']", 'null': 'True'}),
            'download_mp3': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'fiat_price': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '16', 'decimal_places': '8'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'prelisten_mp3': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'prelisten_vorbis': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name'"}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tatianastore.Store']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "UUID('ef1277f4-da1d-4fb6-a6a7-3c851312e37b')", 'max_length': '64', 'blank': 'True'})
        },
        u'tatianastore.store': {
            'Meta': {'object_name': 'Store'},
            'currency': ('django.db.models.fields.CharField', [], {'default': "'USD'", 'max_length': '5'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'operators': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'operated_artits'", 'symmetrical': 'False', 'to': u"orm['tatianastore.User']"}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name'"}),
            'store_url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'tatianastore.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['tatianastore']