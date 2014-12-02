"""
Collects invoices for the given account and timeframe into a tarball.

"""
from optparse import make_option
import datetime
import os
import shutil

from django.core.management.base import BaseCommand

from account_keeping import models


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '-o', '--output',
            dest='output',
            help='Output folder. Make sure that the folder exists.'),
        make_option(
            '-a', '--account',
            dest='account',
            help='Account slug of the account that should be handled.'),
        make_option(
            '-s', '--start',
            dest='start_date',
            help='Start date. Include all transactions from this date.'),
        make_option(
            '-e', '--end',
            dest='end_date',
            help='End date. Include all transactions up to this date.'),
    )
    help = 'Copies invoices of transactions into a folder.'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.counter = 1

    def copy_file(self, transaction):
        if transaction.invoice and transaction.invoice.pdf:
            counter = str(self.counter).zfill(4)
            filename = '{0}.pdf'.format(counter)
            shutil.copy(
                transaction.invoice.pdf.file.name,
                os.path.join(self.output_folder, filename))
            self.counter += 1

    def handle(self, *args, **options):
        account = models.Account.objects.get(slug=options.get('account'))
        self.output_folder = options.get('output')
        start_date = datetime.datetime.strptime(
            options.get('start_date'), '%Y-%m-%d')
        end_date = datetime.datetime.strptime(
            options.get('end_date'), '%Y-%m-%d')
        transactions = models.Transaction.objects.filter(
            account=account,
            transaction_date__gte=start_date,
            transaction_date__lte=end_date,
        ).prefetch_related('children', ).order_by('-transaction_date')
        for transaction in transactions:
            if transaction.children.all():
                for child in transaction.children.all():
                    self.copy_file(child)
            else:
                self.copy_file(transaction)
