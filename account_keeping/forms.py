"""Forms of the account_keeping app."""
from django import forms
from django.utils.translation import ugettext_lazy as _

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
                'invoice_date': forms.widgets.DateInput,
                'payment_date': forms.widgets.DateInput,
            }


class TransactionForm(forms.ModelForm):
    mark_invoice = forms.BooleanField(
        label=_('Mark invoice as paid?'),
        initial=True,
        required=False,
        widget=forms.widgets.CheckboxInput(
            attrs={'data-id': 'mark-invoice-field'}),
    )

    class Meta:
        model = models.Transaction
        fields = '__all__'
        try:
            date_widget = forms.widgets.SelectDateWidget(
                attrs={'style': 'display: inline; width: auto;'})
        except AttributeError:  # pragma: nocover
            date_widget = forms.widgets.DateInput
        widgets = {
            'transaction_date': date_widget,
            'invoice': forms.widgets.NumberInput(
                attrs={'data-id': 'invoice-field'}),
        }

    def save(self, *args, **kwargs):
        if self.instance.invoice and self.cleaned_data.get('mark_invoice'):
            # Set the payment date on related invoice
            self.instance.invoice.payment_date = self.instance.transaction_date
            self.instance.invoice.save()
        return super(TransactionForm, self).save(*args, **kwargs)
