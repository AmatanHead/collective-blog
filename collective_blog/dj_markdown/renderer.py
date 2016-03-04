"""
Markdown renderers.

"""

from django.utils.deconstruct import deconstructible

import markdown


@deconstructible
class BaseRenderer(markdown.Markdown):
    # TODO test renderer and extensions
    def __init__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs
        super(BaseRenderer, self).__init__(*args, **kwargs)

    def __call__(self, text):
        return self.convert(text)
