from django import template
from django.utils.safestring import mark_safe

register = template.Library()



@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})



@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='add_checked_attribute')
def add_checked_attribute(widget):
    return mark_safe(widget.replace('>', ' checked>'))