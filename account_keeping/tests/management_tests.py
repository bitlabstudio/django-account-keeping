"""Tests for the management commands of the ``account_keeping`` app."""
from datetime import date
from os import path

from django.core.management import call_command, CommandError
from django.test import TestCase

from mixer.backend.django import mixer


class CommandTestCase(TestCase):
    def test_collect_invoices(self):
        transaction = mixer.blend('account_keeping.Transaction',
                                  transaction_date=date.today())
        mixer.blend('account_keeping.Transaction', parent=transaction)
        mixer.blend('account_keeping.Transaction',
                    transaction_date=date.today(), account=transaction.account)
        call_command('collect_invoices', account=transaction.account.slug,
                     start_date=date.today().strftime('%Y-%m-%d'),
                     end_date=date.today().strftime('%Y-%m-%d'),
                     output='./foo')

    def test_importer_mmex(self):
        currency = mixer.blend('currency_history.Currency')
        call_command('importer_mmex',
                     account=mixer.blend('account_keeping.Account').slug,
                     currency=currency.iso_code,
                     filepath=path.abspath(path.join(path.dirname(
                         path.dirname(__file__)), 'tests', 'test_file.csv')))
        with self.assertRaises(CommandError):
            call_command('importer_mmex', currency='FOO')
