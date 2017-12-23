import decimal

from django.conf import settings
from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


def format_number(num):
    dec = decimal.Decimal(num)
    tup = dec.as_tuple()
    delta = len(tup.digits) + tup.exponent
    digits = ''.join(str(d) for d in tup.digits)
    if delta <= 0:
        zeros = abs(tup.exponent) - len(tup.digits)
        val = '0.' + ('0' * zeros) + digits
    else:
        val = digits[:delta] + ('0' * tup.exponent) + '.' + digits[delta:]
    val = val.rstrip('0')
    if val[-1] == '.':
        val = val[:-1]
    if tup.sign:
        return '-' + val
    return val


@register.filter()
def currency(value, currency=None):
    try:
        currency = currency.iso_code
    except AttributeError:
        currency = getattr(settings, 'BASE_CURRENCY', 'EUR')
    return u'{0} {1}'.format(currency, intcomma(format_number(value)))
