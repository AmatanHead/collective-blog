"""Markdown data type"""

from json import dumps, loads

import hoep
from .renderers import Hoep


class Markdown(object):
    def __init__(self, source, html=None, renderer=None):
        """
        Markdown data type contains source markdown data and cached
        html.

        :param source: Source markdown data.
        :param html: Generated html. State is considered to be `clean` if the
          html is provided and `dirty` otherwise.
        :param renderer: A class instance with `render` method
          (typically a `Hoep` instance).
          Warning:

        """
        if renderer is None:
            renderer = Hoep(
                extensions=(
                    hoep.EXT_AUTOLINK |
                    hoep.EXT_FENCED_CODE |
                    hoep.EXT_HIGHLIGHT |
                    hoep.EXT_NO_INTRA_EMPHASIS |
                    hoep.EXT_STRIKETHROUGH |
                    hoep.EXT_SUPERSCRIPT |
                    hoep.EXT_TABLES
                ),
                render_flags=(
                    hoep.HTML_ESCAPE |
                    hoep.HTML_EXPAND_TABS
                )
            )

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
            # Dummy
            self._html = self._renderer.render(self._source)
            self._is_dirty = False

    def serialize(self):
        """
        Returns the JSON representation of the class.

        :return: JSON string.

        """
        return dumps(dict(source=self.source, html=self.html))

    @classmethod
    def deserialize(cls, json):
        """
        Returns the markdown instance parsed from the JSON representation
        assuming that in is clean.

        :param json: Source JSON string.
        :return: A `Markdown` class instance.

        """
        data = loads(json)
        return cls(data['source'], data['html'] if 'html' in data else None)

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
