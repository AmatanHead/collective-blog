"""Markdown model fields"""

from django.db.models import TextField, NOT_PROVIDED
from django.utils import encoding
from django.core import exceptions

from .datatype import Markdown
from .forms import MarkdownFormField

from hashlib import md5
import re


class HtmlCacheDescriptor(object):
    def __init__(self, destination_field):
        """
        This descriptor is used as a proxy between html cache and
        markdown field.

        We assume that the only code that have access to this field is
        the django orm system. So writing to and reading from this field
        is not safe since we don't check the input.

        Accessing to this field is almost equivalent to accessing raw
        `markdown._html` data. However, there is also an aloogithm to
        check that the html that is being set to the `markdown._html` is clean.

        When getting html value, this class prepends
        the md5 hash of the source string to the html data.

        When setting html value, we check if the hash is correct.
        If the hash is correct, we set `is_dirty` flag to be false.

        :param destination_field: Object to which the descriptor is pointing.

        """
        self.destination_field = destination_field

        # These fields must not be cached!
        # If html_cache field is being loaded before the main field,
        # these values can be `None`.

        # self.cls_name = self.destination_field.cls_name
        # self.state_name = self.destination_field.state_name

    def setup(self, instance, html=None):
        """
        Set up the state if it's empty.

        We can't do that when the model instance is created because we have
        no access to the initialization process. Thus, we set up the class
        on first read/write operation.

        :param instance: A model instance.
        :param html: Default html content.

        """

        markdown_cls = getattr(instance, self.destination_field.cls_name)

        if not hasattr(instance, self.destination_field.state_name):
            setattr(instance, self.destination_field.state_name, markdown_cls('', html))

    @staticmethod
    def hash(string):
        """
        Calculates and returns the hash of the source markdown data.
        It is used to check that the cached data is up-to-date.

        :param string: A string that needs to be cached.
        :return: A hash string.

        """
        source = '%s\t%s' % (len(encoding.force_text(string)), encoding.force_text(string))
        return '<!-- %s -->' % md5(source.encode()).hexdigest()

    hash_re = re.compile(r'^<!-- [a-zA-Z0-9]{32} -->')

    @classmethod
    def split(cls, html):
        """
        Extract hash from the passed html.

        :param html: Html string to check.
        :return: Pair `(hash, html)`. `hash` may be empty.

        """
        hash_match = cls.hash_re.match(html)
        if hash_match is None:
            return '', html
        else:
            return html[:hash_match.end()], html[hash_match.end():]

    def __get__(self, instance, owner):
        self.setup(instance, '')

        field = getattr(instance, self.destination_field.state_name)

        return self.hash(field.source) + field.html_force

    def __set__(self, instance, value):
        self.setup(instance, '')

        if value is None:
            value = ''

        hash_str, html = self.split(encoding.force_text(value))

        field = getattr(instance, self.destination_field.state_name)

        field._html = html

        # Check that the cache is up-to-date
        if hash_str == self.hash(field.source):
            field._is_dirty = False
        else:
            field._is_dirty = True


class HtmlCacheField(TextField):
    def __init__(self, markdown_field, *args, **kwargs):
        """
        Database field for caching rendered html.

        On save, this field enforces html rendering, than saves the result.

        You should be very careful with database denormalization.
        When you add this field, check that you update all generated html.

        If this field contains Null value, when loading from a database,
        cache is considered being empty so you get a dirty `Markdown`
        object with `html` is Null. However, if this field is not empty,
        cache is considered being up to date so you get
        non-dirty `Markdown` object.

        So be aware of changing contents of the markdown field if you not sure
        that `HtmlCacheField` cannot update the cache (e.g. using plain
        SQL queries or disabling this field while
        database column is not deleted).

        We assume that the only code that have access to this field is
        the django orm system. So writing to and reading from this field
        is not safe since we don't check the input.
        See the `HtmlCacheDescriptor` documentation.

        """
        kwargs.update(dict(editable=False, blank=True, null=True))
        self.markdown_field = markdown_field
        super(HtmlCacheField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        """
        Returns enough information to recreate the field.

        """
        name, path, args, kwargs = super(HtmlCacheField, self).deconstruct()

        if self.markdown_field is not None:
            kwargs.update(dict(markdown_field=self.markdown_field))

        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, virtual_only=False):
        """
        Register the field and add ancillary attributes.

        :param cls: Model instance.
        :param name: Field name.
        :param virtual_only: Virtual only flag.

        """
        super(HtmlCacheField, self).contribute_to_class(cls, name, virtual_only)
        setattr(cls, self.name, HtmlCacheDescriptor(self.markdown_field))


class ClsDescriptor(object):
    def __init__(self, cls):
        """
        A simple read-only descriptor that is used for accessing
        the `Markdown` renderer class.

        """
        self.cls = cls

    def __get__(self, instance, owner):
        return self.cls


class MarkdownDescriptor(object):
    def __init__(self, destination_field):
        self.destination_field = destination_field

        # These fields must not be cached!
        # If html_cache field is being loaded before the main field,
        # these values can be `None`.

        # self.cls_name = self.destination_field.cls_name
        # self.state_name = self.destination_field.state_name

    def setup(self, instance, value=''):
        """
        Set up the state if it's empty.

        We can't do that when the model instance is created because we have
        no access to the initialization process. Thus, we set up the class
        on first read/write operation.

        :param instance: A model instance.
        :param value: Default source content.

        """

        markdown_cls = getattr(instance, self.destination_field.cls_name)

        if not hasattr(instance, self.destination_field.state_name):
            setattr(instance, self.destination_field.state_name, markdown_cls(value))

    def __get__(self, instance, owner):
        self.setup(instance, '')
        return getattr(instance, self.destination_field.state_name)

    def __set__(self, instance, value):
        self.setup(instance, '')

        markdown_cls = getattr(instance, self.destination_field.cls_name)

        if isinstance(value, markdown_cls):
            setattr(instance, self.destination_field.state_name, value)
        else:
            field = getattr(instance, self.destination_field.state_name)
            field._source = encoding.force_text(value)


