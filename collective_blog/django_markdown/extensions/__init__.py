from markdown.extensions import Extension

from .fenced_code import FencedCodeExtension

class EscapeHtml(Extension):
    def extendMarkdown(self, md, md_globals):
        del md.preprocessors['html_block']
        del md.inlinePatterns['html']
