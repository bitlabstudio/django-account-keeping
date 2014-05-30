# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Currency'
        db.create_table(u'account_keeping_currency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('iso_code', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('is_base_currency', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'account_keeping', ['Currency'])

        # Adding model 'CurrencyRate'
        db.create_table(u'account_keeping_currencyrate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account_keeping.Currency'])),
            ('year', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('month', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('rate', self.gf('django.db.models.fields.DecimalField')(max_digits=18, decimal_places=8)),
        ))
        db.send_create_signal(u'account_keeping', ['CurrencyRate'])

        # Adding model 'Account'
        db.create_table(u'account_keeping_account', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=128)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(related_name='accounts', to=orm['account_keeping.Currency'])),
            ('initial_amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('total_amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
        ))
        db.send_create_signal(u'account_keeping', ['Account'])

        # Adding model 'Invoice'
        db.create_table(u'account_keeping_invoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('invoice_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('invoice_date', self.gf('django.db.models.fields.DateField')()),
            ('invoice_number', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invoices', to=orm['account_keeping.Currency'])),
            ('amount_net', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('vat', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=2)),
            ('amount_gross', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('payment_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('pdf', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'account_keeping', ['Invoice'])

        # Adding model 'Payee'
        db.create_table(u'account_keeping_payee', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'account_keeping', ['Payee'])

        # Adding model 'Category'
        db.create_table(u'account_keeping_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'account_keeping', ['Category'])

        # Adding model 'Transaction'
        db.create_table(u'account_keeping_transaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transactions', to=orm['account_keeping.Account'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['account_keeping.Transaction'])),
            ('transaction_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('transaction_date', self.gf('django.db.models.fields.DateField')()),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('invoice_number', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='transactions', null=True, to=orm['account_keeping.Invoice'])),
            ('payee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transactions', to=orm['account_keeping.Payee'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transactions', to=orm['account_keeping.Category'])),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transactions', to=orm['account_keeping.Currency'])),
            ('amount_net', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2, blank=True)),
            ('vat', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=2)),
            ('amount_gross', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2, blank=True)),
            ('value_net', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('value_gross', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
        ))
        db.send_create_signal(u'account_keeping', ['Transaction'])


    def backwards(self, orm):
        # Deleting model 'Currency'
        db.delete_table(u'account_keeping_currency')

        # Deleting model 'CurrencyRate'
        db.delete_table(u'account_keeping_currencyrate')

        # Deleting model 'Account'
        db.delete_table(u'account_keeping_account')

        # Deleting model 'Invoice'
        db.delete_table(u'account_keeping_invoice')

        # Deleting model 'Payee'
        db.delete_table(u'account_keeping_payee')

        # Deleting model 'Category'
        db.delete_table(u'account_keeping_category')

        # Deleting model 'Transaction'
        db.delete_table(u'account_keeping_transaction')


    models = {
        u'account_keeping.account': {
            'Meta': {'object_name': 'Account'},
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accounts'", 'to': u"orm['account_keeping.Currency']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '128'}),
            'total_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'})
        },
        u'account_keeping.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'account_keeping.currency': {
            'Meta': {'object_name': 'Currency'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_base_currency': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'account_keeping.currencyrate': {
            'Meta': {'object_name': 'CurrencyRate'},
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['account_keeping.Currency']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'rate': ('django.db.models.fields.DecimalField', [], {'max_digits': '18', 'decimal_places': '8'}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'account_keeping.invoice': {
            'Meta': {'ordering': "['invoice_date']", 'object_name': 'Invoice'},
            'amount_gross': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'amount_net': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': u"orm['account_keeping.Currency']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_date': ('django.db.models.fields.DateField', [], {}),
            'invoice_number': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'invoice_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'payment_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'pdf': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'vat': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '2'})
        },
        u'account_keeping.payee': {
            'Meta': {'object_name': 'Payee'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'account_keeping.transaction': {
            'Meta': {'ordering': "['transaction_date']", 'object_name': 'Transaction'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['account_keeping.Account']"}),
            'amount_gross': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'amount_net': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['account_keeping.Category']"}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['account_keeping.Currency']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'transactions'", 'null': 'True', 'to': u"orm['account_keeping.Invoice']"}),
            'invoice_number': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['account_keeping.Transaction']"}),
            'payee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['account_keeping.Payee']"}),
            'transaction_date': ('django.db.models.fields.DateField', [], {}),
            'transaction_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'value_gross': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'value_net': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'vat': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '2'})
        }
    }

    complete_apps = ['account_keeping']
