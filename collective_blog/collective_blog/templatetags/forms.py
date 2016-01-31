"""Tags for rendering forms"""

from django.template import Library

register = Library()

@register.inclusion_tag('tags/form_field.html')
def form_field(field, css_class=''):
    return {
        'field': field,
        'css_class': css_class,
    }

@register.inclusion_tag('tags/form_errlist.html')
def form_errlist(form):
    return {
        'form': form,
    }
