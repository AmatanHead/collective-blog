"""Post and its rating"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import datetime

from collective_blog import settings

from .blog import Blog

from dj_markdown.models import MarkdownField, HtmlCacheField
from dj_markdown.datatype import Markdown
from dj_markdown.renderer import BaseRenderer
from dj_markdown.extensions import (FencedCodeExtension,
                                    EscapeHtmlExtension,
                                    SemiSaneListExtension,
                                    StrikethroughExtension,
                                    AutomailExtension,
                                    AutolinkExtension)

from voting.models import AbstractVote


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               models.DO_NOTHING,
                               verbose_name=_('Author'))

    heading = models.CharField(max_length=100,
                               verbose_name=_('Caption'))

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
                                ]
                            ),
                            verbose_name=_('Content'))

    created = models.DateTimeField(blank=True, editable=False)

    _content_html = HtmlCacheField(content)

    blog = models.ForeignKey(Blog, models.CASCADE,
                             verbose_name=_('Blog'),
                             null=True,
                             blank=True)

    def clean(self):
        super(Post, self).clean()
        if not self.is_draft and not self.blog:
            raise ValidationError(_('You must choose a blog '
                                    'before publishing'))

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if not self.pk:
            self.created = datetime.now()
        super(Post, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
        ordering = ("-created",)

    def __str__(self):
        return str(self.heading)


class PostVote(AbstractVote):
    object = models.ForeignKey(Post, on_delete=models.CASCADE,
                               related_name='votes')
