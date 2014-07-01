import locale

from django import template
from django.utils.timezone import datetime

locale.setlocale(locale.LC_ALL, '')
register = template.Library()


@register.filter()
def currency(value):
    return locale.currency(value, symbol=False, grouping=True)


@register.assignment_tag()
def get_current_year():
    return datetime.now().year


@register.assignment_tag()
def get_current_month():
    return datetime.now().month
