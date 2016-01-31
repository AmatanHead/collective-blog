from django.db import models
from collective_blog import settings

from django.utils.translation import ugettext as _


class Profile(models.Model):
    """Additional model which holds profile data for each user"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='profile')

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ("user", )

    def __str__(self):
        return self.user.username
