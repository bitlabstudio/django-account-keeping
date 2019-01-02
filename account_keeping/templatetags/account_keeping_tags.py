import decimal

from django.conf import settings
from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

from ..models import Branch


register = template.Library()


@register.simple_tag
def get_branches():
    return Branch.objects.all()


@register.filter
def currency(value, currency=None):
    try:
        currency = currency.iso_code
    except AttributeError:
        currency = getattr(settings, 'BASE_CURRENCY', 'EUR')

    dec = decimal.Decimal(value)
    tup = dec.as_tuple()
    delta = len(tup.digits) + tup.exponent
    digits = ''.join(str(d) for d in tup.digits)
    if delta <= 0:
        zeros = abs(tup.exponent) - len(tup.digits)
        value = '0.' + ('0' * zeros) + digits
    else:
        value = digits[:delta] + ('0' * tup.exponent) + '.' + digits[delta:]
    value = value.rstrip('0')
    if value[-1] == '.':
        value = value[:-1]
    if not currency or currency != 'BTC':
        value = '{0:.2f}'.format(float(value))
    if tup.sign:
        value = '-' + value

    return u'{0} {1}'.format(currency, intcomma(value))
