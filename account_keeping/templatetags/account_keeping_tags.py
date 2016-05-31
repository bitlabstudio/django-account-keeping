from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat
from django.utils.timezone import datetime

register = template.Library()


@register.filter()
def currency(value):
    return intcomma(floatformat(value, '-2'))


@register.assignment_tag()
def get_current_year():
    return datetime.now().year


@register.assignment_tag()
def get_current_month():
    return datetime.now().month
