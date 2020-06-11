from django import template
register = template.Library()

@register.simple_tag
def define(val=None):
  return "?page=" + val
  
@register.simple_tag
def define_list(val=None):
    
  listArr = []
  listArr.append({"page" : val,"how" : 0})

  return listArr