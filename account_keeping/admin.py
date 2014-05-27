"""Admin classes for the account_keeping app."""
from django.contrib import admin

from . import models


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'iso_code']
admin.site.register(models.Currency, CurrencyAdmin)


class AccountAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'slug', 'currency', 'initial_amount', 'total_amount']
admin.site.register(models.Account, AccountAdmin)


class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_type', 'invoice_date', 'currency', 'amount_net', 'vat',
        'amount_gross', 'payment_date']
    list_filter = ['invoice_type', ]
    date_hierarchy = 'invoice_date'
admin.site.register(models.Invoice, InvoiceAdmin)


class PayeeAdmin(admin.ModelAdmin):
    list_display = ['name', ]
admin.site.register(models.Payee, PayeeAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', ]
admin.site.register(models.Category, CategoryAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_date', 'invoice_number', 'invoice', 'payee', 'category',
        'currency', 'value_net', 'vat', 'value_gross', ]
    list_filter = ['account', ]
    date_hierarchy = 'transaction_date'
admin.site.register(models.Transaction, TransactionAdmin)
