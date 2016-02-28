from django.test import TransactionTestCase
from django.core import validators
from django.core import exceptions

from django_fake_model.models import FakeModel

from .models import MarkdownField, HtmlCacheField, HtmlCacheDescriptor
from .datatype import Markdown


def md_validator(md):
    if '!' in md.source:
        raise exceptions.ValidationError('=(')

    if '!' in md.html:
        raise exceptions.ValidationError('=(')


class MarkdownDerived(Markdown):
    pass


class TestModel(FakeModel):
    """
    A model for test app.

    """

    raw = MarkdownField()
    raw2 = MarkdownField()

    default = MarkdownField(default='Default')
    default2 = MarkdownField(default=Markdown('Default'))
    default3 = MarkdownField(default=Markdown('Default', 'Html'))

    cached = MarkdownField(markdown=MarkdownDerived, blank=True)
    cached_c = HtmlCacheField(cached)

    html_validated = MarkdownField(html_validators=[validators.RegexValidator(r'!', inverse_match=True)], blank=True)

    source_validated = MarkdownField(source_validators=[validators.RegexValidator(r'!', inverse_match=True)], blank=True)

    validated = MarkdownField(validators=[md_validator], blank=True)


@TestModel.fake_me
class MarkdownModelFieldTest(TransactionTestCase):
    def test_class_creation(self):
        """
        Test that what is created is a `Markdown` class instance.

        """

        test = TestModel.objects.create(raw='Source')

        self.assertIsInstance(test.raw, Markdown)
        self.assertEqual(test.raw.source, 'Source')
        self.assertEqual(test.raw.html, '')
        self.assertTrue(test.raw.is_dirty)

        self.assertIsInstance(test.default, Markdown)
        self.assertEqual(test.default.source, 'Default')
        self.assertEqual(test.default.html, '')
        self.assertTrue(test.default.is_dirty)

        self.assertIsInstance(test.default2, Markdown)
        self.assertEqual(test.default2.source, 'Default')
        self.assertEqual(test.default2.html, '')
        self.assertTrue(test.default2.is_dirty)

        self.assertIsInstance(test.default3, Markdown)
        self.assertEqual(test.default3.source, 'Default')
        self.assertEqual(test.default3.html, 'Html')
        self.assertFalse(test.default3.is_dirty)

        self.assertIsInstance(test.cached, MarkdownDerived)
        self.assertNotIsInstance(test.raw, MarkdownDerived)

    def test_blank(self):
        """
        Test that `blank=True` raises in error when and only when
        the field is blank.

        """
        test = TestModel()
        with self.assertRaises(exceptions.ValidationError) as c:
            test.clean_fields()
        self.assertIn('raw', c.exception.error_dict)
        self.assertIn('raw2', c.exception.error_dict)

        test = TestModel(raw='Source')
        with self.assertRaises(exceptions.ValidationError) as c:
            test.clean_fields()
        self.assertNotIn('raw', c.exception.error_dict)
        self.assertIn('raw2', c.exception.error_dict)

    def test_validators(self):
        """
        Test that validators applied correctly.

        """
        test = TestModel(raw='Source', raw2='Source2')

        test.html_validated.source = '!'
        test.html_validated.compile()
        with self.assertRaises(exceptions.ValidationError) as c:
            test.clean_fields()
        self.assertIn('html_validated', c.exception.error_dict)
        self.assertNotIn('source_validated', c.exception.error_dict)

        test.html_validated.source = ''
        test.html_validated.compile()
        test.source_validated.source = '!'
        with self.assertRaises(exceptions.ValidationError) as c:
            test.clean_fields()
        self.assertIn('source_validated', c.exception.error_dict)
        self.assertNotIn('html_validated', c.exception.error_dict)

        test.source_validated.source = ''

        test.validated.source = '!'
        with self.assertRaises(exceptions.ValidationError) as c:
            test.clean_fields()
        self.assertIn('validated', c.exception.error_dict)

        test.validated.compile()
        test.validated.source = ''

        with self.assertRaises(exceptions.ValidationError) as c:
            test.clean_fields()
        self.assertIn('validated', c.exception.error_dict)

    def test_plain_var_access(self):
        """
        Test that `MarkdownDescriptor` works correctly.

        """
        test = TestModel(raw='Source', raw2='Source2')

        self.assertIsInstance(test.raw, Markdown)
        self.assertEqual(test.raw.source, 'Source')

        test.raw = 'String'

        self.assertIsInstance(test.raw, Markdown)
        self.assertEqual(test.raw.source, 'String')

        md = Markdown('String 2')

        test.raw = md

        self.assertIsInstance(test.raw, Markdown)
        self.assertIs(test.raw, md)
        self.assertEqual(test.raw.source, 'String 2')

        test = TestModel(raw='Source', raw2='Source2', cached=[{}])

        self.assertEqual(test.cached.source, '[{}]')

        test.cached = {}

        self.assertEqual(test.cached.source, '{}')

    def test_cached(self):
        """
        Test that cached values accessed correctly.

        """
        test = TestModel(raw='Source', raw2='Source2', cached='text')

        self.assertIsInstance(test.cached, Markdown)
        self.assertEqual(test.cached.source, 'text')
        self.assertEqual(test.cached.html, '')
        self.assertTrue(test.cached.is_dirty)

        md = MarkdownDerived('String')

        test.cached = md

        self.assertIsInstance(test.cached, Markdown)
        self.assertEqual(test.cached.source, 'String')
        self.assertEqual(test.cached.html, '')
        self.assertTrue(test.cached.is_dirty)

        test.cached.compile()

        self.assertIsInstance(test.cached, Markdown)
        self.assertEqual(test.cached.source, 'String')
        self.assertEqual(test.cached.html, md.html_force)
        self.assertFalse(test.cached.is_dirty)

        md = MarkdownDerived('String 2')

        test = TestModel(raw='Source', raw2='Source2', cached=md)

        self.assertIsInstance(test.cached, Markdown)
        self.assertEqual(test.cached.source, 'String 2')
        self.assertEqual(test.cached.html, '')
        self.assertTrue(test.cached.is_dirty)

        test.cached.compile()

        self.assertIsInstance(test.cached, Markdown)
        self.assertEqual(test.cached.source, 'String 2')
        self.assertEqual(test.cached.html, md.html_force)
        self.assertFalse(test.cached.is_dirty)

    def test_raw_cache_access(self):
        """
        Test that `HtmlCacheDescriptor` works correctly with broken
        cache values.

        """
        md = MarkdownDerived('String')
        source = md.source

        test = TestModel(raw='Source', raw2='Source2', cached=md)

        self.assertIs(test.cached, md)

        test.cached_c = 'Cache is broken!'

        self.assertEqual(test.cached.source, source)
        self.assertEqual(test.cached.html, 'Cache is broken!')
        self.assertTrue(test.cached.is_dirty)

        test.cached_c = HtmlCacheDescriptor.hash(source) + source

        self.assertEqual(test.cached.source, source)
        self.assertEqual(test.cached.html, source)
        self.assertFalse(test.cached.is_dirty)

    def test_cache_hash(self):
        """
        Test that hashing and splitting function works correctly.

        """
        source1 = 'string 1'
        source2 = 'string 2'

        hashed1 = HtmlCacheDescriptor.hash(source1)
        hashed2 = HtmlCacheDescriptor.hash(source2)

        h1, s1 = HtmlCacheDescriptor.split(hashed1 + source1)
        h2, s2 = HtmlCacheDescriptor.split(hashed2 + source2)

        self.assertEqual(s1, source1)
        self.assertEqual(s2, source2)
        self.assertNotEqual(h1, h2)

        source1 = ''
        source2 = None

        hashed1 = HtmlCacheDescriptor.hash(source1)
        hashed2 = HtmlCacheDescriptor.hash(source2)

        h1, s1 = HtmlCacheDescriptor.split(hashed1 + source1)
        h2, s2 = HtmlCacheDescriptor.split(hashed2 + str(source2))

        self.assertEqual(s1, source1)
        self.assertEqual(s2, str(source2))
        self.assertNotEqual(h1, h2)

    def test_contribute_to_class(self):
        test = TestModel(raw='Source', raw2='Source2')

        self.assertIs(test.raw_cls, Markdown)
        self.assertIs(test.raw2_cls, Markdown)
        self.assertIs(test.default_cls, Markdown)
        self.assertIs(test.default2_cls, Markdown)
        self.assertIs(test.default3_cls, Markdown)
        self.assertIs(test.cached_cls, MarkdownDerived)
