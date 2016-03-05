"""Markdown renderers"""

from django.utils.deconstruct import deconstructible

import markdown


@deconstructible
class BaseRenderer(markdown.Markdown):
    # TODO test renderer and extensions
    def __init__(self, *args, **kwargs):
        """Default markdown renderer

        It's required that you add one renderer for each markdown field.

        We need to subclass `markdown.Markdown` in order to provide
        serialization and the `__call__` method.

        """
        self.__args = args
        self.__kwargs = kwargs
        super(BaseRenderer, self).__init__(*args, **kwargs)

    def __call__(self, text):
        """Convert markdown to serialized XHTML or HTML

        Note that this method is not guaranteed to return clean html.

        """
        return self.convert(text)
