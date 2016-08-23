from django.forms.widgets import Select
from django.utils.safestring import mark_safe


class LightSelect(Select):
    def render(self, *args, **kwargs):
        html = super(LightSelect, self).render(*args, **kwargs)
        html_wrap = '<span class="select-arrow">%s</span>' % html
        return mark_safe(html_wrap)
