"""Views for the account_keeping app."""
from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.template.defaultfilters import date as date_filter
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from . import models


class AccountsViewMixin(object):
    """
    Mixin that collects all data to show all transactions for all accounts.

    """
    template_name = 'account_keeping/accounts_view.html'

    def get_account_balance(self, account):
        """
        Returns the balance up until the last transaction BEFORE this view.

        """
        raise NotImplementedError('Method not implemented')  # pragma: no cover

    def get_context_data(self, **kwargs):
        ctx = super(AccountsViewMixin, self).get_context_data(**kwargs)
        accounts = models.Account.objects.all()
        account_transactions = []
        totals = {
            'amount_net': 0,
            'amount_gross': 0,
            'expenses_net': 0,
            'expenses_gross': 0,
            'income_net': 0,
            'income_gross': 0,
        }
        base_currency = models.Currency.objects.get(is_base_currency=True)
        for account in accounts:
            rate = 1
            if not account.currency.is_base_currency:
                rate = self.get_rate(account.currency)

            account_balance = self.get_account_balance(account)

            qs = self.get_transactions(account)

            deposit = models.Transaction.TRANSACTION_TYPES['deposit']
            withdrawal = models.Transaction.TRANSACTION_TYPES['withdrawal']

            amount_net_sum = qs.aggregate(
                Sum('value_net'))['value_net__sum'] or 0
            amount_gross_sum = qs.aggregate(
                Sum('value_gross'))['value_gross__sum'] or 0
            expenses_net_sum = qs.filter(
                transaction_type=withdrawal).aggregate(
                    Sum('amount_net'))['amount_net__sum'] or 0
            expenses_gross_sum = qs.filter(
                transaction_type=withdrawal).aggregate(
                    Sum('amount_gross'))['amount_gross__sum'] or 0
            income_net_sum = qs.filter(transaction_type=deposit).aggregate(
                Sum('amount_net'))['amount_net__sum'] or 0
            income_gross_sum = qs.filter(transaction_type=deposit).aggregate(
                Sum('amount_gross'))['amount_gross__sum'] or 0

            amount_net_sum_base = amount_net_sum * rate
            amount_gross_sum_base = amount_gross_sum * rate
            expenses_net_sum_base = expenses_net_sum * rate
            expenses_gross_sum_base = expenses_gross_sum * rate
            income_net_sum_base = income_net_sum * rate
            income_gross_sum_base = income_gross_sum * rate

            totals['amount_net'] += amount_net_sum_base
            totals['amount_gross'] += amount_gross_sum_base
            totals['expenses_net'] += expenses_net_sum_base
            totals['expenses_gross'] += expenses_gross_sum_base
            totals['income_net'] += income_net_sum_base
            totals['income_gross'] += income_gross_sum_base

            account_transactions.append({
                'account': account,
                'account_balance': account_balance,
                'transactions': qs,
                'amount_net_total': amount_net_sum,
                'amount_gross_total': amount_gross_sum,
                'expenses_net_total': expenses_net_sum,
                'expenses_gross_total': expenses_gross_sum,
                'income_net_total': income_net_sum,
                'income_gross_total': income_gross_sum,
                'amount_net_sum_base': amount_net_sum_base,
                'amount_gross_sum_base': amount_gross_sum_base,
                'expenses_net_sum_base': expenses_net_sum_base,
                'expenses_gross_sum_base': expenses_gross_sum_base,
                'income_net_sum_base': income_net_sum_base,
                'income_gross_sum_base': income_gross_sum_base,
            })

        qs = self.get_outstanding_invoices()
        outstanding_expenses_gross_sum_base = 0
        outstanding_income_gross_sum_base = 0
        outstanding_amount_gross_sum_base = 0
        outstanding_ccy_totals = {}
        for currency in models.Currency.objects.all():
            rate = 1
            if not currency.is_base_currency:
                rate = self.get_rate(currency)
            outstanding_expenses_gross_sum = qs.filter(
                invoice_type=withdrawal, currency=currency).aggregate(
                    Sum('amount_gross'))['amount_gross__sum'] or 0
            outstanding_expenses_gross_sum_base += \
                outstanding_expenses_gross_sum * rate

            outstanding_income_gross_sum = qs.filter(
                invoice_type=deposit, currency=currency).aggregate(
                    Sum('amount_gross'))['amount_gross__sum'] or 0
            outstanding_income_gross_sum_base += \
                outstanding_income_gross_sum * rate

            outstanding_amount_gross_sum_base = \
                outstanding_income_gross_sum - outstanding_expenses_gross_sum

            outstanding_ccy_totals[currency] = {
                'expenses_gross': outstanding_expenses_gross_sum_base,
                'income_gross': outstanding_income_gross_sum_base,
                'amount_gross': outstanding_amount_gross_sum_base,
            }

        totals['outstanding_expenses_gross'] = \
            outstanding_expenses_gross_sum_base
        totals['outstanding_income_gross'] = outstanding_income_gross_sum_base
        totals['outstanding_amount_gross'] = outstanding_amount_gross_sum_base

        ctx.update({
            'view_name': self.get_view_name(),
            'transaction_types': models.Transaction.TRANSACTION_TYPES,
            'base_currency': base_currency,
            'totals': totals,
            'account_transactions': account_transactions,
            'outstanding_invoices': qs,
            'outstanding_ccy_totals': outstanding_ccy_totals,
        })
        return ctx

    def get_view_name(self):
        """
        Return the name of the view that is displayed in the main h1-tag.

        """
        raise NotImplementedError('Method not implemented')  # pragma: no cover

    def get_outstanding_invoices(self):
        """
        Returns the transactions that should be shown in this view.

        """
        raise NotImplementedError('Method not implemented')  # pragma: no cover

    def get_rate(self, currency):
        """
        Returns the conversion rate.

        For month views, it should use a ConversionRate object and a filter
        on the given month.

        For other views, I'm not sure what to use.

        """
        raise NotImplementedError('Method not implemented')  # pragma: no cover

    def get_transactions(self, account):
        """
        Returns the transactions that should be shown in this view.

        """
        raise NotImplementedError('Method not implemented')  # pragma: no cover


