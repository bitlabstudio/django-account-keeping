"""Tests for the views of the account_keeping app."""
from django.test import TestCase
from django.utils.timezone import now

from django_libs.tests.factories import UserFactory
from django_libs.tests.mixins import ViewRequestFactoryTestMixin

from . import factories
from .. import views


class MonthViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``MonthView`` view class."""
    longMessage = True
    view_class = views.MonthView

    def setUp(self):
        self.user = UserFactory(is_superuser=True)
        self.ccy = factories.CurrencyFactory(is_base_currency=True)
        self.account = factories.AccountFactory(currency=self.ccy)
        self.trans1 = factories.TransactionFactory(
            account=self.account, currency=self.ccy)

        self.ccy2 = factories.CurrencyFactory()
        self.account2 = factories.AccountFactory(currency=self.ccy2)
        self.trans2 = factories.TransactionFactory(
            account=self.account2, currency=self.ccy2)
        factories.CurrencyRateFactory(
            currency=self.ccy2, year=now().year, month=now().month)

    def get_view_kwargs(self):
        return {
            'year': self.trans1.transaction_date.year,
            'month': self.trans1.transaction_date.month,
        }

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(self.user)


class AllTimeViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``AllTimeView`` view class."""
    longMessage = True
    view_class = views.AllTimeView

    def setUp(self):
        self.user = UserFactory(is_superuser=True)
        self.ccy = factories.CurrencyFactory(is_base_currency=True)
        self.account = factories.AccountFactory(currency=self.ccy)
        self.trans1 = factories.TransactionFactory(
            account=self.account, currency=self.ccy)

        self.ccy2 = factories.CurrencyFactory()
        self.account2 = factories.AccountFactory(currency=self.ccy2)
        self.trans2 = factories.TransactionFactory(
            account=self.account2, currency=self.ccy2)
        factories.CurrencyRateFactory(
            currency=self.ccy2, year=now().year, month=now().month)

    def get_view_kwargs(self):
        return {}

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(self.user)


class YearOverviewViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``YearOverviewView`` view class."""
    longMessage = True
    view_class = views.YearOverviewView

    def setUp(self):
        self.user = UserFactory(is_superuser=True)
        self.ccy = factories.CurrencyFactory(is_base_currency=True)
        self.account = factories.AccountFactory(currency=self.ccy)
        self.trans1 = factories.TransactionFactory(
            account=self.account, currency=self.ccy)
        self.trans2 = factories.TransactionFactory(
            account=self.account, currency=self.ccy,
            transaction_type=views.DEPOSIT)

        self.ccy2 = factories.CurrencyFactory()
        self.account2 = factories.AccountFactory(currency=self.ccy2)
        self.trans3 = factories.TransactionFactory(
            account=self.account2, currency=self.ccy2)
        factories.CurrencyRateFactory(
            currency=self.ccy2, year=now().year, month=now().month)

    def get_view_kwargs(self):
        return {'year': self.trans1.transaction_date.year, }

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(self.user)
