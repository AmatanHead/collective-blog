"""Base form classes for rendering light-compatible html"""

from django.forms.forms import BaseForm
from django.utils.html import conditional_escape
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

import re


class BaseFormRenderer(BaseForm):
    """Mixin that provides functions for rendering light-compatible html"""

    def _render_group(self, group):
        """Render several fields at the same line

        Responsive grid is used.

        """
        if len(group) > 3:
            raise AssertionError('group \'%s\' is too long' % repr(group))
        elif len(group) == 3:
            cols = 'one-third'
            offset_classes = ['',
                              ' offset-by-one-third',
                              ' offset-by-two-thirds']
        elif len(group) == 2:
            cols = 'one-half'
            offset_classes = ['',
                              ' offset-by-one-half']
        else:
            raise AssertionError('group \'%s\' is too short' % repr(group))

        html_output = '<div class="row">'

        offset = 0

        for field in group:
            if field is None:
                offset += 1
            else:
                offset_class = offset_classes[offset]
                offset = 0
                html_output += '<div class="%s column%s">' % (
                    cols, offset_class)
                html_output += self._render_field(field)
                html_output += '</div>'

        html_output += '</div>'

        return html_output

    # Matches `renderer` elements that will expand to <hr>s
    _separator = re.compile(r'-+')

    def _render_field(self, field):
        """Render a <section> with a single field"""
        if field is None:
            return '<section>&nbsp;</section>'
        elif self._separator.match(field):
            return '<hr>'
        elif field not in self.fields:
            raise IndexError('unknown field %s' % field)

        field = self[field]

        errors = self.error_class(
            [conditional_escape(error) for error in field.errors])

        classes = field.css_classes().split()

        if (field.field.required and
                not getattr(self, 'ignore_required_style', None)):
            classes.append('required')

        if classes:
            css_classes = ' class="%s"' % ' '.join(classes)
        else:
            css_classes = ''

        if field.label:
            label = conditional_escape(force_text(field.label))
            label = field.label_tag(label) or ''
        else:
            label = ''

        if field.help_text:
            help_text = '<div class="desc">%s</div>' % force_text(field.help_text)
        else:
            help_text = ''

        if field.is_hidden and not errors:
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
                    'field': str(field),
                })

    def as_section(self):
        """Returns this form rendered as HTML <section>s

        Uou can set up `renderer` array in your class.
        This array should contain a list of field names.

        If such one is specified, this function will first render that fields.

        Each element of the `renderer` list can be:
        * A string of hyphens (e.g. '-----')
          will render the `<hr>` tag.
        * A name of a field will render that field.
        * A tuple of two or three field names will render that fields
          in a single row (using flexible grid).
        * A `None` object will render an empty `<section>`.

        """

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
