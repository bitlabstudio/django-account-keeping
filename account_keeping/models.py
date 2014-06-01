"""
Models for the account_keeping app.

TODO: Add lazy_trans and docstrings

"""
from decimal import Decimal

from django.db import models


class AmountMixin(object):
    """
    Mixin that handles amount_net, vat and amount_gross fields on save().

    """
    def set_amount_fields(self):
        if self.amount_net and not self.amount_gross:
            if self.vat:
                self.amount_gross = \
                    self.amount_net * (self.vat / Decimal(100.0) + 1)
            else:
                self.amount_gross = self.amount_net

        if self.amount_gross and not self.amount_net:
            if self.vat:
                self.amount_net = \
                    Decimal(1.0) / (self.vat / Decimal(100.0) + 1) \
                    * self.amount_gross
            else:
                self.amount_net = self.amount_gross


class Currency(models.Model):
    name = models.CharField(max_length=64)
    iso_code = models.CharField(max_length=3)
    is_base_currency = models.BooleanField(default=False)

    def __unicode__(self):
        return self.iso_code


class CurrencyRate(models.Model):
    currency = models.ForeignKey(Currency)
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=18, decimal_places=8)

    def __unicode__(self):
        return '{0}, {1}-{2}: {3}'.format(
            self.currency.iso_code, self.year, self.month, self.rate)


class Account(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)
    currency = models.ForeignKey(Currency, related_name='accounts')
    initial_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)

    def __unicode__(self):
        return self.name


class Invoice(AmountMixin, models.Model):
    INVOICE_TYPES = {
        'withdrawal': 'w',
        'deposit': 'd',
    }

    INVOICE_TYPE_CHOICES = [
        (INVOICE_TYPES['withdrawal'], 'withdrawal'),
        (INVOICE_TYPES['deposit'], 'deposit'),
    ]

    invoice_type = models.CharField(max_length=1, choices=INVOICE_TYPE_CHOICES)
    invoice_date = models.DateField()
    invoice_number = models.CharField(max_length=256, blank=True)
    currency = models.ForeignKey(Currency, related_name='invoices')
    amount_net = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    vat = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    amount_gross = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField(blank=True, null=True)
    pdf = models.FileField(upload_to='invoice_files', blank=True, null=True)

    class Meta:
        ordering = ['invoice_date', ]

    def __unicode__(self):
        if self.invoice_number:
            return self.invoice_number
        return '{0} - {1}'.format(self.invoice_date, self.invoice_type)

    def save(self, *args, **kwargs):
        self.set_amount_fields()
        return super(Invoice, self).save(*args, **kwargs)


class Payee(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


class Transaction(AmountMixin, models.Model):
    TRANSACTION_TYPES = {
        'withdrawal': 'w',
        'deposit': 'd',
    }

    TRANSACTION_TYPE_CHOICES = [
        (TRANSACTION_TYPES['withdrawal'], 'withdrawal'),
        (TRANSACTION_TYPES['deposit'], 'deposit'),
    ]

    account = models.ForeignKey(Account, related_name='transactions')
    parent = models.ForeignKey(
        'account_keeping.Transaction',
        related_name='children',
        blank=True, null=True,
    )
    transaction_type = models.CharField(
        max_length=1, choices=TRANSACTION_TYPE_CHOICES)
    transaction_date = models.DateField()
    description = models.TextField(blank=True)
    invoice_number = models.CharField(max_length=256, blank=True)
    invoice = models.ForeignKey(
        Invoice, blank=True, null=True, related_name='transactions')
    payee = models.ForeignKey(Payee, related_name='transactions')
    category = models.ForeignKey(Category, related_name='transactions')
    currency = models.ForeignKey(Currency, related_name='transactions')
    amount_net = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, blank=True)
    vat = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    amount_gross = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, blank=True)
    value_net = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    value_gross = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['transaction_date', ]

    def __unicode__(self):
        if self.invoice_number:
            return self.invoice_number
        if self.invoice and self.invoice.invoice_number:
            return self.invoice.invoice_number
        return '{0} - {1}'.format(self.payee, self.category)

    def save(self, *args, **kwargs):
        self.set_amount_fields()
        multiplier = 1
        if self.transaction_type == self.TRANSACTION_TYPES['withdrawal']:
            multiplier = -1
        self.value_net = self.amount_net * multiplier
        self.value_gross = self.amount_gross * multiplier

        return super(Transaction, self).save(*args, **kwargs)
