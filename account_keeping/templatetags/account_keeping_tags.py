from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat

register = template.Library()


@register.filter()
def currency(value):
    return intcomma(floatformat(value, '-2'))
