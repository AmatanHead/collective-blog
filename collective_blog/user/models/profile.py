from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _, ugettext as __

from collective_blog import settings
from collective_blog.utils.errors import PermissionCheckFailed

from s_voting.models import VoteCacheField
from .karma import Karma

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


def _karma_cache_query(v):
    return Q(pk=v.object.profile.pk)


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

    karma = VoteCacheField(Karma)

    # Common methods
    # --------------

    def delete(self, using=None, keep_parents=False):
        self.user.delete()
        super(Profile, self).delete(using, keep_parents)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ("user",)

    def __str__(self):
        return str(self.user)

    # Permissions control
    # -------------------

    @staticmethod
    def can_be_moderated_by(user):
        """Check if the user is a moderator with profile editing rights"""
        return user.is_active and user.is_staff and (
            user.has_perm('user.change_profile') or
            user.has_perm('auth.change_user'))

    def can_be_edited_by(self, user):
        """Check if this profile can be edited by the user

        Only moderators and the owner of the profile can edit it.

        """
        return user.is_active and (user.pk == self.user.pk or
                                   self.can_be_moderated_by(user))

    def email_can_be_seen_by(self, user):
        """Check if the email field can be seen by the user

        Only moderators and the owner of the profile
        can see the email if it is private.

        """
        return (self.email_is_public or user.pk == self.user.pk or
                self.can_be_moderated_by(user))

    def email_as_seen_by(self, user):
        """Returns the email with a little annotation for private emails

        E.g. `a.b@c.d (Only you can see the email)`.

        """
        if not self.user.email:
            return ''
        if self.email_can_be_seen_by(user) and not self.email_is_public:
            return self.user.email + ' (%s)' % __('Only you can see the email')
        elif self.email_is_public:
            return self.user.email
        return ''

    def can_be_voted_by(self, user):
        """Check if this profile can bo voted by the user passed"""
        return user.is_active and user.pk != self.user.pk and self.user.is_active

    # Actions
    # -------

    def switch_is_active(self, moderator):
        """Block or unblock user if the moderator have proper permissions"""
        if self.user.pk == moderator.pk:
            raise PermissionCheckFailed(__("You can't use this action "
                                           "on yourself."))
        if not self.can_be_moderated_by(moderator):
            raise PermissionCheckFailed(__("Sorry, you have no permissions "
                                           "to edit this profile."))

        self.user.is_active = not self.user.is_active
        self.user.save()
