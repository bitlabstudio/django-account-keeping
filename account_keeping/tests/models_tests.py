"""Tests for the models of the account_keeping app."""
from django.test import TestCase

from . import factories


class CurrencyTestCase(TestCase):
    """Tests for the ``Currency`` model."""
    def test_model(self):
        obj = factories.CurrencyFactory()
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
