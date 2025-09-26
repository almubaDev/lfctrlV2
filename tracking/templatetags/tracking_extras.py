from django import template

register = template.Library()

@register.filter
def absolute(value):
    """Retorna el valor absoluto de un número"""
    try:
        if value is None:
            return None
        return abs(float(value))
    except (ValueError, TypeError):
        return None

@register.filter
def format_number(value, decimals=1):
    """Formatea un número con la cantidad de decimales especificada"""
    try:
        if value is None:
            return "-"
        return f"{float(value):.{decimals}f}"
    except (ValueError, TypeError):
        return "-"

@register.simple_tag
def calculate_weight_change(current_weight, previous_weight):
    """
    Calcula el cambio de peso entre dos registros.
    Retorna (diferencia, símbolo de dirección)
    """
    if previous_weight is None or current_weight is None:
        return 0.0, None
        
    try:
        difference = float(current_weight) - float(previous_weight)
        if difference > 0:
            return abs(difference), '↑'
        elif difference < 0:
            return abs(difference), '↓'
        else:
            return 0.0, '='
    except (ValueError, TypeError):
        return 0.0, None

@register.filter
def subtract(value, arg):
    """Resta dos valores"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0