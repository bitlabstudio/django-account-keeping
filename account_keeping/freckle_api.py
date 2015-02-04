"""API calls against letsfreckle.com"""
from django.conf import settings

from freckle_client.client import FreckleClientV2

from . import models


client = FreckleClientV2(settings.ACCOUNT_KEEPING_FRECKLE_ACCESS_TOKEN)


def get_unpaid_invoices_with_transactions():
    """
    Returns all invoices that are unpaid on freckle but have transactions.

    This means, that the invoice is either partially paid and can be left as
    unpaid in freckle, or the invoice has been fully paid and should be set to
    paid in freckle as well.

    """
    result = []
    unpaid_invoices = client.fetch_json(
        'invoices', query_params={'state': 'unpaid'})
    for invoice in unpaid_invoices:
        invoice_with_transactions = models.Invoice.objects.filter(
            invoice_number=invoice['number'], transactions__isnull=False)
        if invoice_with_transactions:
            result.append(invoice)
    return result
