from django import template

register = template.Library()

# template tag to get the class name of the object in the html
@register.filter(name='classname')
def classname(obj):
    return obj.__class__.__name__
