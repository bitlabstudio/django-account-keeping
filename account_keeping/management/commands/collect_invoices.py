"""
Collects invoices for the given account and timeframe into a tarball.

"""
import datetime
import os
import shutil

from django.core.management.base import BaseCommand

from ... import models


class Command(BaseCommand):
    help = 'Copies invoices of transactions into a folder.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-o', '--output',
            dest='output',
            help='Output folder. Make sure that the folder exists.',
        )
        parser.add_argument(
            '-a', '--account',
            dest='account',
            help='Account slug of the account that should be handled.',
        )
        parser.add_argument(
            '-s', '--start',
            dest='start_date',
            help='Start date. Include all transactions from this date.',
        )
        parser.add_argument(
            '-e', '--end',
            dest='end_date',
            help='End date. Include all transactions up to this date.',
        )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.counter = 1

    def copy_file(self, transaction):
        if transaction.invoice and transaction.invoice.pdf:  # pragma: nocover
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
