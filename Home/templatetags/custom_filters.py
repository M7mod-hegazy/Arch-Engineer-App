from django import template
from django.conf import settings

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def add_css_version(value):
    try:
        return f"{value}?v={settings.CSS_VERSION}"
    except:
        return value

@register.filter
def replace(value, arg):
    """
    Replaces all occurrences of arg with a space in the given value
    """
    return value.replace(arg, " ")

@register.filter
def format_sort_label(value):
    """
    Formats sort_by value into readable text
    """
    if not value:
        return ""
    
    # Remove _asc or _desc
    text = value.replace('_asc', '').replace('_desc', '')
    # Replace underscores with spaces
    text = text.replace('_', ' ')
    # Capitalize words
    text = text.title()
    
    # Add order indicator
    if value.endswith('_desc'):
        text += ' (Descending)'
    elif value.endswith('_asc'):
        text += ' (Ascending)'
    
    return text
