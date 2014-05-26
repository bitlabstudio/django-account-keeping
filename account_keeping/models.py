"""Models for the account_keeping app."""
from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=64)
    iso_code = models.CharField(max_length=3)
    usd_rate = models.DecimalField(max_digits=10, decimal_places=8)


class Account(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)
    currency = models.ForeignKey(Currency, related_name='accounts')
    initial_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)


class Invoice(models.Model):
    INVOICE_TYPES = [
        'C', 'D',
    ]

    INVOICE_TYPE_CHOICES = [
        (INVOICE_TYPES[0], 'credit'),
        (INVOICE_TYPES[1], 'debit'),
    ]

    invoice_type = models.CharField(max_length=1, choices=INVOICE_TYPE_CHOICES)
    invoice_date = models.DateField()
    currency = models.ForeignKey(Currency, related_name='invoices')
    amount_net = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    vat = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    amount_gross = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField(blank=True, null=True)


class Payee(models.Model):
    name = models.CharField(max_length=256)


class Category(models.Model):
    name = models.CharField(max_length=256)


class Transaction(models.Model):
    date = models.DateField()
    description = models.TextField(blank=True)
    invoice_number = models.CharField(max_length=256, blank=True)
    invoice = models.ForeignKey(
        Invoice, blank=True, null=True, related_name='transactions')
    payee = models.ForeignKey(Payee, related_name='transactions')
    category = models.ForeignKey(Category, related_name='transactions')
    currency = models.ForeignKey(Currency, related_name='transactions')
    amount_net = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    vat = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    amount_gross = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
