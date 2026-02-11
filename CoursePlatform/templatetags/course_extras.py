from django import template

register = template.Library()

@register.filter
def get_item(sequence, position):
    """
    Returns the item at the given position in the sequence.
    If the position is out of range, returns None.
    """
    try:
        return sequence[position]
    except (IndexError, TypeError, AttributeError):
        return None

@register.filter
def split(value, delimiter=','):
    """
    Splits the input string by the given delimiter.
    """
    if not value:
        return []
    return value.split(delimiter)
