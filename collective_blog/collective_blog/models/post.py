"""Post and its rating"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext as __

from datetime import datetime

from collective_blog import settings
from collective_blog.utils.errors import PermissionCheckFailed

from .blog import Blog

from s_markdown.models import MarkdownField, HtmlCacheField
from s_markdown.datatype import Markdown
from s_markdown.renderer import BaseRenderer
from s_markdown.extensions import (FencedCodeExtension,
                                   EscapeHtmlExtension,
                                   SemiSaneListExtension,
                                   StrikethroughExtension,
                                   AutomailExtension,
                                   AutolinkExtension,
                                   CutExtension)

from uuslug import uuslug

from s_voting.models import AbstractVote

import re


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               models.DO_NOTHING,
                               verbose_name=_('Author'))

    heading = models.CharField(max_length=100,
                               verbose_name=_('Caption'))

    slug = models.SlugField(max_length=100,
                            db_index=True,
                            unique=True,
                            blank=True,
                            editable=False)

    is_draft = models.BooleanField(default=True,
                                   verbose_name=_('Is draft'))

    content = MarkdownField(blank=False,
                            markdown=Markdown,
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
                                    CutExtension(anchor='cut'),
                                ]
                            ),
                            verbose_name=_('Content'))

    created = models.DateTimeField(blank=True, editable=False)

    updated = models.DateTimeField(blank=True, editable=False, auto_now=True)

    _content_html = HtmlCacheField(content)

    blog = models.ForeignKey(Blog, models.CASCADE,
                             verbose_name=_('Blog'),
                             null=True,
                             blank=True)

    def clean(self):
        """Check that published articles have blog set"""
        super(Post, self).clean()
        if not self.is_draft and not self.blog:
            raise ValidationError(_('You must choose a blog '
                                    'before publishing'))

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Pre-save routine like updating the slug field etc."""

        if not self.pk:
            self.created = datetime.now()

        self.slug = uuslug(self.heading,
                           instance=self,
                           max_length=100,
                           start_no=2,
                           word_boundary=True,
                           save_order=True)

        self.slug = self.slug.lower()

        super(Post, self).save(force_insert, force_update, using, update_fields)

    cut_pattern = re.compile(r'<!-- cut here '
                             r'(\{\{(?P<caption>[^\}]+)\}\} )?'
                             r'-->')

    def content_before_cut(self):
        """Returns html before cut"""
        m = self.cut_pattern.search(self.content.html_force)

        if m is None:
            return self.content.html_force
        else:
            return self.content.html_force[:m.start()]

    def cut_caption(self):
        """Returns cut caption, if specified, or the default one.

        From `---- cut {{ Let's rock! }} ----` will return `Let's rock!`.

        This method does not escape tags in the caption.
        The markdown engine should sanitize it.

        """
        m = self.cut_pattern.search(self.content.html_force)

        print(m)

        if (m is None or 'caption' not in m.groupdict() or
                m.groupdict()['caption'] is None):
            return _('Read more ->')
        else:
            return m.groupdict()['caption']

    def can_be_seen_by_user(self, user, membership):
        """Check if this post can be seen by the user passed"""
        if (user.is_active and user.is_staff and
                user.has_perm('blog.change_post')):
            return True
        elif user.pk == self.author.pk:
            return True
        elif self.is_draft:
            return False
        else:
            return (self.blog.type == 'O' or
                    (membership and not self.blog.is_banned(membership)))

    def can_be_voted_by(self, user, membership):
        """Check if this post can be voted by the user passed"""
        if user.pk == self.author.pk:
            return False
        return (user.is_active and not user.is_anonymous() and
                self.can_be_seen_by_user(user, membership))

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ("-created",)

    def __str__(self):
        return str(self.heading)


class PostVote(AbstractVote):
    object = models.ForeignKey(Post, on_delete=models.CASCADE,
                               related_name='votes')

    @classmethod
    def vote_for(cls, user, obj, vote):
        if user.pk == obj.author.pk:
            raise PermissionCheckFailed(__("You can't vote for your own post"))

        if obj.blog is not None:
            membership = obj.blog.check_membership(user)
        else:
            membership = None

        if obj.can_be_voted_by(user, membership):
            super(PostVote, cls).vote_for(user, obj, vote)
        else:
            raise PermissionCheckFailed(__("You can't vote for this post"))
