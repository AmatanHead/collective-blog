"""
Markdown renderers.

"""

import hoep


class Hoep(hoep.Hoep):
    def __init__(self, extensions=0, render_flags=0):
        """
        Basic markdown renderer.

        :param extensions:, :param render_flags: See the `Hoep` docs.

        """
        # We need to subclass `hoep.Hoep` to use serialization.
        super(Hoep, self).__init__(extensions, render_flags)
        self._extensions_cached = extensions
        self._render_flags_cached = render_flags

    def deconstruct(self):
        """
        Deconstruct this field for further serialization
        (used in migrations)

        :return: Standard deconstruction result.

        """
        path = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        args = []
        kwargs = {}
        if self._extensions_cached:
            kwargs.update(dict(extensions=self._extensions_cached))
        if self._render_flags_cached:
            kwargs.update(dict(render_flags=self._render_flags_cached))
        return path, args, kwargs
