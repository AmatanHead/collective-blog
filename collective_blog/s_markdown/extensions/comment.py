"""Disable headers and some other blocks for comment-like markdown peaces"""
from django.utils.deconstruct import deconstructible

from markdown.extensions import Extension


@deconstructible
class CommentExtension(Extension):
    """Disable headers and some other blocks for comment-like messages"""

    def extendMarkdown(self, md, md_globals):
        """Disable <hr>, <h.>

        To disable rendering of these blocks,
        we need to delete theirs processors.

        :param md: Current markdown instance.
        :param md_globals: Global markdown vars.

        """
        md.parser.blockprocessors.pop('hr', '')
        md.parser.blockprocessors.pop('hashheader', '')
        md.parser.blockprocessors.pop('setextheader', '')
