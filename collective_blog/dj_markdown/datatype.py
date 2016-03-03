"""
Markdown data type.

This is the datatype that is stored in the markdown field.

"""

from django.utils import encoding


class Markdown(object):
    def __init__(self, renderer, source, html=None):
        """
        Markdown data type contains source markdown data and cached
        html.

        :param source: Source markdown data.
        :param html: Generated html. State is considered to be `clean` if the
          html is provided and `dirty` otherwise.
        :param renderer: An instance of a `renderers.BaseRenderer` subclass
          that will be used to render an html.

        """
        self._source = source
        self._renderer = renderer

        if html is None:
            self._html = ''
            self._is_dirty = True
        else:
            self._html = html
            self._is_dirty = False

    @property
    def source(self):
        """
        :return: The source markdown string.

        """
        return self._source

    @source.setter
    def source(self, value):
        """
        Set the source markdown string and mark the object state as `dirty`.

        Setting source string does not cause any compilation process.
        That is, markdown compilation is done in a lazy way.

        :param value: New source value.

        """
        self._source = value
        self._is_dirty = True

    @property
    def html(self):
        """
        :return: The html value.

        If the state of the object is `dirty`,
        html may not match the source data.

        """
        return self._html

    @property
    def is_dirty(self):
        """
        :return: Object state.

        For dirty objects, html is not guaranteed to match the source data.

        """
        return self._is_dirty

    @property
    def html_force(self):
        """
        :return: The html value.

        Accessing this property forces the html updating process.

        """
        self.compile()
        return self._html

    def compile(self, force=False):
        """
        Updates the html value by compiling source data.

        The compilation process is not invoked on clean classes unless
        `force` is set to `True`.

        :param force: Force compilation.

        """
        if self.is_dirty or force:
            self._html = self._renderer(encoding.force_text(self._source))
            self._is_dirty = False

    def deconstruct(self):
        """
        Deconstruct this field for further serialization
        (used in migrations)

        :return: Standard deconstruction result.

        """
        path = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        args = []
        kwargs = dict(source=self.source, renderer=self._renderer)
        if not self.is_dirty:
            kwargs.update(dict(html=self.html))
        return path, args, kwargs
