"""Views for the account_keeping app."""
import decimal
from datetime import date

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import connection
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.defaultfilters import date as date_filter
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import generic

from currency_history.models import Currency, CurrencyRateHistory
from dateutil import relativedelta

from . import forms
from . import models
from . import utils
from .freckle_api import get_unpaid_invoices_with_transactions
from .utils import get_date as d


DEPOSIT = models.Transaction.TRANSACTION_TYPES['deposit']
WITHDRAWAL = models.Transaction.TRANSACTION_TYPES['withdrawal']


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class AccountsViewMixin(object):
    """
    Mixin that collects all data to show all transactions for all accounts.

    """
    template_name = 'account_keeping/accounts_view.html'

    def get_context_data(self, **kwargs):
        ctx = super(AccountsViewMixin, self).get_context_data(**kwargs)
        accounts = models.Account.objects.filter(active=True)
        account_transactions = []
        totals = {
            'amount_net': 0,
            'amount_gross': 0,
            'expenses_net': 0,
            'expenses_gross': 0,
            'income_net': 0,
            'income_gross': 0,
        }
        base_currency = getattr(settings, 'BASE_CURRENCY', 'EUR')
        for account in accounts:
            rate = 1
            if not account.currency.iso_code == base_currency:
                rate = self.get_rate(account.currency)

            account_balance = account.get_balance(self.month)

            qs = self.get_transactions(account)

            amount_net_sum = qs.aggregate(
                Sum('value_net'))['value_net__sum'] or 0
            amount_gross_sum = qs.aggregate(
                Sum('value_gross'))['value_gross__sum'] or 0
            expenses_net_sum = qs.filter(
                transaction_type=WITHDRAWAL).aggregate(
                    Sum('amount_net'))['amount_net__sum'] or 0
            expenses_gross_sum = qs.filter(
                transaction_type=WITHDRAWAL).aggregate(
                    Sum('amount_gross'))['amount_gross__sum'] or 0
            income_net_sum = qs.filter(transaction_type=DEPOSIT).aggregate(
                Sum('amount_net'))['amount_net__sum'] or 0
            income_gross_sum = qs.filter(transaction_type=DEPOSIT).aggregate(
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

        # We want to show a table: For each currency, show outstanding
        # income and expenses and profit. We also want a Total column. Of
        # course we need to convert all currency values to a base currency so
        # that we can create a sum for the total column.
        qs = self.get_outstanding_invoices()
        outstanding_expenses_gross_total_base = 0
        outstanding_income_gross_total_base = 0
        outstanding_profit_gross_total_base = 0
        outstanding_ccy_totals = {}
        for currency in Currency.objects.all():
            rate = 1
            if not currency.iso_code == base_currency:
                rate = self.get_rate(currency)
            outstanding_expenses_gross_sum = qs.filter(
                invoice_type=WITHDRAWAL, currency=currency).aggregate(
                    Sum('amount_gross'))['amount_gross__sum'] or 0
            outstanding_expenses_gross_sum_base = \
                outstanding_expenses_gross_sum * rate
            outstanding_expenses_gross_total_base += \
                outstanding_expenses_gross_sum_base

            outstanding_income_gross_sum = qs.filter(
                invoice_type=DEPOSIT, currency=currency).aggregate(
                    Sum('amount_gross'))['amount_gross__sum'] or 0
            outstanding_income_gross_sum_base = \
                outstanding_income_gross_sum * rate
            outstanding_income_gross_total_base += \
                outstanding_income_gross_sum_base

            outstanding_profit_gross_sum = \
                outstanding_income_gross_sum \
                - outstanding_expenses_gross_sum
            outstanding_profit_gross_sum_base = \
                outstanding_income_gross_sum_base \
                - outstanding_expenses_gross_sum_base
            outstanding_profit_gross_total_base += \
                outstanding_profit_gross_sum_base

            outstanding_ccy_totals[currency] = {
                'expenses_gross': outstanding_expenses_gross_sum,
                'expenses_gross_base': outstanding_expenses_gross_sum_base,
                'income_gross': outstanding_income_gross_sum,
                'income_gross_base': outstanding_income_gross_sum_base,
                'profit_gross': outstanding_profit_gross_sum,
                'profit_gross_base': outstanding_profit_gross_sum_base,
            }

        totals['outstanding_expenses_gross'] = \
            outstanding_expenses_gross_total_base
        totals['outstanding_income_gross'] = \
            outstanding_income_gross_total_base
        totals['outstanding_profit_gross'] = \
            outstanding_profit_gross_total_base

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


class AllTimeView(AccountsViewMixin, generic.TemplateView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.month = date(date.today().year, date.today().month, 1)
        return super(AllTimeView, self).dispatch(request, *args, **kwargs)

    def get_view_name(self):
        return 'All Time Overview'

    def get_outstanding_invoices(self):
        return models.Invoice.objects.filter(
            payment_date__isnull=True
        )

    def get_rate(self, currency):
        return decimal.Decimal(CurrencyRateHistory.objects.filter(
            rate__from_currency=currency,
            rate__to_currency__iso_code=getattr(
                settings, 'BASE_CURRENCY', 'EUR'),
        )[0].value)

    def get_transactions(self, account):
        return models.Transaction.objects.filter(
            account=account,
            parent__isnull=True,
        )


class CurrentMonthRedirectView(generic.View):
    """Redirects to the ``MonthOverviewView`` for the current month."""
    def dispatch(self, request, *args, **kwargs):
        now_ = now()
        return redirect(
            'account_keeping_month', year=now_.year, month=now_.month)


class CurrentYearRedirectView(generic.View):
    """Redirects to the ``MonthView`` for the current year."""
    def dispatch(self, request, *args, **kwargs):
        now_ = now()
        return redirect('account_keeping_year', year=now_.year)


class IndexView(LoginRequiredMixin, generic.TemplateView):
    """View that shows the main menu for the accounting app."""
    template_name = 'account_keeping/index_view.html'

    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)
        ctx.update({
            'invoices_without_pdf': models.Invoice.objects.get_without_pdf(),
            'transactions_without_invoice':
                models.Transaction.objects.get_without_invoice(),
            'transaction_types': models.Transaction.TRANSACTION_TYPES,
            'unpaid_invoices_with_transactions':
                get_unpaid_invoices_with_transactions(),
        })
        return ctx


class MonthView(AccountsViewMixin, generic.TemplateView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.month = date(int(kwargs.get('year')), int(kwargs.get('month')), 1)
        return super(MonthView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(MonthView, self).get_context_data(**kwargs)
        last_month = \
            self.month - relativedelta.relativedelta(months=1)
        next_month = \
            self.month + relativedelta.relativedelta(months=1)
        if next_month > date.today():
            next_month = None

        ctx.update({
            'month': self.month,
            'last_month': last_month,
            'next_month': next_month,
        })
        return ctx

    def get_view_name(self):
        return date_filter(self.month, 'F Y')

    def get_outstanding_invoices(self):
        next_month = self.month + relativedelta.relativedelta(months=1)
        return models.Invoice.objects.filter(
            Q(invoice_date__lt=next_month),
            Q(payment_date__isnull=True) | Q(payment_date__gte=next_month),
        ).prefetch_related('transactions')

    def get_rate(self, currency):
        rates = CurrencyRateHistory.objects.filter(
            rate__from_currency=currency,
            rate__to_currency__iso_code=getattr(
                settings, 'BASE_CURRENCY', 'EUR'),
        )
        try:
            return decimal.Decimal(rates.filter(
                date__year=self.month.year,
                date__month=self.month.month,
            )[0].value)
        except IndexError:
            # Get latest rate history record
            return decimal.Decimal(rates[0].value)

    def get_transactions(self, account):
        return models.Transaction.objects.filter(
            account=account,
            parent__isnull=True,
            transaction_date__year=self.month.year,
            transaction_date__month=self.month.month,
        )


class YearOverviewView(generic.TemplateView):
    template_name = 'account_keeping/year_view.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.year = int(kwargs.get('year'))
        return super(YearOverviewView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(YearOverviewView, self).get_context_data(**kwargs)
        past_months_of_year = utils.get_months_of_year(self.year)
        last_year = self.year - 1
        next_year = self.year + 1
        if next_year > date.today().year:
            next_year = None

        truncate_date = connection.ops.date_trunc_sql(
            'month', 'transaction_date')

        qs_year = models.Transaction.objects.filter(
            parent__isnull=True, transaction_date__year=self.year).extra(
                {'month': truncate_date})

        qs_income = qs_year.filter(
            transaction_type=DEPOSIT).values(
                'month', 'currency').annotate(
                    Sum('amount_gross')).order_by('currency', 'month')

        months = []
        for i in range(1, 13):
            months.append(date(self.year, i, 1))

        month_rates = {}
        base_currency = getattr(settings, 'BASE_CURRENCY', 'EUR')
        for month in months:
            for currency in Currency.objects.all():
                rate = 1
                if not currency.iso_code == base_currency:
                    rates = CurrencyRateHistory.objects.filter(
                        rate__from_currency=currency,
                        rate__to_currency__iso_code=base_currency,
                    )
                    try:
                        rate = decimal.Decimal(rates.filter(
                            date__year=month.year,
                            date__month=month.month,
                        )[0].value)
                    except IndexError:
                        # Get latest rate history record
                        rate = decimal.Decimal(rates[0].value)
                if month not in month_rates:
                    month_rates[month] = {}
                month_rates[month][currency.pk] = decimal.Decimal(rate)

        for row in qs_income:
            row['month'] = d(row['month']).date()
            row['amount_gross__sum'] = \
                row['amount_gross__sum'] \
                * month_rates[row['month']][row['currency']]

        income_total = {}
        for row in qs_income:
            if row['month'] not in income_total:
                income_total[row['month']] = 0
            income_total[row['month']] += row['amount_gross__sum']

        qs_expenses = qs_year.filter(
            transaction_type=WITHDRAWAL).values(
                'month', 'currency').annotate(
                    Sum('amount_gross')).order_by('currency', 'month')

        for row in qs_expenses:
            row['month'] = d(row['month']).date()
            row['amount_gross__sum'] = \
                row['amount_gross__sum'] \
                * month_rates[row['month']][row['currency']]

        expenses_total = {}
        for row in qs_expenses:
            if row['month'] not in expenses_total:
                expenses_total[row['month']] = 0
            expenses_total[row['month']] += row['amount_gross__sum']

        profit_total = {}
        for month in months:
            try:
                profit_total[month] = \
                    income_total[month] - expenses_total[month]
            except KeyError:
                pass

        # This adds a new column to the query which only holds the month
        # of the invoice_date and payment_date
        truncate_invoice_date = connection.ops.date_trunc_sql(
            'month', 'invoice_date')
        truncate_transaction_date = connection.ops.date_trunc_sql(
            'month', 'transaction_date')
        truncate_payment_date = connection.ops.date_trunc_sql(
            'payment_month', 'payment_date')
        qs_invoices_year = models.Invoice.objects.filter(
            invoice_date__year=self.year).extra({
                'month': truncate_invoice_date,
                'payment_month': truncate_payment_date})

        qs_new = qs_invoices_year.filter(invoice_type=DEPOSIT)
        qs_new = qs_new.values('month', 'currency')
        qs_new = qs_new.annotate(Sum('value_gross'))
        qs_new = qs_new.order_by('currency', 'month')

        for row in qs_new:
            row['month'] = d(row['month']).date()
            row['value_gross__sum'] = \
                row['value_gross__sum'] \
                * month_rates[row['month']][row['currency']]

        new_total = {}
        for row in qs_new:
            if row['month'] not in new_total:
                new_total[row['month']] = 0
            new_total[row['month']] += row['value_gross__sum']
        for month in months:
            if month not in new_total:
                new_total[month] = 0

        outstanding_total = {}
        for month in months:
            # for each month, we want to Sum the invoices, that were still
            # outstanding as of that month. An invoice sent in February and
            # paid in May would appear as outstanding on the months February,
            # March, April.
            if month.month > past_months_of_year:
                # In the current year, we don't want to save values for future
                # months
                break

            next_month = month + relativedelta.relativedelta(months=1)

            # TODO: Centralise this, we have this select in
            # get_outstanding_invoices already
            invoices = models.Invoice.objects.filter(
                Q(invoice_date__lt=next_month),
                Q(payment_date__isnull=True) | Q(payment_date__gte=next_month))
            invoices = invoices.prefetch_related('transactions')
            invoices = invoices.extra({'month': truncate_invoice_date, })
            invoices = invoices.values('currency')
            qs = invoices.annotate(value_sum=Sum('value_gross'))
            qs_outstanding_month = qs.order_by('currency')

            for row in qs_outstanding_month:
                row['value_sum'] = row['value_sum'] * month_rates[month][
                    row['currency']]
                try:
                    outstanding_total[month] += row['value_sum']
                except KeyError:
                    outstanding_total[month] = row['value_sum']

        partial_payments_total = {}
        for month in months:
            if month.month > past_months_of_year:
                # In the current year, we don't want to save values for future
                # months
                break

            next_month = month + relativedelta.relativedelta(months=1)

            txns = models.Transaction.objects.filter(
                invoice__invoice_date__lt=next_month,
                transaction_date__lt=next_month,
                invoice__payment_date__isnull=True)
            txns = txns.extra({'month': truncate_transaction_date, })
            txns = txns.values('currency')
            qs = txns.annotate(value_sum=Sum('value_gross'))
            qs_partial_payments_month = qs.order_by('currency')

            for row in qs_partial_payments_month:
                row['value_sum'] = row['value_sum'] * month_rates[month][
                    row['currency']]
                try:
                    partial_payments_total[month] += row['value_sum']
                except KeyError:
                    partial_payments_total[month] = row['value_sum']
            if partial_payments_total.get(month):
                try:
                    outstanding_total[month] -= partial_payments_total[month]
                except KeyError:
                    outstanding_total[month] = \
                        0 - partial_payments_total[month]

        balance_total = {}
        for month in months:
            if month.month > past_months_of_year:
                # In the current year, we don't want to save values for future
                # months
                break

            month_end = month + relativedelta.relativedelta(
                months=1, seconds=-1)
            for account in models.Account.objects.filter(active=True):
                qs_balance = models.Transaction.objects.filter(
                    account=account,
                    parent__isnull=True,
                    transaction_date__lte=month_end,
                ).aggregate(Sum('value_gross'))
                try:
                    qs_balance['value_gross__sum'] += account.initial_amount
                except TypeError:
                    # happens when there are no Transactions for that month
                    qs_balance['value_gross__sum'] = 0
                    qs_balance['value_gross__sum'] += account.initial_amount
                if not account.currency.iso_code == base_currency:
                    qs_balance['value_gross__sum'] = \
                        qs_balance['value_gross__sum'] \
                        * month_rates[month][account.currency.pk]
                if month not in balance_total:
                    balance_total[month] = 0
                balance_total[month] += qs_balance['value_gross__sum']

        equity_total = {}
        income_total_total = 0
        for month in months:
            try:
                equity_total[month] = \
                    balance_total[month] + outstanding_total[month]
            except KeyError:
                break

        for month in months:
            try:
                income_total_total += income_total[month]
            except KeyError:
                break
        income_average = income_total_total / past_months_of_year

        expenses_total_total = 0
        for month in months:
            try:
                expenses_total_total += expenses_total[month]
            except KeyError:
                break
        expenses_average = expenses_total_total / past_months_of_year

        profit_total_total = 0
        for month in months:
            try:
                profit_total_total += profit_total[month]
            except KeyError:
                break
        profit_average = profit_total_total / past_months_of_year

        new_total_total = 0
        for month in months:
            try:
                new_total_total += new_total[month]
            except KeyError:  # pragma: nocover
                break
        new_average = new_total_total / past_months_of_year

        outstanding_total_total = 0
        for month in months:
            try:
                outstanding_total_total += outstanding_total[month]
            except KeyError:
                break
        outstanding_average = outstanding_total_total / past_months_of_year

        balance_total_total = 0
        for month in months:
            try:
                balance_total_total += balance_total[month]
            except KeyError:
                break
        balance_average = balance_total_total / past_months_of_year

        equity_total_total = 0
        for month in months:
            try:
                equity_total_total += equity_total[month]
            except KeyError:
                break
        equity_average = equity_total_total / past_months_of_year

        ctx.update({
            'year': self.year,
            'last_year': last_year,
            'next_year': next_year,
            'months': months,
            'income_total': income_total,
            'expenses_total': expenses_total,
            'profit_total': profit_total,
            'new_total': new_total,
            'outstanding_total': outstanding_total,
            'balance_total': balance_total,
            'equity_total': equity_total,
            'income_total_total': income_total_total,
            'expenses_total_total': expenses_total_total,
            'profit_total_total': profit_total_total,
            'new_total_total': new_total_total,
            'income_average': income_average,
            'expenses_average': expenses_average,
            'profit_average': profit_average,
            'new_average': new_average,
            'outstanding_average': outstanding_average,
            'balance_average': balance_average,
            'equity_average': equity_average,
        })
        return ctx


class PayeeMixin(LoginRequiredMixin):
    model = models.Payee
    fields = '__all__'
    success_url = reverse_lazy('account_keeping_payees')


class PayeeListView(PayeeMixin, generic.ListView):
    pass


class PayeeCreateView(PayeeMixin, generic.CreateView):
    pass


class PayeeUpdateView(PayeeMixin, generic.UpdateView):
    pass


class AccountListView(LoginRequiredMixin, generic.ListView):
    model = models.Account


class InvoiceMixin(object):
    model = models.Invoice
    form_class = forms.InvoiceForm

    def get_success_url(self):
        return reverse('account_keeping_month', kwargs={
            'year': self.object.invoice_date.year,
            'month': self.object.invoice_date.month,
        })


class InvoiceCreateView(InvoiceMixin, LoginRequiredMixin, generic.CreateView):
    def get_form_kwargs(self):
        kwargs = super(InvoiceCreateView, self).get_form_kwargs()
        kwargs['initial'].update({
            'invoice_date': now(),
        })
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(InvoiceCreateView, self).get_context_data(**kwargs)
        ctx.update({
            'last_invoices': models.Invoice.objects.exclude(
                invoice_number__exact='').values_list(
                'invoice_number', flat=True)[:10],
        })
        return ctx


class InvoiceUpdateView(InvoiceMixin, LoginRequiredMixin, generic.UpdateView):
    pass


class TransactionMixin(object):
    model = models.Transaction
    form_class = forms.TransactionForm

    def get_success_url(self):
        return u'{}#{}'.format(reverse('account_keeping_month', kwargs={
            'year': self.object.transaction_date.year,
            'month': self.object.transaction_date.month,
        }), self.object.account.slug)


class TransactionCreateView(TransactionMixin, LoginRequiredMixin,
                            generic.CreateView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if self.request.GET.get('invoice'):
            self.initial.update({'invoice': self.request.GET['invoice']})
        if self.request.GET.get('parent'):
            self.initial.update({'parent': self.request.GET['parent']})
        return super(TransactionCreateView, self).dispatch(
            request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(TransactionCreateView, self).get_form_kwargs()
        kwargs['initial'].update({
            'transaction_date': now(),
        })
        return kwargs


class TransactionUpdateView(TransactionMixin, LoginRequiredMixin,
                            generic.UpdateView):
    pass


class TransactionExportView(LoginRequiredMixin, generic.FormView):
    """Creates a csv, which includes a specific set of transactions."""
    template_name = 'account_keeping/export.html'
    form_class = forms.ExportForm

    def get_form_kwargs(self):
        kwargs = super(TransactionExportView, self).get_form_kwargs()
        kwargs['initial'].update({
            'start': date(now().today().year - 1, 1, 1),
            'end': date(now().today().year - 1, 12, 31),
        })
        return kwargs

    def form_valid(self, form):
        dataset = models.TransactionResource().export(
            queryset=models.Transaction.objects.filter(
                transaction_date__gte=form.cleaned_data['start'],
                transaction_date__lte=form.cleaned_data['end'],
            ).order_by('-transaction_date', '-pk')
        )
        response = HttpResponse(dataset.xls, content_type="application/csv")
        response['Content-Disposition'] = \
            u'attachment; filename="{} {} - {}.xls"'.format(
                form.cleaned_data['account'].name,
                form.cleaned_data['start'],
                form.cleaned_data['end'])
        return response
