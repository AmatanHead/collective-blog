"""Disable html parsing so that all html is escaped"""

from django.utils.deconstruct import deconstructible

import markdown


@deconstructible
class EscapeHtmlExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        """Disable html processing

        See the example at
        https://pythonhosted.org/Markdown/release-2.6.html#safe_mode-deprecated

        """
        md.preprocessors.pop('html_block', '')
        md.inlinePatterns.pop('html', '')
