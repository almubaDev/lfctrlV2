from django import template
from django.utils.formats import number_format

register = template.Library()

@register.filter
def format_money(value):
    try:
        formatted = number_format(value, decimal_pos=0, use_l10n=True)
        return formatted.replace(",", ".")
    except (ValueError, TypeError):
        return "0"

@register.filter
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)
