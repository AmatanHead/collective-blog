from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext as __

from datetime import datetime

from collective_blog import settings

from dj_markdown.models import MarkdownField, HtmlCacheField
from dj_markdown.datatype import Markdown
from dj_markdown.renderer import BaseRenderer
from dj_markdown.extensions import (FencedCodeExtension,
                                    EscapeHtmlExtension,
                                    SemiSaneListExtension,
                                    StrikethroughExtension,
                                    AutomailExtension,
                                    AutolinkExtension,
                                    CommentExtension)


class Blog(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name=_('Name'),
                            unique=True)
    slug = models.SlugField(max_length=100,
                            verbose_name=_("Blog's url"),
                            unique=True)

    about = MarkdownField(blank=True,
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
                                  CommentExtension(),
                              ]
                          ),
                          verbose_name=_('About'),
                          help_text=_('Tell us about yourself '
                                      '(use the markdown, Luke!)'))

    _about_html = HtmlCacheField(about)

    TYPES = (
        ('O', _('Open')),
        ('P', _('Private')),
    )

    type = models.CharField(max_length=2, default='0', choices=TYPES,
                            verbose_name=_('Type of the blog'))

    JOIN_CONDITIONS = (
        ('A', _('Anyone can join')),
        ('K', _('Only users with high karma can join')),
        ('I', _('Manual approval required'))
    )

    join_condition = models.CharField(max_length=2, default='A',
                                      choices=JOIN_CONDITIONS,
                                      verbose_name=_('Who can join the blog'))

    join_karma_threshold = models.SmallIntegerField(default=0,
                                                    verbose_name=_(
                                                        'Join karma threshold'))

    POST_CONDITIONS = (
        ('A', _('Anyone can add post')),
        ('K', _('Only users with high karma can add post')),
    )

    post_condition = models.CharField(max_length=2, default='A',
                                      choices=POST_CONDITIONS,
                                      verbose_name=_('Who can add posts'))

    post_membership_required = models.BooleanField(
        default=False, verbose_name=_('Require membership to write posts'))

    post_karma_threshold = models.SmallIntegerField(
        default=0, verbose_name=_('Post karma threshold'))

    COMMENT_CONDITIONS = (
        ('A', _('Anyone can comment')),
        ('K', _('Only users with high karma can comment')),
    )

    comment_condition = models.CharField(max_length=2, default='A',
                                         choices=COMMENT_CONDITIONS,
                                         verbose_name=_('Who can comment in the blog'))

    comment_membership_required = models.BooleanField(
        default=False, verbose_name=_('Require membership to write comments'))

    comment_karma_threshold = models.SmallIntegerField(
        default=0, verbose_name=_('Comment karma threshold'))

    members = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     through='Membership',
                                     editable=False)

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ("name",)

    def __str__(self):
        return str(self.name)


class Membership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             models.CASCADE)
    blog = models.ForeignKey(Blog,
                             models.CASCADE)

    ROLES = (
        ('O', _('Owner')),
        ('M', _('Member')),
        ('B', _('Banned')),
        ('A', _('Administrator'))
    )

    ban_expiration = models.DateTimeField(auto_now_add=True,
                                          editable=False)

    role = models.CharField(max_length=2, choices=ROLES, default='M')

    can_change_settings = models.BooleanField(
        default=False, verbose_name=_("Can change blog's settings"))

    can_edit_posts = models.BooleanField(
        default=False, verbose_name=_("Can edit posts"))
    can_delete_posts = models.BooleanField(
        default=False, verbose_name=_("Can delete posts"))

    can_edit_comments = models.BooleanField(
        default=False, verbose_name=_("Can edit comments"))
    can_delete_comments = models.BooleanField(
        default=False, verbose_name=_("Can delete comments"))

    can_ban = models.BooleanField(
        default=False, verbose_name=_("Can ban a member"))

    def can_be_banned(self):
        return self.role not in ['O', 'A']

    @classmethod
    def ban_permanently(cls, blog, user):
        membership = cls.objects.filter(user=user, blog=blog).first()

        if membership is None:
            membership = Membership(user=user, blog=blog)

        if membership.can_be_banned():
            membership.role = 'B'
            membership.save()

    @classmethod
    def ban(cls, blog, user, timedelta):
        membership = cls.objects.filter(user=user, blog=blog).first()

        if membership is None:
            membership = Membership(user=user, blog=blog)

        if membership.can_be_banned():
            membership.ban_expiration = datetime.now() + timedelta
            membership.save()

    def is_banned(self):
        return self.role != 'B' and self.ban_expiration < datetime.now()

    def check_can_change_settings(self):
        return (self.role in ['O', 'A'] and
                not self.is_banned() and
                self.check_can_change_settings)

    def check_can_edit_posts(self):
        return (self.role in ['O', 'A'] and
                not self.is_banned() and
                self.check_can_edit_posts)

    def check_can_delete_posts(self):
        return (self.role in ['O', 'A'] and
                not self.is_banned() and
                self.check_can_delete_posts)

    def check_can_edit_comments(self):
        return (self.role in ['O', 'A'] and
                not self.is_banned() and
                self.check_can_edit_comments)

    def check_can_delete_comments(self):
        return (self.role in ['O', 'A'] and
                not self.is_banned() and
                self.check_can_delete_comments)

    def check_can_ban(self):
        return (self.role in ['O', 'A'] and
                not self.is_banned() and
                self.check_can_ban)

    class Meta:
        unique_together = ('user', 'blog')
