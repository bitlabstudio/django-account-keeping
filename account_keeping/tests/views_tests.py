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
        self.trans1 = factories.TransactionFactory()
        self.account = self.trans1.account
        self.account.currency.is_base_currency = True
        self.account.currency.save()
        self.trans2 = factories.TransactionFactory()
        factories.CurrencyRateFactory(
            currency=self.trans2.account.currency,
            year=now().year, month=now().month,
        )

    def get_view_kwargs(self):
        return {
            'year': self.trans1.transaction_date.year,
            'month': self.trans1.transaction_date.month,
        }

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(self.user)
