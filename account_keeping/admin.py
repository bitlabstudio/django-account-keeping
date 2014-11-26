"""Admin classes for the account_keeping app."""
from django.contrib import admin

from . import models


class AccountAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'slug', 'currency', 'initial_amount', 'total_amount']
admin.site.register(models.Account, AccountAdmin)


class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_type', 'invoice_date', 'currency', 'amount_net', 'vat',
        'amount_gross', 'payment_date']
    list_filter = ['invoice_type', 'currency', 'payment_date']
    date_hierarchy = 'invoice_date'
    search_fields = ['invoice_number', 'description']
admin.site.register(models.Invoice, InvoiceAdmin)


class PayeeAdmin(admin.ModelAdmin):
    list_display = ['name', ]
admin.site.register(models.Payee, PayeeAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', ]
admin.site.register(models.Category, CategoryAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_date', 'parent', 'invoice_number', 'invoice', 'payee',
        'category', 'currency', 'value_net', 'vat', 'value_gross', ]
    list_filter = ['account', 'currency', 'payee', 'category']
    date_hierarchy = 'transaction_date'
    raw_id_fields = ['parent', 'invoice']
    search_fields = [
        'invoice_number', 'invoice__invoice_number', 'description']
admin.site.register(models.Transaction, TransactionAdmin)
