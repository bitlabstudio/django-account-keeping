import locale
from datetime import date

from django import template

locale.setlocale(locale.LC_ALL, '')
register = template.Library()


@register.filter()
def currency(value):
    return locale.currency(value, symbol=False, grouping=True)


@register.assignment_tag()
def get_current_year():
    return date.today().year


@register.assignment_tag()
def get_current_month():
    return date.today().month
