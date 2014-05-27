"""Tests for the models of the account_keeping app."""
from django.test import TestCase

from . import factories


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

        obj = factories.TransactionFactory(transaction_type='C')
        self.assertEqual(obj.value_net, obj.amount_net, msg=(
            'When type is credit, the value should be positive'))

        obj = factories.TransactionFactory(transaction_type='D')
        self.assertEqual(obj.value_net, obj.amount_net * -1, msg=(
            'When type is debit, the value should be negative'))
