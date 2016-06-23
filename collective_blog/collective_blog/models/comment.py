from django.db import models

from django.utils.translation import ugettext_lazy as _, ugettext as __

from mptt.models import MPTTModel, TreeForeignKey

from collective_blog.settings import settings
from collective_blog.utils.errors import PermissionCheckFailed
from s_markdown.models import MarkdownField, HtmlCacheField
from s_markdown.datatype import Markdown
from s_markdown.renderer import BaseRenderer
from s_markdown.extensions import (FencedCodeExtension,
                                   EscapeHtmlExtension,
                                   SemiSaneListExtension,
                                   StrikethroughExtension,
                                   AutomailExtension,
                                   AutolinkExtension,
                                   CommentExtension)
from s_voting.models import AbstractVote, VoteCacheField


class CommentVote(AbstractVote):
    object = models.ForeignKey('Comment', on_delete=models.CASCADE,
                               related_name='votes')

    @classmethod
    def vote_for(cls, user, obj, vote):
        if user.pk == obj.author.pk:
            raise PermissionCheckFailed(__("You can't vote for your own comment"))

        if obj.post.blog is not None:
            membership = obj.post.blog.check_membership(user)
        else:
            membership = None

        if (user.is_active and not user.is_anonymous() and
                obj.post.can_be_seen_by_user(user, membership)):
            super(CommentVote, cls).vote_for(user, obj, vote)
        else:
            raise PermissionCheckFailed(__("You can't vote for this comment"))


class Comment(MPTTModel):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE)

    post = models.ForeignKey('Post', models.CASCADE,
                             verbose_name=_('Post'),
                             db_index=True)

    content = MarkdownField(markdown=Markdown,
                            renderer=BaseRenderer(
                                extensions=[
                                    'markdown.extensions.smarty',
                                    'markdown.extensions.abbr',
                                    'markdown.extensions.def_list',
                                    'markdown.extensions.tables',
                                    'markdown.extensions.smart_strong',
                                    FencedCodeExtension(),
                                    EscapeHtmlExtension(),
                                    SemiSaneListExtension(),
                                    StrikethroughExtension(),
                                    AutolinkExtension(),
                                    AutomailExtension(),
                                    CommentExtension(),
                                ]
                            ),
                            verbose_name=_('Comment'))

    _content_html = HtmlCacheField(content)

    created = models.DateTimeField(blank=True, editable=False,
                                   auto_now_add=True)

    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', db_index=True)

    rating = VoteCacheField(CommentVote)

    is_hidden = models.BooleanField(default=False,
                                    verbose_name=_('Is hidden'))
    is_hidden_by_moderator = models.BooleanField(default=False,
                                                 verbose_name=_('Is hidden by moderator'))

    class MPTTMeta:
        order_insertion_by = ['created']

    def __str__(self):
        return str(self.author) + ' on ' + str(self.post)
