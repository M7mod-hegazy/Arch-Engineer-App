from django import template

register = template.Library()

@register.filter(name='addclasses')
def addclasses(value, arg):
    """
    Add custom CSS classes to a form field.
    """
    return value.widget.attrs.update({'class': arg})

@register.filter(name='add_css_classes')
def add_css_classes(value, arg):
    """
    Add custom CSS classes to a string.
    """
    return f'{value} {arg}'
