from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext as __

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


class Profile(models.Model):
    """Additional model which holds profile data for each user

    You should not select users by this model's primary key or by
    `User` model's primary key.

    Use `User.username` field instead of primary keys.

    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='profile',
                                editable=False)

    location = models.CharField(max_length=100, blank=True,
                                verbose_name=_('Location'))

    # TODO proper widget
    birthday = models.DateField(null=True, blank=True,
                                verbose_name=_('Birthday'))

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

    email_is_public = models.BooleanField(verbose_name=_('Show email'),
                                          default=False)

    # To go: liked tags

    def can_be_edited_by(self, user):
        has_perms = user.is_active and user.is_staff and (
            user.has_perm('user.change_profile') or
            user.has_perm('auth.change_user'))

        return user.is_active and (user.pk == self.user.pk or has_perms)

    def email_can_be_seen_by(self, user):
        has_perms = user.is_active and user.is_staff and (
            user.has_perm('user.change_profile') or
            user.has_perm('auth.change_user'))

        return self.email_is_public or user.pk == self.user.pk or has_perms

    def email_as_seen_by(self, user):
        if not self.user.email:
            return ''
        if self.email_can_be_seen_by(user) and not self.email_is_public:
            return self.user.email + ' (' + __('Only you can see the email') + ')'
        elif self.email_is_public:
            return self.user.email
        return ''

    def can_be_voted_by(self, user):
        return user.is_active and user.pk != self.user.pk

    def delete(self, using=None, keep_parents=False):
        self.user.delete()
        super(Profile, self).delete(using, keep_parents)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ("user",)

    def __str__(self):
        return str(self.user)
