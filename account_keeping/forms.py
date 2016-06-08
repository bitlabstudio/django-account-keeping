"""Forms of the account_keeping app."""
from django import forms

from . import models


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = models.Invoice
        fields = '__all__'
        try:
            widgets = {
                'invoice_date': forms.widgets.SelectDateWidget(
                    attrs={'style': 'display: inline; width: auto;'}),
                'payment_date': forms.widgets.SelectDateWidget(
                    attrs={'style': 'display: inline; width: auto;'}),
            }
        except AttributeError:  # pragma: nocover
            widgets = {
                'invoice_date': forms.widgets.DateInput(),
                'payment_date': forms.widgets.DateInput(),
            }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = '__all__'
        try:
            widgets = {
                'transaction_date': forms.widgets.SelectDateWidget(
                    attrs={'style': 'display: inline; width: auto;'}),
            }
        except AttributeError:  # pragma: nocover
            widgets = {
                'transaction_date': forms.widgets.DateInput(),
            }
