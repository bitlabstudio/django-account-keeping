"""Tests for the forms of the account_keeping app."""
from django.test import TestCase
from django.utils.timezone import now

from mixer.backend.django import mixer

from .. import forms


class InvoiceFormTestCase(TestCase):
    """Tests for the ``InvoiceForm`` form."""
    longMessage = True

    def test_form(self):
        form = forms.InvoiceForm(data={
            'invoice_type': 'd',
            'invoice_date': now().strftime('%Y-%m-%d'),
            'currency': mixer.blend('currency_history.Currency').pk,
            'vat': 0,
            'value_net': 0,
            'value_gross': 0,
        })
        self.assertFalse(form.errors)


class TransactionFormTestCase(TestCase):
    """Tests for the ``TransactionForm`` form."""
    longMessage = True

    def test_form(self):
        form = forms.TransactionForm(data={
            'transaction_type': 'd',
            'transaction_date': now().strftime('%Y-%m-%d'),
            'account': mixer.blend('account_keeping.Account').pk,
            'payee': mixer.blend('account_keeping.Payee').pk,
            'category': mixer.blend('account_keeping.Category').pk,
            'currency': mixer.blend('currency_history.Currency').pk,
            'vat': 0,
            'value_net': 0,
            'value_gross': 0,
        })
        self.assertFalse(form.errors)
