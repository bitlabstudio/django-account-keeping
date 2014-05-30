import locale

from django import template

locale.setlocale(locale.LC_ALL, '')
register = template.Library()


@register.filter()
def currency(value):
    return locale.currency(value, symbol=False, grouping=True)
