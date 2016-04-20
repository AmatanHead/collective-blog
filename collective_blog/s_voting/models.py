"""Abstract base for implementing voting subsystems"""

from django.db import models
from django.db.models import Sum, Count, QuerySet, ObjectDoesNotExist
from django.utils.translation import ugettext as __

from collective_blog import settings
from collective_blog.utils.errors import PermissionCheckFailed


class VotesQuerySet(QuerySet):
    """Queryset of votes

    Allows for routine operations like getting overall rating etc.

    """
    def score_query(self):
        """Aggregate score and num_votes"""
        result = self.aggregate(
            score=Sum('vote'),
            num_votes=Count('vote')
        )

        if result['score'] is None:
            result['score'] = 0

        return result

    def score(self):
        """Sum all votes"""
        return self.score_query()['score']

    def num_votes(self):
        """Count all votes"""
        return self.score_query()['num_votes']


class VoteManager(models.Manager):
    """Wrap objects to the `VotesQuerySet`"""

    def get_queryset(self):
        return VotesQuerySet(self.model)


class AbstractVote(models.Model):
    """A vote on an object by a User"""

    SCORES = (
        (+1, '+1'),
        (-1, '-1'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='votes_for_%(app_label)s_%(class)s')
    vote = models.SmallIntegerField(choices=SCORES)
    object = None  # Should be overwritten

    objects = VoteManager()

    class Meta:
        unique_together = (('user', 'object'), )
        abstract = True

    def __str__(self):
        return '%s: %s on %s' % (self.user, self.vote, self.object)

    @classmethod
    def vote_for(cls, user, obj, vote):
        """Create or update a vote

        :param user: Who votes.
        :param obj: For what votes.
        :param vote: +1, 0, or -1.

        """
        if vote not in [-1, 0, 1]:
            raise PermissionCheckFailed(__("Wrong vote"))

        if user.is_anonymous():
            raise PermissionCheckFailed(__("You should be logged in"))

        if not user.is_active:
            raise PermissionCheckFailed(__("Your account is disabled"))

        if vote == 0:
            cls.objects.filter(user=user, object=obj).delete()
        else:
            try:
                v = cls.objects.get(user=user, object=obj)
                v.vote = vote
                v.save()
            except ObjectDoesNotExist:
                cls.objects.create(user=user, object=obj, vote=vote)