class MarkdownField(TextField):
    def __init__(self, *args, **kwargs):
        """
        Database field for storing `Markdown` objects.

        This field forces the html update process while preparing for query.
        Therefore it is guaranteed that html stored in a database
        is always ut-to-date.

        Parameters:

        :param default: Can be either a string ot a `Markdown` class instance.
          Strings are converted to `Markdown` objects.
        :param state_name: A name for the state field.
          Default is `<name>_state`.
        :param cls_name: A name for the markdown generator class.
          Default is `<name>_cls`.
        :param source_validators: A list of validators that will be applied
          to the source markdown field.
        :param html_validators: A list of validators that will be applied
          to the html markdown field.
        :param validators: A list of validators that will receive
          a `Markdown` class instance.
        :param markdown: A class derived from `Markdown` that will be used for
          storing the value.


        Ignored parameters:

        :param primary_key:
        :param unique:
        :param db_index:
        :param null:
        :param rel:
        :param unique_for_date:
        :param unique_for_month:
        :param unique_for_year:
        :param choices:
        :param db_tablespace:

        """
        markdown = kwargs.pop('markdown', Markdown)
        state_name = kwargs.pop('state_name', None)
        cls_name = kwargs.pop('cls_name', None)

        self.validators = kwargs.pop('validators', [])

        self.source_validators = kwargs.pop('source_validators', [])
        self.html_validators = kwargs.pop('html_validators', [])

        self.cls_name = cls_name
        self.state_name = state_name

        self.markdown = markdown

        kwargs.pop('primary_key', '')
        kwargs.pop('max_length', '')
        kwargs.pop('unique', '')
        kwargs.pop('db_index', '')
        kwargs.pop('rel', '')
        kwargs.pop('null', '')
        kwargs.pop('unique_for_date', '')
        kwargs.pop('unique_for_month', '')
        kwargs.pop('unique_for_year', '')
        kwargs.pop('choices', '')
        kwargs.pop('db_tablespace', '')

        super(MarkdownField, self).__init__(*args, **kwargs)

        # Default is set in the `super` call
        if self.default is NOT_PROVIDED:
            self.default = self.markdown('', '')

        if not isinstance(self.default, self.markdown):
            self.default = self.markdown(encoding.force_text(self.default))

        self._html_field = None

    def deconstruct(self):
        """
        Returns enough information to recreate the field

        """
        name, path, args, kwargs = super(MarkdownField, self).deconstruct()

        if self.source_validators:
            kwargs.update(dict(source_validators=self.source_validators))
        if self.html_validators:
            kwargs.update(dict(html_validators=self.html_validators))
        if self.cls_name is not None:
            kwargs.update(dict(cls_name=self.cls_name))
        if self.state_name is not None:
            kwargs.update(dict(state_name=self.state_name))

        kwargs.update(dict(markdown=self.markdown))

        return name, path, args, kwargs

    def run_validator(self, validator, args=None, kwargs=None):
        """
        Runs a single validator on a value.

        :param validator: A callable. The validator to run.
        :param args: Arguments for the validator
        :param kwargs: Keyword arguments for the validator
        :return: List of errors.

        """
        if kwargs is None:
            kwargs = {}
        if args is None:
            args = []
        try:
            validator(*args, **kwargs)
            return []
        except exceptions.ValidationError as e:
            if hasattr(e, 'code') and e.code in self.error_messages:
                e.message = self.error_messages[e.code]
            return e.error_list

    def run_validators(self, value):
        """
        Run validators on the given value.

        :param value: the `Markdown` class instance which needs validation.
        :return: None
        :raise: ValidationError

        """
        errors = []

        for validator in iter(self.source_validators):
            errors.extend(self.run_validator(validator, [value.source]))

        for validator in iter(self.html_validators):
            errors.extend(self.run_validator(validator, [value.html]))

        for validator in iter(self.validators):
            errors.extend(self.run_validator(validator, [value]))

        if errors:
            raise exceptions.ValidationError(errors)

    def validate(self, value, model_instance):
        """
        Run all source, html, and common validators

        :param model_instance: The model instance.
        :param value: `Markdown` class instance which needs to be validated.

        """
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if not self.blank and (value in self.empty_values or value.source in self.empty_values):
            raise exceptions.ValidationError(self.error_messages['blank'], code='blank')

    def get_prep_value(self, value):
        """
        From python to database.

        :param value: A `Markdown` class instance.
        :return: JSON serialized `Markdown` class.

        """
        if value is None:
            return None
        else:
            return value.source

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
        Prepare value for the lookup (e.g. `var__gt=...`)

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
            '_validators': self.validators,
            '_source_validators': self.source_validators,
            '_html_validators': self.html_validators,
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

        if self.cls_name is None:
            self.cls_name = self.name + '_cls'

        if self.state_name is None:
            self.state_name = '_' + self.name + '_state'

        setattr(cls, self.cls_name, ClsDescriptor(self.markdown))
        setattr(cls, self.name, MarkdownDescriptor(self))
