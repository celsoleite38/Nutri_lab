# alimentos/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def widthratio(value, max_value, max_width):
    """Calcula a porcentagem para a barra de progresso"""
    try:
        if float(max_value) == 0:
            return 0
        return (float(value) / float(max_value)) * float(max_width)
    except (ValueError, TypeError):
        return 0