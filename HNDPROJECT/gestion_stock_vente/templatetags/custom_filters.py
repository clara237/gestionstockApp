from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary using a variable
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None