class MonthView(AccountsViewMixin, TemplateView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.month = date(int(kwargs.get('year')), int(kwargs.get('month')), 1)
        return super(MonthView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(MonthView, self).get_context_data(**kwargs)
        ctx.update({
            'month': self.month,
        })
        return ctx

    def get_account_balance(self, account):
        account_balance = models.Transaction.objects.filter(
            account=account,
            parent__isnull=True,
            transaction_date__lt=self.month,
        ).aggregate(Sum('value_gross'))['value_gross__sum'] or 0
        account_balance = account_balance + account.initial_amount
        return account_balance

    def get_view_name(self):
        return date_filter(self.month, 'F Y')

    def get_outstanding_invoices(self):
        next_month = date(self.month.year, self.month.month + 1, 1)
        return models.Invoice.objects.filter(
            Q(invoice_date__lte=self.month),
            Q(payment_date__isnull=True) | Q(payment_date__gte=next_month),
        )

    def get_rate(self, currency):
        return models.CurrencyRate.objects.get(
            year=self.month.year, month=self.month.month,
            currency=currency,
        ).rate

    def get_transactions(self, account):
        return models.Transaction.objects.filter(
            account=account,
            parent__isnull=True,
            transaction_date__year=self.month.year,
            transaction_date__month=self.month.month,
        )


class AllTimeView(AccountsViewMixin, TemplateView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AllTimeView, self).dispatch(request, *args, **kwargs)

    def get_account_balance(self, account):
        return account.initial_amount

    def get_view_name(self):
        return 'All Time Overview'

    def get_outstanding_invoices(self):
        return models.Invoice.objects.filter(
            payment_date__isnull=True
        )

    def get_rate(self, currency):
        return models.CurrencyRate.objects.filter(
            currency=currency).order_by('-year', '-month')[:1][0].rate

    def get_transactions(self, account):
        return models.Transaction.objects.filter(
            account=account,
            parent__isnull=True,
        )
