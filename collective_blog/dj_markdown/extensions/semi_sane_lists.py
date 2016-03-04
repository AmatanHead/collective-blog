"""
Adds github-like lists syntax.

Copied from https://github.com/google/py-gfm/

"""
# Copyright (c) 2012, the Dart project authors.  Please see the AUTHORS file
# for details. All rights reserved. Use of this source code is governed by a
# BSD-style license that can be found in the LICENSE file.

from django.utils.deconstruct import deconstructible

import markdown


class SemiSaneOListProcessor(markdown.blockprocessors.OListProcessor):
    SIBLING_TAGS = ['ol']


class SemiSaneUListProcessor(markdown.blockprocessors.UListProcessor):
    SIBLING_TAGS = ['ul']


@deconstructible
class SemiSaneListExtension(markdown.Extension):
    """An extension that causes lists to be treated the same way GitHub does.

    Like the sane_lists extension, GitHub considers a list to end if it's
    separated by multiple newlines from another list of a different type. Unlike
    the sane_lists extension, GitHub will mix list types if they're not
    separated by multiple newlines.

    Github also recognizes lists that start in the middle of a paragraph. This
    is currently not supported by this extension, since the Python parser has a
    deeply-ingrained belief that blocks are always separated by multiple
    newlines.
    """

    def extendMarkdown(self, md, md_globals):
        md.parser.blockprocessors['olist'] = SemiSaneOListProcessor(md.parser)
        md.parser.blockprocessors['ulist'] = SemiSaneUListProcessor(md.parser)
