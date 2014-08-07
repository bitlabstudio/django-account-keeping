"""Tests for the views of the account_keeping app."""
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import now

from django_libs.tests.factories import UserFactory
from django_libs.tests.mixins import ViewRequestFactoryTestMixin

from . import factories
from .. import views


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


class CurrentMonthRedirectViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``CurrentMonthRedirectView`` view class."""
    longMessage = True
    view_class = views.CurrentMonthRedirectView

    def setUp(self):
        super(CurrentMonthRedirectViewTestCase, self).setUp()
        self.now_ = now()

    def get_view_kwargs(self):
        return {'year': self.now_.year, 'month': self.now_.month}

    def test_view(self):
        expected_url = reverse(
            'account_keeping_month', kwargs=self.get_view_kwargs())
        self.redirects(expected_url)


class CurrentYearRedirectViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``CurrentYearRedirectView`` view class."""
    longMessage = True
    view_class = views.CurrentYearRedirectView

    def setUp(self):
        super(CurrentYearRedirectViewTestCase, self).setUp()
        self.now_ = now()

    def get_view_kwargs(self):
        return {'year': self.now_.year, }

    def test_view(self):
        expected_url = reverse(
            'account_keeping_year', kwargs=self.get_view_kwargs())
        self.redirects(expected_url)


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


class YearOverviewViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``YearOverviewView`` view class."""
    longMessage = True
    view_class = views.YearOverviewView

    def setUp(self):
        self.user = UserFactory(is_superuser=True)
        self.ccy = factories.CurrencyFactory(is_base_currency=True)
        for i in range(12):
            factories.CurrencyRateFactory(currency=self.ccy, month=i + 1)
        self.account = factories.AccountFactory(currency=self.ccy)
        self.trans1 = factories.TransactionFactory(
            account=self.account, currency=self.ccy)
        self.trans2 = factories.TransactionFactory(
            account=self.account, currency=self.ccy,
            transaction_type=views.DEPOSIT)

        self.ccy2 = factories.CurrencyFactory()
        for i in range(12):
            factories.CurrencyRateFactory(currency=self.ccy2, month=i + 1)
        self.account2 = factories.AccountFactory(currency=self.ccy2)
        self.trans3 = factories.TransactionFactory(
            account=self.account2, currency=self.ccy2)

    def get_view_kwargs(self):
        return {'year': self.trans1.transaction_date.year, }

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(self.user)
