from markdown.extensions import Extension

from .fenced_code import FencedCodeExtension
from .semi_sane_lists import SemiSaneListExtension
from .strikethrough import StrikethroughExtension
from .automail import AutomailExtension
from .autolink import AutolinkExtension

class EscapeHtmlExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        del md.preprocessors['html_block']
        del md.inlinePatterns['html']
