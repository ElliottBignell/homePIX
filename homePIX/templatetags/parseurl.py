from django import template
import re

register = template.Library()

@register.filter
def current_content( url, page ):

    paths = re.match( r"/([^/]+)/.*", url )

    if paths:
        if paths[ 1 ] == page:
            return "--homepix-bg"

    return "--homepix-dark"

@register.filter
def current_background( url, page ):

    paths = re.match( r"/([^/]+)/.*", url )

    if paths:
        if paths[ 1 ] == page:
            return "--homepix-dark"

    return "--homepix-bg"
