from django.forms.utils import flatatt
from django.forms.widgets import Select
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class LightSelect(Select):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [format_html('<span class="select-arrow"><select{}>', flatatt(final_attrs))]
        options = self.render_options(choices, [value])
        if options:
            output.append(options)
        output.append('</select></span>')
        return mark_safe('\n'.join(output))
