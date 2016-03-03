"""
Markdown renderers.

"""

import markdown


class BaseRenderer(markdown.Markdown):
    def __init__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs
        super(BaseRenderer, self).__init__(*args, **kwargs)

    def deconstruct(self):
        path = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        args = self.__args
        kwargs = self.__kwargs
        return path, args, kwargs

    def __call__(self, text):
        return self.convert(text)
