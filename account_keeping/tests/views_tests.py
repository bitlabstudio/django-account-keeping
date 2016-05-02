"""Tests for the views of the account_keeping app."""
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import now, timedelta

from django_libs.tests.mixins import ViewRequestFactoryTestMixin
from mixer.backend.django import mixer

from .. import views


class AllTimeViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``AllTimeView`` view class."""
    view_class = views.AllTimeView

    def setUp(self):
        self.user = mixer.blend('auth.User', is_superuser=True)
        self.ccy = mixer.blend('currency_history.Currency', iso_code='EUR')
        self.account = mixer.blend('account_keeping.Account',
                                   currency=self.ccy)
        self.trans1 = mixer.blend(
            'account_keeping.Transaction',
            account=self.account, currency=self.ccy)

        self.ccy2 = mixer.blend('currency_history.Currency')
        self.account2 = mixer.blend('account_keeping.Account',
                                    currency=self.ccy2)
        self.trans2 = mixer.blend(
            'account_keeping.Transaction',
            account=self.account2, currency=self.ccy2)
        mixer.blend(
            'currency_history.CurrencyRateHistory',
            rate__from_currency=self.ccy2,
            rate__to_currency=self.ccy,
            date=now(),
        )

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(self.user)


class CurrentMonthRedirectViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``CurrentMonthRedirectView`` view class."""
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
    view_class = views.MonthView

    def setUp(self):
        self.user = mixer.blend('auth.User', is_superuser=True)
        self.ccy = mixer.blend('currency_history.Currency', iso_code='EUR')
        self.account = mixer.blend('account_keeping.Account',
                                   currency=self.ccy)
        self.trans1 = mixer.blend(
            'account_keeping.Transaction',
            account=self.account, currency=self.ccy)

        self.ccy2 = mixer.blend('currency_history.Currency')
        self.account2 = mixer.blend('account_keeping.Account',
                                    currency=self.ccy2)
        self.trans2 = mixer.blend(
            'account_keeping.Transaction',
            account=self.account2, currency=self.ccy2)
        rate = mixer.blend(
            'currency_history.CurrencyRateHistory',
            rate__from_currency=self.ccy2,
            rate__to_currency=self.ccy,
        )
        rate.date = now() - timedelta(days=131)
        rate.save()

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
    view_class = views.YearOverviewView

    def setUp(self):
        self.user = mixer.blend('auth.User', is_superuser=True)
        self.ccy = mixer.blend('currency_history.Currency', iso_code='EUR')
        self.account = mixer.blend('account_keeping.Account',
                                   currency=self.ccy)
        self.trans1 = mixer.blend(
            'account_keeping.Transaction',
            account=self.account, currency=self.ccy)
        self.trans2 = mixer.blend(
            'account_keeping.Transaction',
            account=self.account, currency=self.ccy,
            transaction_type=views.DEPOSIT)

        self.ccy2 = mixer.blend('currency_history.Currency')
        for i in range(11):
            new_date = now().replace(day=1).replace(month=i + 2)
            rate = mixer.blend(
                'currency_history.CurrencyRateHistory',
                rate__from_currency=self.ccy2,
                rate__to_currency=self.ccy,
            )
            rate.date = new_date
            rate.save()
        self.account2 = mixer.blend('account_keeping.Account',
                                    currency=self.ccy2)
        self.trans3 = mixer.blend(
            'account_keeping.Transaction',
            account=self.account2, currency=self.ccy2)

    def get_view_kwargs(self):
        return {'year': self.trans1.transaction_date.year, }

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(self.user)


class IndexViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``IndexView`` view class."""
    view_class = views.IndexView

    def setUp(self):
        self.user = mixer.blend('auth.User', is_superuser=True)
        mixer.blend('account_keeping.Transaction')

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(self.user)
