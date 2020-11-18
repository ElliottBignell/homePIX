from django import template

register = template.Library()

@register.simple_tag
def album_top( index, offset, height ):
    return offset + height * index