"""Tests for the models of the account_keeping app."""
from django.test import TestCase
from django.utils.timezone import now, timedelta

from mixer.backend.django import mixer

from .. import models


WITHDRAWAL = models.Transaction.TRANSACTION_TYPES['withdrawal']
DEPOSIT = models.Transaction.TRANSACTION_TYPES['deposit']


class AccountTestCase(TestCase):
    """Tests for the ``Account`` model."""
    def setUp(self):
        self.account = mixer.blend('account_keeping.Account')

    def test_model(self):
        self.assertTrue(str(self.account))

    def test_get_balance(self):
        self.assertEqual(self.account.get_balance(), 0)


class InvoiceTestCase(TestCase):
    """Tests for the ``Invoice`` model."""
    def test_model(self):
        obj = mixer.blend('account_keeping.Invoice', invoice_number='')
        self.assertTrue(str(obj))
        obj.invoice_number = 'Foo123'
        obj.save()
        self.assertEqual(str(obj), 'Foo123')

    def test_manager(self):
        mixer.blend('account_keeping.Invoice')
        mixer.blend('account_keeping.Invoice')
        self.assertEqual(models.Invoice.objects.get_without_pdf().count(), 2)

    def test_balance(self):
        invoice = mixer.blend('account_keeping.Invoice', amount_net=100)
        self.assertEqual(int(invoice.balance), -100)
        mixer.blend('account_keeping.Transaction', amount_net=10,
                    invoice=invoice, currency=invoice.currency)
        transaction = mixer.blend('account_keeping.Transaction', amount_net=50,
                                  invoice=invoice)
        mixer.blend('currency_history.CurrencyRateHistory', value=0.5,
                    rate__from_currency=transaction.currency,
                    rate__to_currency=invoice.currency)
        self.assertEqual(int(invoice.balance), -65)


class PayeeTestCase(TestCase):
    """Tests for the ``Payee`` model."""
    def setUp(self):
        self.payee = mixer.blend('account_keeping.Payee')

    def test_model(self):
        self.assertTrue(str(self.payee))

    def test_invoices(self):
        self.assertEqual(self.payee.invoices().count(), 0)


class CategoryTestCase(TestCase):
    """Tests for the ``Category`` model."""
    def test_model(self):
        obj = mixer.blend('account_keeping.Category')
        self.assertTrue(str(obj))


