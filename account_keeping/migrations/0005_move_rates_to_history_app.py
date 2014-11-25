# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.conf import settings
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for currency in orm.Currency.objects.all():
            orm['currency_history.Currency'].objects.get_or_create(
                title=currency.name,
                iso_code=currency.iso_code,
            )
        for rate in orm.CurrencyRate.objects.all():
            from_currency = orm['currency_history.Currency'].objects.get(
                iso_code=rate.currency.iso_code)
            to_currency = orm['currency_history.Currency'].objects.get(
                iso_code=getattr(settings, 'BASE_CURRENCY', 'EUR'))
            rate_obj, created = orm[
                'currency_history.CurrencyRate'].objects.get_or_create(
                    from_currency=from_currency,
                    to_currency=to_currency,
                )
            history = orm['currency_history.CurrencyRateHistory'].objects.create(
                value=rate.rate,
                rate=rate_obj,
            )
            history.date = history.date.replace(day=1).replace(
                month=rate.month).replace(year=rate.year)
            history.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'account_keeping.account': {
            'Meta': {'object_name': 'Account'},
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accounts'", 'to': u"orm['currency_history.Currency']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '128'}),
            'total_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'})
        },
        u'account_keeping.category': {
            'Meta': {'ordering': "['name']", 'object_name': 'Category'},
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
            'Meta': {'ordering': "['-invoice_date']", 'object_name': 'Invoice'},
            'amount_gross': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'amount_net': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': u"orm['currency_history.Currency']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_date': ('django.db.models.fields.DateField', [], {}),
            'invoice_number': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'invoice_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'payment_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'pdf': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'value_gross': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'value_net': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'vat': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '2'})
        },
        u'account_keeping.payee': {
            'Meta': {'ordering': "['name']", 'object_name': 'Payee'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'account_keeping.transaction': {
            'Meta': {'ordering': "['-transaction_date']", 'object_name': 'Transaction'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['account_keeping.Account']"}),
            'amount_gross': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'amount_net': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['account_keeping.Category']"}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': u"orm['currency_history.Currency']"}),
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
        },
        u'currency_history.currency': {
            'Meta': {'ordering': "['iso_code']", 'object_name': 'Currency'},
            'abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'currency_history.currencyrate': {
            'Meta': {'ordering': "['from_currency__iso_code', 'to_currency__iso_code']", 'object_name': 'CurrencyRate'},
            'from_currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rates_from'", 'to': u"orm['currency_history.Currency']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'to_currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rates_to'", 'to': u"orm['currency_history.Currency']"})
        },
        u'currency_history.currencyratehistory': {
            'Meta': {'ordering': "['-date', 'rate__to_currency__iso_code']", 'object_name': 'CurrencyRateHistory'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'history'", 'to': u"orm['currency_history.CurrencyRate']"}),
            'tracked_by': ('django.db.models.fields.CharField', [], {'default': "u'Add your email'", 'max_length': '512'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['account_keeping']
    symmetrical = True
