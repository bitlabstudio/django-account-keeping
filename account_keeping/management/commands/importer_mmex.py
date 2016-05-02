"""
Importer that handles .csv files exported via Money Manager Ex.

IMPORTANT: MMEX does not distinguish between incoming and outgoing "Transfer"
transactions. After you export the .csv you must identify all incoming
"Transfer" transactions and rename the type to "TransferDeposit".

"""
from decimal import Decimal
from optparse import make_option
import csv
import datetime

from django.core.management.base import BaseCommand, CommandError

from currency_history.models import Currency

from ... import models


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '-f', '--file',
            dest='filepath',
            help='Filepath to the .csv file that contains the data'),
        make_option(
            '-a', '--account',
            dest='account',
            help='Account slug of the account that should hold the new data'),
        make_option(
            '-c', '--currency',
            dest='currency',
            help='ISO-code of the currency for the specified data'),
        make_option(
            '-t', '--vat',
            dest='vat',
            help='VAT that should be applied to all transactions (i.e. 19)'),
    )
    help = 'Imports the specified .csv file from mmex'

    def handle(self, *args, **options):
        try:
            currency = Currency.objects.get(iso_code=options.get('currency'))
        except Currency.DoesNotExist:
            raise CommandError('The specified currency does not exist')

        account = models.Account.objects.get(slug=options.get('account'))
        vat = options.get('vat')
        if not vat:
            vat = 0
        vat = Decimal(vat)

        filepath = options.get('filepath')

        deposit = models.Transaction.TRANSACTION_TYPES['deposit']
        withdrawal = models.Transaction.TRANSACTION_TYPES['withdrawal']

        with open(filepath, 'rb') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                transaction_date = datetime.datetime.strptime(
                    row[0], '%d/%m/%Y')
                payee, created = models.Payee.objects.get_or_create(
                    name=row[1])
                if row[2] in ['Withdrawal', 'Transfer']:
                    transaction_type = withdrawal
                else:
                    transaction_type = deposit
                amount = Decimal(row[3])
                if row[4] and not row[5]:
                    cat_name = row[4]
                else:
                    cat_name = row[5]
                category, created = models.Category.objects.get_or_create(
                    name=cat_name)
                description = row[7]

                invoice = models.Invoice.objects.create(
                    invoice_type=transaction_type,
                    invoice_date=datetime.date(1900, 1, 1),
                    currency=currency,
                    amount_gross=amount,
                    vat=vat,
                    payment_date=transaction_date,
                )

                models.Transaction.objects.create(
                    account=account,
                    transaction_type=transaction_type,
                    transaction_date=transaction_date,
                    description=description,
                    invoice=invoice,
                    payee=payee,
                    category=category,
                    currency=currency,
                    amount_gross=amount,
                    vat=vat,
                )
