"""Tests for the models of the account_keeping app."""
from decimal import Decimal

from django.test import TestCase

from . import factories
from .. import models


WITHDRAWAL = models.Transaction.TRANSACTION_TYPES['withdrawal']
DEPOSIT = models.Transaction.TRANSACTION_TYPES['deposit']


class CurrencyTestCase(TestCase):
    """Tests for the ``Currency`` model."""
    def test_model(self):
        obj = factories.CurrencyFactory()
        self.assertTrue(obj.pk)


class CurrencyRateTestCase(TestCase):
    """Tests for the ``CurrencyRate`` model."""
    def test_model(self):
        obj = factories.CurrencyRateFactory()
        self.assertTrue(obj.pk)


class AccountTestCase(TestCase):
    """Tests for the ``Account`` model."""
    def test_model(self):
        obj = factories.AccountFactory()
        self.assertTrue(obj.pk)


class InvoiceTestCase(TestCase):
    """Tests for the ``Invoice`` model."""
    def test_model(self):
        obj = factories.InvoiceFactory()
        self.assertTrue(obj.pk)


class PayeeTestCase(TestCase):
    """Tests for the ``Payee`` model."""
    def test_model(self):
        obj = factories.PayeeFactory()
        self.assertTrue(obj.pk)


class CategoryTestCase(TestCase):
    """Tests for the ``Category`` model."""
    def test_model(self):
        obj = factories.CategoryFactory()
        self.assertTrue(obj.pk)


class TransactionTestCase(TestCase):
    """Tests for the ``Transaction`` model."""
    longMessage = True

    def test_model(self):
        obj = factories.TransactionFactory()
        self.assertTrue(obj.pk)

    def test_save(self):
        obj = factories.TransactionFactory(
            amount_net=100, vat=19, amount_gross=None)
        self.assertEqual(obj.amount_gross, 119, msg=(
            'If only amount_net is given, amount_gross should be calculated'))

        obj = factories.TransactionFactory(
            amount_net=100, vat=0, amount_gross=None)
        self.assertEqual(obj.amount_gross, 100, msg=(
            'If only amount_net is given and VAT is 0, amount_gross should be'
            ' identical to amount_net'))

        obj = factories.TransactionFactory(
            amount_net=None, vat=19, amount_gross=119)
        self.assertEqual(obj.amount_net, 100, msg=(
            'If only amount_gross is given, amount_net should be calculated'))

        obj = factories.TransactionFactory(
            amount_net=None, vat=0, amount_gross=119)
        self.assertEqual(obj.amount_gross, 119, msg=(
            'If only amount_gross is given and VAT is 0, amount_net should be'
            ' identical to amount_gross'))

        obj = factories.TransactionFactory(transaction_type=DEPOSIT)
        self.assertEqual(obj.value_net, obj.amount_net, msg=(
            'When type is deposit, the value should be positive'))

        obj = factories.TransactionFactory(transaction_type=WITHDRAWAL)
        self.assertEqual(obj.value_net, obj.amount_net * -1, msg=(
            'When type is withdrawal, the value should be negative'))

    def test_get_description(self):
        """Tests for the ``get_description`` method."""
        trans = factories.TransactionFactory()
        result = trans.get_description()
        self.assertEqual(result, 'n/a', msg=(
            'If no description is set, it should return `n/a`'))

        trans.description = 'foo'
        trans.save()
        result = trans.get_description()
        self.assertEqual(result, 'foo', msg=(
            'If description is set, it should return the description'))

        invoice = factories.InvoiceFactory(description='barfoo')
        trans = factories.TransactionFactory(invoice=invoice)
        result = trans.get_description()
        self.assertEqual(result, 'barfoo', msg=(
            'If no description is set but the invoice has one, it should'
            ' return that one'))

        trans = factories.TransactionFactory()
        factories.TransactionFactory(parent=trans, description='foofoo')
        factories.TransactionFactory(parent=trans, description='barbar')
        result = trans.get_description()
        self.assertEqual(result, 'foofoo,\nbarbar,\n', msg=(
            'If no description is set but children have one, it should'
            ' return the descriptions of the children'))

        trans = factories.TransactionFactory()
        factories.TransactionFactory(parent=trans, invoice=invoice)
        factories.TransactionFactory(parent=trans, description='barbar')
        result = trans.get_description()
        self.assertEqual(result, 'barfoo,\nbarbar,\n', msg=(
            'If no description is set and children are present, but a child'
            ' doesn`t have a description, it should return the description of'
            ' the child`s invoice'))

    def test_get_invoices(self):
        """Tests for the ``get_invoices`` method."""
        trans = factories.TransactionFactory()
        result = trans.get_invoices()
        self.assertEqual(result, [None, ], msg=(
            'If it doesn`t have an invoice, it should return a list with'
            ' None'))

        invoice = factories.InvoiceFactory()
        trans.invoice = invoice
        trans.save
        result = trans.get_invoices()
        self.assertEqual(result, [invoice, ], msg=(
            'If it has an invoice, it should return a list with the invoice'))

        trans = factories.TransactionFactory()
        factories.TransactionFactory(parent=trans, invoice=invoice)
        result = trans.get_invoices()
        self.assertEqual(result, [invoice, ], msg=(
            'If it does not have an invoice, it should return the invoices of'
            ' it`s children'))

    def test_get_totals_by_payee(self):
        """Tests for the ``get_totals_by_payee`` method."""
        trans1a = factories.TransactionFactory()
        factories.TransactionFactory(
            account=trans1a.account, payee=trans1a.payee)
        factories.TransactionFactory(account=trans1a.account)
        result = models.Transaction.objects.get_totals_by_payee(
            trans1a.account)
        self.assertEqual(result[0]['value_gross__sum'], Decimal('-23.8'), msg=(
            'Should return all transactions grouped by payee'))
