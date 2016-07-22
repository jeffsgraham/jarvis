from django import template
register = template.Library()

#useful for retrieving dictionary values whose keys have spaces
@register.filter
def get(mapping, key):
    return mapping.get(key, '')
