"""Markdown data type"""

from json import dumps, loads

class Markdown(object):
    def __init__(self, source, html=None):
        self._source = source
        if html is None:
            self._html = ''
            self._is_dirty = True
        else:
            self._html = html
            self._is_dirty = False

    def _source_get(self):
        return self._source

    @property
    def source(self):
        """
        Return source markdown string.

        """
        return self._source

    @source.setter
    def source(self, value):
        """
        Set source markdown string and mark the object state as `dirty`.

        Setting source string does not cause any compilation process.
        That is, markdown compilation is done in a lazy way.

        """
        self._source = value
        self._is_dirty = True

    @property
    def html(self):
        """
        Returns html value.

        If the state of the object is `dirty`,
        html may not match the source data.

        """
        return self._html

    @property
    def is_dirty(self):
        """
        Returns object state.

        For dirty objects, html is not guaranteed to match the source data.

        """
        return self._is_dirty

    @property
    def html_force(self):
        """
        Returns html value.

        Accessing this property forces the html updating process.

        """
        self.compile()
        return self._html

    def compile(self, force=False):
        """
        Updates the html value by compiling source data.

        The compilation process is not invoked on clean classes unless
        `force` is set to `True`.

        """
        if self.is_dirty or force:
            # Dummy
            self._html = (self._source + '\n<br>\n<mark>Compiled</mark><br>')
            self._is_dirty = False

    def serialize(self):
        """
        Returns the JSON representation of the class.

        """
        return dumps(dict(source=self.source, html=self.html))

    @classmethod
    def deserialize(cls, json):
        """
        Returns the markdown instance parsed from the JSON representation
        assuming that in is clean.

        """
        data = loads(json)
        return cls(data['source'], data['html'])

    def deconstruct(self):
        """
        Deconstruct this field for further serialization
        (used in migrations)

        """
        path = "markdown.datatype.Markdown"
        args = []
        kwargs = dict(source=self.source)
        if not self.is_dirty:
            kwargs.update(dict(html=self.html))
        return path, args, kwargs
