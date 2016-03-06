"""Adds syntax for creating habracut"""
from __future__ import absolute_import
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

import re

from django.utils.deconstruct import deconstructible


@deconstructible
class CutExtension(Extension):
    """Adds habracut

    E.g. `----cut----`

    """

    def extendMarkdown(self, md, md_globals):
        """Add FencedBlockPreprocessor to the Markdown instance

        :param md: Current markdown instance.
        :param md_globals: Global markdown vars.

        """
        md.registerExtension(self)

        md.preprocessors.add('cut',
                             CutPreprocessor(md),
                             ">normalize_whitespace")


class CutPreprocessor(Preprocessor):
    """Main fenced code block renderer"""

    block_re = re.compile(
        r'-{4,}[ ]*cut[ ]*(here)?[ ]*-{4,}', re.MULTILINE | re.DOTALL | re.VERBOSE | re.IGNORECASE)

    def run(self, lines):
        """Match cut tags and store them in the htmlStash

        :param lines: Lines of code.

        """

        text = '\n'.join(lines)

        m = self.block_re.search(text)

        if m is not None:
            placeholder = self.markdown.htmlStash.store('<!-- cut here -->',
                                                        safe=True)

            text = '%s\n%s\n%s' % (text[:m.start()],
                                   placeholder,
                                   text[m.end():])

        return text.split('\n')
