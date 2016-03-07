"""Form field for the markdown field

It is based on the `CharField`.
Unlike `CharField`, it works with `Markdown` objects.

"""

from django import forms
from django.core import exceptions

from .datatype import Markdown
from .renderer import BaseRenderer
from .widgets import MarkdownTextarea


class MarkdownFormField(forms.fields.CharField):
    # TODO tests

    def __init__(self, *args, **kwargs):
        """Form field for editing markdown objects"""
        source_validators = kwargs.pop('source_validators', [])
        _source_validators = kwargs.pop('_source_validators', [])
        html_validators = kwargs.pop('html_validators', [])
        _html_validators = kwargs.pop('_html_validators', [])
        validators = kwargs.pop('validators', [])
        _validators = kwargs.pop('_validators', [])

        self.validators = validators + _validators
        self.html_validators = html_validators + _html_validators
        self.source_validators = source_validators + _source_validators

        self.markdown_cls = kwargs.pop('markdown', Markdown)
        self.renderer = kwargs.pop('renderer', BaseRenderer())

        defaults = {'widget': MarkdownTextarea}
        defaults.update(kwargs)

        super(MarkdownFormField, self).__init__(*args, **defaults)

    def run_validator(self, validator, *args, **kwargs):
        """Runs a single validator on a value

        :param validator: A callable. The validator to run.
        :param args: Arguments for the validator
        :param kwargs: Keyword arguments for the validator
        :return: List of errors.

        """
        for validator in self.validators:
            try:
                validator(*args, **kwargs)
                return []
            except exceptions.ValidationError as e:
                if hasattr(e, 'code') and e.code in self.error_messages:
                    e.message = self.error_messages[e.code]
                return e.error_list

    def run_validators(self, value):
        """Run validators on the given value

        :param value: the `Markdown` class instance which needs validation.
        :return: None
        :raise: ValidationError

        """
        if value in self.empty_values:
            return

        errors = []

        for validator in iter(self.source_validators):
            errors.extend(self.run_validator(validator, [value.source]))

        for validator in iter(self.html_validators):
            errors.extend(self.run_validator(validator, [value.html]))

        for validator in iter(self.validators):
            errors.extend(self.run_validator(validator, [value]))

        if errors:
            raise exceptions.ValidationError(errors)

    def validate(self, value):
        """Run all source, html, and common validators

        :param value: `Markdown` class instance which needs to be validated.

        """
        if value in self.empty_values and self.required:
            raise exceptions.ValidationError(self.error_messages['required'], code='required')

    def to_python(self, value):
        """Text to python

        :param value: Source string, `Markdown`, or None.
        :return: None or `Markdown`.

        """
        if value in self.empty_values and value != '':
            return value
        elif isinstance(value, self.markdown_cls):
            return value
        else:
            return self.markdown_cls(self.renderer, value)

    def prepare_value(self, value):
        """Python to text

        :param value: A `Markdown` class instance.
        :return: Source text that will be displayed in a widget.

        """
        if isinstance(value, self.markdown_cls):
            return value.source
        else:
            return value
