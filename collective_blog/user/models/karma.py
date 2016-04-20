from django.db import models
from django.utils.translation import ugettext as __

from collective_blog import settings
from collective_blog.utils.errors import PermissionCheckFailed
from s_voting.models import AbstractVote


class Karma(AbstractVote):
    """Votes for user (karma)"""

    object = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='karma')

    @classmethod
    def vote_for(cls, user, obj, vote):
        if user.pk == obj.pk:
            raise PermissionCheckFailed(__("You can't vote for yourself"))

        if not obj.profile.can_be_voted_by(user):
            raise PermissionCheckFailed(__("You can't vote for this user"))

        super(Karma, cls).vote_for(user, obj, vote)
