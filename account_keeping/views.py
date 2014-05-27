"""Views for the account_keeping app."""
from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from . import models


class MonthView(TemplateView):
    template_name = 'account_keeping/month_view.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.month = date(int(kwargs.get('year')), int(kwargs.get('month')), 1)
        return super(MonthView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(MonthView, self).get_context_data(**kwargs)
        accounts = models.Account.objects.all()
        account_transactions = []
        for account in accounts:
            qs = models.Transaction.objects.filter(
                account=account,
                parent__isnull=True,
                transaction_date__year=self.month.year,
                transaction_date__month=self.month.month,
            )
            amount_net_sum = qs.aggregate(
                Sum('value_net'))['value_net__sum']
            amount_gross_sum = qs.aggregate(
                Sum('value_gross'))['value_gross__sum']
            expenses_net_sum = qs.filter(transaction_type="D").aggregate(
                Sum('amount_net'))['amount_net__sum']
            expenses_gross_sum = qs.filter(transaction_type="D").aggregate(
                Sum('amount_gross'))['amount_gross__sum']
            income_net_sum = qs.filter(transaction_type="C").aggregate(
                Sum('amount_net'))['amount_net__sum']
            income_gross_sum = qs.filter(transaction_type="C").aggregate(
                Sum('amount_gross'))['amount_gross__sum']

            account_transactions.append({
                'account': account,
                'transactions': qs,
                'amount_net_total': amount_net_sum,
                'amount_gross_total': amount_gross_sum,
                'expenses_net_total': expenses_net_sum,
                'expenses_gross_total': expenses_gross_sum,
                'income_net_total': income_net_sum,
                'income_gross_total': income_gross_sum,
            })
        ctx.update({
            'month': self.month,
            'account_transactions': account_transactions,
        })
        return ctx
