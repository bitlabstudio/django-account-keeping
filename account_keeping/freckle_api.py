"""API calls against letsfreckle.com"""
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

try:
    from freckle_client.client import FreckleClientV2
    client = FreckleClientV2(settings.ACCOUNT_KEEPING_FRECKLE_ACCESS_TOKEN)
except ImportError:  # pragma: nocover
    client = None
from requests.exceptions import ConnectionError, HTTPError

from . import models


def get_unpaid_invoices_with_transactions():
    """
    Returns all invoices that are unpaid on freckle but have transactions.

    This means, that the invoice is either partially paid and can be left as
    unpaid in freckle, or the invoice has been fully paid and should be set to
    paid in freckle as well.

    """
    if not client:  # pragma: nocover
        return None
    result = {}
    try:
        unpaid_invoices = client.fetch_json(
            'invoices', query_params={'state': 'unpaid'})
    except (ConnectionError, HTTPError):  # pragma: nocover
        result.update({'error': _('Wasn\'t able to connect to Freckle.')})
    else:
        invoices = []
        for invoice in unpaid_invoices:
            invoice_with_transactions = models.Invoice.objects.filter(
                invoice_number=invoice['reference'],
                transactions__isnull=False)
            if invoice_with_transactions:
                invoices.append(invoice)
        result.update({'invoices': invoices})
    return result
