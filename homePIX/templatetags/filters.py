from django import template
import calendar
from pprint import pprint

register = template.Library()

def next(some_list, current_index):
    """
    Returns the next element of the list using the current index if it exists.
    Otherwise returns an empty string.
    """
    try:
        return some_list[int(current_index) + 1] # access the next element
    except:
        return '' # return empty string in case of exception

def previous(some_list, current_index):
    """
    Returns the previous element of the list using the current index if it exists.
    Otherwise returns an empty string.
    """
    try:
        return some_list[int(current_index) - 1] # access the previous element
    except:
        return '' # return empty string in case of exception

register.filter( 'previous', previous )
register.filter( 'next', next )

@register.filter
def index(indexable, i):
    return indexable[i]

@register.filter
def month_name(month_number):
    return calendar.month_name[month_number]

@register.filter
def month_abbr(month_number):
    return calendar.month_abbr[month_number]

@register.filter
def month_number(month_nr):
    return "{:0>2d}".format( month_nr )

@register.simple_tag(takes_context=True)
def month_thumbnail( context, year, month ):

    idx = str( year ) + "-" + str( month - 1 )
    thumbnails = context[ 'thumbnails' ]

    if idx in thumbnails:
        return thumbnails[ idx ]
    else:
        return ''
