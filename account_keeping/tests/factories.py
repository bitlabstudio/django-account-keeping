"""Factories for the account_keeping app."""
from django.utils.timezone import now

import factory
from currency_history.tests.factories import CurrencyFactory

from .. import models


class AccountFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Account

    name = factory.Sequence(lambda n: 'name{0}'.format(n))
    slug = factory.Sequence(lambda n: 'slug{0}'.format(n))
    currency = factory.SubFactory(CurrencyFactory)


class InvoiceFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Invoice

    invoice_type = models.Invoice.INVOICE_TYPES['withdrawal']
    invoice_date = factory.LazyAttribute(lambda x: now())
    currency = factory.SubFactory(CurrencyFactory)
    amount_net = 10
    vat = 19
    amount_gross = 11.9


class PayeeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Payee

    name = factory.Sequence(lambda n: 'name{0}'.format(n))


class CategoryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Category

    name = factory.Sequence(lambda n: 'name{0}'.format(n))


class TransactionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Transaction

    account = factory.SubFactory(AccountFactory)
    transaction_date = factory.LazyAttribute(lambda x: now())
    transaction_type = models.Transaction.TRANSACTION_TYPES['withdrawal']
    payee = factory.SubFactory(PayeeFactory)
    category = factory.SubFactory(CategoryFactory)
    currency = factory.SubFactory(CurrencyFactory)
    amount_net = 10
    vat = 19
    amount_gross = 11.9
