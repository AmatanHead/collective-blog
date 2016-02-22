from django.forms.forms import BaseForm
from django.utils.html import conditional_escape
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


class BaseFormRenderer(BaseForm):
    def _render_group(self, group):
        if len(group) > 3:
            raise AssertionError('group \'%s\' is too long' % repr(group))
        elif len(group) == 3:
            cols = 'one-third'
        elif len(group) == 2:
            cols = 'one-half'
        else:
            raise AssertionError('group \'%s\' is too short' % repr(group))

        html_output = '<div class="row">'

        for field in group:
            html_output += '<div class="%s column">' % cols
            html_output += self._render_field(field)
            html_output += '</div>'

        html_output += '</div>'

        return html_output

    def _render_field(self, field):
        if field not in self.fields:
            raise IndexError('unknown field %s' % field)

        bf = self[field]

        errors = self.error_class(
            [conditional_escape(error) for error in bf.errors])

        if bf.css_classes():
            css_classes = ' class="%s"' % bf.css_classes()
        else:
            css_classes = ''

        if bf.label:
            label = conditional_escape(force_text(bf.label))
            label = bf.label_tag(label) or ''
        else:
            label = ''

        if bf.help_text:
            help_text = '<div class="desc">%s</div>' % force_text(bf.help_text)
        else:
            help_text = ''

        if bf.is_hidden and not errors:
            hidden = ' style="display: none;"'
        else:
            hidden = ''

        return ('<section%(hidden)s%(css_classes)s>'
                '    %(label)s %(field)s'
                '    %(help_text)s'
                '    %(errors)s'
                '</section>' % {
                    'hidden': hidden,
                    'css_classes': css_classes,
                    'label': label,
                    'help_text': help_text,
                    'errors': errors,
                    'field': str(bf),
                })

    def as_section(self):
        """Returns this form rendered as HTML <section>s."""

        renderer = getattr(self, 'renderer', [])

        served_fields = set()

        if self.non_field_errors():
            html_output = '<section class="separate">%s</section>' % force_text(self.non_field_errors())
        else:
            html_output = ''

        for field in renderer:
            if isinstance(field, (list, tuple)):
                served_fields |= set(field)
                html_output += self._render_group(field)
            else:
                served_fields.add(field)
                html_output += self._render_field(field)

        for field in self.fields.keys():
            if field not in served_fields:
                served_fields.add(field)
                html_output += self._render_field(field)

        return mark_safe(html_output)
