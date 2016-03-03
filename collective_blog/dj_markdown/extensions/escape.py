"""
Disable html parsing so that all html is escaped.

See https://pythonhosted.org/Markdown/release-2.6.html#safe_mode-deprecated

"""
import markdown


class EscapeHtmlExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.pop('html_block', '')
        md.inlinePatterns.pop('html', '')
