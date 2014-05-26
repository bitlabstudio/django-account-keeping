"""Factories for the account_keeping app."""
from django.utils.timezone import now

import factory

from .. import models


class CurrencyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Currency

    name = factory.Sequence(lambda n: 'name{0}'.format(n))
    iso_code = factory.Sequence(lambda n: 'iso{0}'.format(n))


class AccountFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Account

    name = factory.Sequence(lambda n: 'name{0}'.format(n))
    slug = factory.Sequence(lambda n: 'slug{0}'.format(n))
    currency = factory.SubFactory(CurrencyFactory)


class InvoiceFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Invoice

    invoice_type = 'credit'
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

    date = factory.LazyAttribute(lambda x: now())
    payee = factory.SubFactory(PayeeFactory)
    category = factory.SubFactory(CategoryFactory)
    currency = factory.SubFactory(CurrencyFactory)
    amount_net = 10
    vat = 19
    amount_gross = 11.9
