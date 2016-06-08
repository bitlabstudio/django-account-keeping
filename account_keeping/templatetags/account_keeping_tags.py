from django.conf import settings
from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.filter()
def currency(value, currency=None):
    try:
        currency = currency.code
    except AttributeError:
        currency = getattr(settings, 'BASE_CURRENCY', 'EUR')
    cleaned_value = '{0:.2f}'.format(float(value))
    return u'{0} {1}'.format(currency, intcomma(cleaned_value))
