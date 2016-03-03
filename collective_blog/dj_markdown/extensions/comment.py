"""
Disable headers and some other blocks for comment-like markdown peaces.

"""
from markdown.extensions import Extension


class CommentExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.parser.blockprocessors.pop('hr', '')
        md.parser.blockprocessors.pop('hashheader', '')
        md.parser.blockprocessors.pop('setextheader', '')
