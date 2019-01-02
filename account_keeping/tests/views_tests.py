"""Tests for the views of the account_keeping app."""
import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import now, timedelta

from django_libs.tests.mixins import ViewRequestFactoryTestMixin
from mixer.backend.django import mixer
from mock import patch
from requests import Response

from .. import views


class AllTimeViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``AllTimeView`` view class."""
    view_class = views.AllTimeView

    def setUp(self):
        self.user = mixer.blend('auth.User', is_superuser=True)
        self.ccy = mixer.blend('currency_history.Currency', iso_code='EUR')
        self.account = mixer.blend(
            'account_keeping.Account', currency=self.ccy,
            branch__currency=self.ccy)
        self.trans1 = mixer.blend(
            'account_keeping.Transaction',
            account=self.account, currency=self.ccy)

        self.ccy2 = mixer.blend('currency_history.Currency')
        self.account2 = mixer.blend(
            'account_keeping.Account', currency=self.ccy2,
            branch__currency=self.ccy2)
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
        req = self.get_get_request(user=self.user)
        req.COOKIES['django_account_keeping_branch'] = 'main'
        view = self.get_view()
        resp = view(req)
        self.assert200(resp, self.user)


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
        self.account = mixer.blend(
            'account_keeping.Account', currency=self.ccy,
            branch__currency=self.ccy)
        self.trans1 = mixer.blend(
            'account_keeping.Transaction',
            account=self.account, currency=self.ccy)

        self.ccy2 = mixer.blend('currency_history.Currency')
        self.account2 = mixer.blend(
            'account_keeping.Account', currency=self.ccy2,
            branch__currency=self.ccy2)
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
        req = self.get_get_request(user=self.user,
                                   view_kwargs=self.get_view_kwargs())
        req.COOKIES['django_account_keeping_branch'] = 'foo'
        view = self.get_view()
        resp = view(req, **self.get_view_kwargs())
        self.assert200(resp, self.user)
        self.is_callable(self.user, kwargs={
            'year': now().year, 'month': now().month})


class YearOverviewViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``YearOverviewView`` view class."""
    view_class = views.YearOverviewView

    def setUp(self):
        self.user = mixer.blend('auth.User', is_superuser=True)
        self.ccy = mixer.blend('currency_history.Currency', iso_code='EUR')
        self.account = mixer.blend(
            'account_keeping.Account', currency=self.ccy,
            branch__currency=self.ccy)
        self.trans1 = mixer.blend(
            'account_keeping.Transaction', transaction_date=now(),
            account=self.account, currency=self.ccy)
        mixer.blend(
            'account_keeping.Transaction', transaction_date=now(),
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
        self.account2 = mixer.blend(
            'account_keeping.Account', currency=self.ccy2,
            branch__currency=self.ccy2)
        mixer.blend(
            'account_keeping.Transaction', transaction_date=now(),
            transaction_type=views.WITHDRAWAL,
            account=self.account2, currency=self.ccy2)
        mixer.blend(
            'account_keeping.Transaction', transaction_date=now(),
            transaction_type=views.DEPOSIT,
            account=self.account2, currency=self.ccy)

        mixer.blend(
            'account_keeping.Invoice', invoice_date=now(),
            invoice_type=views.DEPOSIT,
            account=self.account2, currency=self.ccy2,
            branch__currency=self.ccy2)

    def get_view_kwargs(self):
        return {'year': now().year, }

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(self.user)
        self.is_callable(self.user, kwargs={'year': now().year})


class IndexViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``IndexView`` view class."""
    view_class = views.IndexView

    def setUp(self):
        self.user = mixer.blend('auth.User', is_superuser=True)
        mixer.blend('account_keeping.Transaction')

    @patch('requests.request')
    def test_view(self, mock):
        resp = Response()
        resp.status_code = 200
        resp._content = json.dumps([{
            'reference': 1,
        }])
        mock.return_value = resp
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(self.user)


class BranchSelectViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``BranchSelectView`` view class."""
    view_class = views.BranchSelectView

    def setUp(self):
        self.user = mixer.blend('auth.User')
        self.branch = mixer.blend('account_keeping.Branch')

    def get_view_kwargs(self):
        return {'slug': self.branch.slug}

    def test_view(self):
        self.redirects(user=self.user, to='/')
        self.is_not_callable(self.user, kwargs={'slug': 'foo'})


class PayeeListViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``PayeeListView`` view class."""
    view_class = views.PayeeListView

    def setUp(self):
        self.user = mixer.blend('auth.User', is_superuser=True)
        mixer.blend('account_keeping.Transaction')

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(self.user)


class InvoiceCreateViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``InvoiceCreateView`` view class."""
    view_class = views.InvoiceCreateView

    def setUp(self):
        self.user = mixer.blend('auth.User', is_superuser=True)

    def test_view(self):
        self.is_callable(self.user)
        self.is_postable(self.user, data={
            'invoice_type': 'd',
            'invoice_date': now().strftime('%Y-%m-%d'),
            'currency': mixer.blend('currency_history.Currency').pk,
            'branch': mixer.blend('account_keeping.Branch').pk,
            'amount_net': 0,
            'amount_gross': 0,
            'vat': 0,
            'value_net': 0,
            'value_gross': 0,
        }, to_url_name='account_keeping_month')


class TransactionCreateViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``TransactionCreateView`` view class."""
    view_class = views.TransactionCreateView

    def setUp(self):
        self.user = mixer.blend('auth.User', is_superuser=True)

    def test_view(self):
        self.is_callable(self.user)
        date = now()
        account = mixer.blend('account_keeping.Account')
        data = {
            'transaction_type': 'd',
            'transaction_date': date.strftime('%Y-%m-%d'),
            'account': account.pk,
            'payee': mixer.blend('account_keeping.Payee').pk,
            'category': mixer.blend('account_keeping.Category').pk,
            'currency': mixer.blend('currency_history.Currency').pk,
            'amount_net': 0,
            'amount_gross': 0,
            'vat': 0,
            'value_net': 0,
            'value_gross': 0,
        }
        self.is_postable(self.user, data=data, to=u'{}#{}'.format(
            reverse('account_keeping_month', kwargs={
                'year': date.year, 'month': date.month}), account.slug))

        self.is_callable(self.user, data={'invoice': 1})
        self.is_callable(self.user, data={'parent': 1})


class TransactionExportViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``TransactionExportView`` view class."""
    view_class = views.TransactionExportView

    def setUp(self):
        self.user = mixer.blend('auth.User', is_superuser=True)

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(self.user)
        self.is_postable(user=self.user, ajax=True, data={
            'account': mixer.blend('account_keeping.Account').pk,
            'start': '2015-01-01',
            'end': '2018-01-01',
        })
