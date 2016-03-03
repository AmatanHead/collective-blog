"""
Adds fenced code block support.

Copied from
https://pythonhosted.org/Markdown/extensions/fenced_code_blocks.html

Original code Copyright 2007-2008 [Waylan Limberg](http://achinghead.com/).
All changes Copyright 2008-2014 The Python Markdown Project
License: [BSD](http://www.opensource.org/licenses/bsd-license.php)

"""

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

import re

from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from django.utils.html import escape


class FencedCodeExtension(Extension):
    """
    Adds fenced code blocks, e.g.

    ```lang

    ...

    ```

    """

    def extendMarkdown(self, md, md_globals):
        """
        Add FencedBlockPreprocessor to the Markdown instance.

        """
        md.registerExtension(self)

        md.preprocessors.add('fenced_code_block',
                             FencedBlockPreprocessor(md),
                             ">normalize_whitespace")


class Formatter(HtmlFormatter):
    """
    Formats a highlighted code block so that it is compatible with
    the `Light` framework layout.

    """
    def _wrap_pre(self, inner):
        yield 0, ('<pre><ol>')
        for tup in inner:
            print(tup)
            yield tup[0], '<li>%s</li>' % tup[1]
        yield 0, '</ol></pre>'


class FencedBlockPreprocessor(Preprocessor):
    """
    Main fenced code block renderer.

    """

    block_re = re.compile(
        r'(?P<fence>^(?:`{3}))[ ]*'
        r'(?P<lang>[a-zA-Z0-9_+-]*)?[ ]*\n'
        r'(?P<code>.*?)(?<=\n)'
        r'(?P=fence)[ ]*$', re.MULTILINE | re.DOTALL | re.VERBOSE)

    def run(self, lines):
        """
        Match and store Fenced Code Blocks in the HtmlStash.

        :param lines: Lines of code.

        """

        text = "\n".join(lines)
        while 1:
            m = self.block_re.search(text)
            if m:
                lang = ''
                if m.group('lang'):
                    lang = m.group('lang')

                try:
                    lexer = get_lexer_by_name(lang, stripall=True)
                    formatter = Formatter()
                    code = highlight(m.group('code'), lexer, formatter)
                except ClassNotFound:
                    code = escape(m.group('code'))
                    if lang:
                        formatter = lambda x: '<li>%s</li>' % x
                        code = ''.join(map(formatter, code.split('\n')))
                        code = '<ol>%s</ol>' % code
                    code = '<pre>%s</pre>' % code

                placeholder = self.markdown.htmlStash.store(code, safe=True)
                text = '%s\n%s\n%s' % (text[:m.start()],
                                       placeholder,
                                       text[m.end():])
            else:
                break
        return text.split("\n")