class TransactionTestCase(TestCase):
    """Tests for the ``Transaction`` model."""
    longMessage = True

    def setUp(self):
        self.transaction = mixer.blend('account_keeping.Transaction',
                                       invoice_number='')

    def test_model(self):
        self.assertTrue(str(self.transaction))
        self.transaction.invoice = mixer.blend('account_keeping.Invoice')
        self.assertEqual(str(self.transaction),
                         self.transaction.invoice.invoice_number)
        self.transaction.invoice_number = 'Foo123'
        self.assertEqual(str(self.transaction), 'Foo123')

    def test_save(self):
        obj = mixer.blend(
            'account_keeping.Transaction',
            amount_net=100, vat=19, amount_gross=None)
        self.assertEqual(obj.amount_gross, 119, msg=(
            'If only amount_net is given, amount_gross should be calculated'))

        obj = mixer.blend(
            'account_keeping.Transaction',
            amount_net=100, vat=0, amount_gross=None)
        self.assertEqual(obj.amount_gross, 100, msg=(
            'If only amount_net is given and VAT is 0, amount_gross should be'
            ' identical to amount_net'))

        obj = mixer.blend(
            'account_keeping.Transaction',
            amount_net=None, vat=19, amount_gross=119)
        self.assertEqual(obj.amount_net, 100, msg=(
            'If only amount_gross is given, amount_net should be calculated'))

        obj = mixer.blend(
            'account_keeping.Transaction',
            amount_net=None, vat=0, amount_gross=119)
        self.assertEqual(obj.amount_gross, 119, msg=(
            'If only amount_gross is given and VAT is 0, amount_net should be'
            ' identical to amount_gross'))

        obj = mixer.blend('account_keeping.Transaction',
                          transaction_type=DEPOSIT)
        self.assertEqual(obj.value_net, obj.amount_net, msg=(
            'When type is deposit, the value should be positive'))

        obj = mixer.blend('account_keeping.Transaction',
                          transaction_type=WITHDRAWAL)
        self.assertEqual(obj.value_net, obj.amount_net * -1, msg=(
            'When type is withdrawal, the value should be negative'))

    def test_get_description(self):
        """Tests for the ``get_description`` method."""
        trans = mixer.blend('account_keeping.Transaction', description='')
        result = trans.get_description()
        self.assertEqual(result, 'n/a', msg=(
            'If no description is set, it should return `n/a`'))

        trans.description = 'foo'
        trans.save()
        result = trans.get_description()
        self.assertEqual(result, 'foo', msg=(
            'If description is set, it should return the description'))

        invoice = mixer.blend('account_keeping.Invoice', description='barfoo')
        trans = mixer.blend('account_keeping.Transaction', invoice=invoice,
                            description='')
        result = trans.get_description()
        self.assertEqual(result, 'barfoo', msg=(
            'If no description is set but the invoice has one, it should'
            ' return that one'))

        trans = mixer.blend('account_keeping.Transaction', description='')
        mixer.blend('account_keeping.Transaction', parent=trans,
                    description='foofoo',
                    transaction_date=now() - timedelta(days=2))
        mixer.blend('account_keeping.Transaction', parent=trans,
                    description='barbar',
                    transaction_date=now() - timedelta(days=1))
        result = trans.get_description()
        self.assertEqual(result, 'barbar,\nfoofoo,\n', msg=(
            'If no description is set but children have one, it should'
            ' return the descriptions of the children'))

        trans = mixer.blend('account_keeping.Transaction', description='')
        mixer.blend('account_keeping.Transaction',
                    parent=trans, invoice=invoice, description='')
        mixer.blend('account_keeping.Transaction', parent=trans,
                    description='barbar',
                    transaction_date=now() - timedelta(days=1))
        result = trans.get_description()
        self.assertEqual(result, 'barbar,\nbarfoo,\n', msg=(
            'If no description is set and children are present, but a child'
            ' doesn\'t have a description, it should return the description of'
            ' the child\'s invoice'))

    def test_get_invoices(self):
        """Tests for the ``get_invoices`` method."""
        trans = mixer.blend('account_keeping.Transaction')
        result = trans.get_invoices()
        self.assertEqual(result, [None, ], msg=(
            'If it doesn`t have an invoice, it should return a list with'
            ' None'))

        invoice = mixer.blend('account_keeping.Invoice')
        trans.invoice = invoice
        trans.save
        result = trans.get_invoices()
        self.assertEqual(result, [invoice, ], msg=(
            'If it has an invoice, it should return a list with the invoice'))

        trans = mixer.blend('account_keeping.Transaction')
        mixer.blend('account_keeping.Transaction',
                    parent=trans, invoice=invoice)
        result = trans.get_invoices()
        self.assertEqual(result, [invoice, ], msg=(
            'If it does not have an invoice, it should return the invoices of'
            ' it`s children'))

    def test_get_totals_by_payee(self):
        """Tests for the ``get_totals_by_payee`` method."""
        trans1a = mixer.blend('account_keeping.Transaction', value_gross=11.9)
        mixer.blend('account_keeping.Transaction', value_gross=11.9,
                    account=trans1a.account, payee=trans1a.payee)
        mixer.blend('account_keeping.Transaction', account=trans1a.account,
                    value_gross=11.9)
        result = models.Transaction.objects.get_totals_by_payee(
            trans1a.account)
        self.assertEqual(result.count(), 2, msg=(
            'Should return all transactions grouped by payee'))

    def test_manager(self):
        self.assertEqual(
            models.Transaction.objects.get_without_invoice().count(), 1)
