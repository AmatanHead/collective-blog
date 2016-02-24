"""Markdown model fields"""

from django.db.models import TextField, NOT_PROVIDED
from django.core import exceptions
from django import forms

from .widgets import MarkdownTextarea
from .datatype import Markdown


class MarkdownField(TextField):
    def __init__(self, *args, markdown=Markdown, db_column=None, source_validators=None,
                 html_validators=None, common_validators=None,
                 **kwargs):
        """
        Database field for storing `Markdown` objects.

        This field forces the html update process while preparing for query.
        Therefore it is guaranteed that html stored in a database
        is always ut-to-date.

        Parameters:

        :param verbose_name:, :param help_text: A standard features
          (see the reference).
        :param blank:, :param null: A standard features (see the reference).
        :param default: TODO
        :param editable: If False, the field will not be displayed in the admin
          or any other ModelForm. They are also skipped during
          model validation.
        :param db_column: Could be a string or a tuple of two strings.
          If a string is passed, use `<db_column>_source` and
          `<db_column>_html` as a column names. If a tuple of two string
          is passed, those strings are used as a column names.
        :param error_messages: A standard feature (see the reference).
        :param source_validators: A list of validators that will be applied
          to the source markdown field.
        :param html_validators: A list of validators that will be applied
          to the html markdown field.
        :param common_validators: A list of validators that will receive both
          source and html as a positional arguments
          (e.g. `def validator(source, html): ...` ).
        :param markdown: A class derived from `Markdown` that will be used for
          storing the value.


        Ignored parameters:

        :param primary_key:
        :param unique:
        :param db_index:
        :param validators:
        :param rel:
        :param serialize:
        :param unique_for_date:
        :param unique_for_month:
        :param unique_for_year:
        :param choices:
        :param db_tablespace:


        """
        if not common_validators:
            common_validators = []
        if not html_validators:
            html_validators = []
        if not source_validators:
            source_validators = []

        self._db_column_cached = db_column  # save for deconstruction
        if db_column and isinstance(db_column, str):
            self.source_column = db_column + '_source'
            self.html_column = db_column + '_html'
        elif db_column and isinstance(db_column, (tuple, list)):
            self.source_column = db_column[0]
            self.html_column = db_column[1]
        else:
            self.source_column = None
            self.html_column = None

        self.source_validators = source_validators
        self.html_validators = html_validators
        self.common_validators = common_validators

        self.markdown = markdown

        kwargs.pop('primary_key', '')
        kwargs.pop('max_length', '')
        kwargs.pop('unique', '')
        kwargs.pop('db_index', '')
        kwargs.pop('validators', '')
        kwargs.pop('rel', '')
        kwargs.pop('serialize', '')
        kwargs.pop('unique_for_date', '')
        kwargs.pop('unique_for_month', '')
        kwargs.pop('unique_for_year', '')
        kwargs.pop('choices', '')
        kwargs.pop('db_tablespace', '')

        super(MarkdownField, self).__init__(*args, **kwargs)

        if self.default is NOT_PROVIDED:
            self.default = self.markdown('', '')

        if not isinstance(self.default, self.markdown):
            self.default = self.markdown(str(self.default))

    def deconstruct(self):
        """
        Returns enough information to recreate the field

        """
        name, path, args, kwargs = super(MarkdownField, self).deconstruct()

        if self._db_column_cached is not None:
            kwargs.update(dict(db_column=self._db_column_cached))

        if self.source_validators:
            kwargs.update(dict(source_validators=self.source_validators))
        if self.html_validators:
            kwargs.update(dict(html_validators=self.html_validators))
        if self.common_validators:
            kwargs.update(dict(common_validators=self.common_validators))

        kwargs.update(dict(markdown=self.markdown))

        return name, path, args, kwargs

    def run_validators(self, value):
        """
        Run all source, html, and common validators

        :param value: `Markdown` class instance which needs to be validated.

        """
        # We are using custom validator lists so we need to overwrite
        # this function.
        print('~' * 80)
        print(value, type(value), repr(value))
        print('~' * 80)

    def from_db_value(self, value, *args, **kwargs):
        """
        From database to python.

        :param value: JSON value that is stored in the database.
        :param args:, :param kwargs: Other arguments are unused.

        :return: The `Markdown` class instance.

        """
        if value is None or not value:
            return None
        try:
            return self.markdown.deserialize(value)
        except Exception as e:
            raise exceptions.ValidationError(str(e))

    def get_prep_value(self, value):
        """
        From python to database.

        :param value: A `Markdown` class instance.
        :return: JSON serialized `Markdown` class.

        """
        if value is None:
            return None
        else:
            value.compile()
            return value.serialize()

    def to_python(self, value):
        """
        From any to python (used in processing forms)

        :param value: Source string, `Markdown`, or None.
        :return: None or `Markdown`.

        """
        if value is None:
            return value
        elif isinstance(value, self.markdown):
            return value
        else:
            return self.markdown(value)

    def get_db_prep_lookup(self, *args, **kwargs):
        """
        Prepare value for the lookup (e.g. `value__gt=...`)

        :param args:, :param kwargs: Unused.

        """
        raise NotImplementedError(self.get_db_prep_lookup)

    def formfield(self, **kwargs):
        """
        Returns a form field for this model field.

        :param kwargs: Arguments for the form field class.
        :return: A form field instance.
        """
        defaults = {
            'form_class': MarkdownFormField,
            'markdown': self.markdown,
        }
        defaults.update(kwargs)
        return super(MarkdownField, self).formfield(**defaults)

    def contribute_to_class(self, cls, name, virtual_only=False):
        """
        Register the field and add ancillary attributes.

        :param cls: Model instance.
        :param name: Field name.
        :param virtual_only: Virtual only flag.

        """
        super(MarkdownField, self).contribute_to_class(cls, name, virtual_only)
        setattr(cls, '%s_cls' % self.attname, self.markdown)


class MarkdownFormField(forms.fields.CharField):
    """
    Form field for editing markdown objects.

    """
    def __init__(self, *args, source_validators=None, html_validators=None,
                 common_validators=None, markdown=None, **kwargs):
        if not common_validators:
            common_validators = []
        if not html_validators:
            html_validators = []
        if not source_validators:
            source_validators = []

        self.markdown = markdown
        self.common_validators = common_validators
        self.html_validators = html_validators
        self.source_validators = source_validators

        defaults = {'widget': MarkdownTextarea}
        defaults.update(kwargs)

        super(MarkdownFormField, self).__init__(*args, **defaults)

    def run_validators(self, value):
        # We are using custom validator lists so we need to overwrite
        # this function.
        print('~' * 80)
        print(value, type(value), repr(value))
        print('~' * 80)

    def to_python(self, value):
        """
        Text to python.

        :param value: Source string, `Markdown`, or None.
        :return: None or `Markdown`.

        """
        if value in self.empty_values and value != '':
            return value
        elif isinstance(value, self.markdown):
            return value
        else:
            return self.markdown(value)

    def prepare_value(self, value):
        """
        Python to text.

        :param value: A `Markdown` class instance.
        :return: Source text that will be displayed in a widget.

        """
        if isinstance(value, self.markdown):
            return value.source
        else:
            return value
