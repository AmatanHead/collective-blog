from django.db import models
from collective_blog import settings

from django.utils.translation import ugettext_lazy as _


class Profile(models.Model):
    """Additional model which holds profile data for each user.

    You should not select users by this model's primary key or by
    `User` model's primary key.

    Use `User.username` field instead of primary keys.

    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='profile')

    location = models.CharField(max_length=100, blank=True,
                                verbose_name=_('Location'))

    birthday = models.DateField(null=True,
                                verbose_name=_('Birthday'))

    about_source = models.TextField(blank=True,
                                    verbose_name=_('About'),
                                    help_text=_('Tell us about yourself'))

    about_html = models.TextField(blank=True)

    email_is_public = models.BooleanField(verbose_name=_('Show email'), default=False)

    # To go: karma, votes, liked tags

    @classmethod
    def can_edit_profile(cls, user, profile):
        return (user.pk == profile.user.pk or
                user.has_perm('user.can_change_profile') or
                user.has_perm('auth.can_change_user'))

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ("user", )

    def __str__(self):
        return self.user.username
