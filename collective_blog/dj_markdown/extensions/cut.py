"""Adds syntax for creating habracut"""
from __future__ import absolute_import
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

import re

from django.utils.deconstruct import deconstructible
from django.utils.html import escape


@deconstructible
class CutExtension(Extension):
    def __init__(self, *args, **kwargs):
        """Adds habracut

        E.g. `----cut----`

        """
        self.anchor = kwargs.pop('anchor', '')
        super(CutExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add FencedBlockPreprocessor to the Markdown instance

        :param md: Current markdown instance.
        :param md_globals: Global markdown vars.

        """
        md.registerExtension(self)

        if 'fenced_code_block' in md.preprocessors:
            md.preprocessors.add('cut',
                                 CutPreprocessor(md, anchor=self.anchor),
                                 ">fenced_code_block")
        else:
            md.preprocessors.add('cut',
                                 CutPreprocessor(md, anchor=self.anchor),
                                 ">normalize_whitespace")


class CutPreprocessor(Preprocessor):
    def __init__(self, *args, **kwargs):
        """Main fenced code block renderer"""
        self.anchor = kwargs.pop('anchor', '')
        super(CutPreprocessor, self).__init__(*args, **kwargs)

    block_re = re.compile(
        r'-{4,}[ ]*'
        r'cut[ ]*(here)?[ ]*'
        r'(\{\{(?P<caption>[^\}]+)\}\})?'
        r'[ ]*-{4,}', re.MULTILINE | re.DOTALL | re.VERBOSE | re.IGNORECASE)

    def run(self, lines):
        """Match cut tags and store them in the htmlStash

        :param lines: Lines of code.

        """

        text = '\n'.join(lines)

        m = self.block_re.search(text)

        if m is not None:
            if 'caption' in m.groupdict():
                html = '<!-- cut here {{ %s }} -->' % escape(m.groupdict()['caption'])
            else:
                html = '<!-- cut here -->'

            if self.anchor:
                html += '<a name="%s"></a>' % escape(self.anchor)

            placeholder = self.markdown.htmlStash.store(html,
                                                        safe=True)

            text = '%s\n%s\n%s' % (text[:m.start()],
                                   placeholder,
                                   text[m.end():])

        return text.split('\n')
