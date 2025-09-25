from django import template

register = template.Library()

@register.filter
def format_money(value):
    try:
        return "{:,.0f}".format(float(value))
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