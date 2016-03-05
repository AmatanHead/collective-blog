from django.db import models

from collective_blog import settings
from voting.models import AbstractVote


class Karma(AbstractVote):
    """Votes for user (karma)"""

    object = models.ForeignKey(settings.AUTH_USER_MODEL,
                               related_name='karma')
