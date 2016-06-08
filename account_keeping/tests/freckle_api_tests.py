"""Tests for the freckle API functions of the account_keeping app."""
import json

from django.test import TestCase

from mixer.backend.django import mixer
from mock import patch
from requests import Response

from .. import freckle_api


class GetUnpaidInvoicesWithTransactionsTestCase(TestCase):
    """Tests for the ``get_unpaid_invoices_with_transactions`` function."""
    longMessage = True

    @patch('requests.request')
    def test_function(self, mock):
        invoice = mixer.blend('account_keeping.Invoice')
        mixer.blend('account_keeping.Transaction', invoice=invoice)
        resp = Response()
        resp._content = json.dumps([{
            'number': invoice.invoice_number,
        }])
        mock.return_value = resp
        self.assertEqual(
            len(freckle_api.get_unpaid_invoices_with_transactions()), 1)
