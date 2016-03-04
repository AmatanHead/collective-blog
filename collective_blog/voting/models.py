from django.db import models
from django.db.models import Sum, Count, QuerySet, ObjectDoesNotExist

from collective_blog import settings


class VotesQuerySet(QuerySet):
    """
    Queryset of votes.

    Allows for routine operations like getting overall rating etc.

    """
    def score(self):
        """
        Sum all votes.

        :return: A dictionary containing `score` and `num_votes` keys.
        """
        result = self.aggregate(
            score=Sum('vote'),
            num_votes=Count('vote')
        )

        if result['score'] is None:
            result['score'] = 0

        return result


class VoteManager(models.Manager):
    """
    Wrap objects to the `VotesQuerySet`.

    """
    def get_queryset(self):
        return VotesQuerySet(self.model)


class AbstractVote(models.Model):
    """
    A vote on an object by a User.

    """

    SCORES = (
        (+1, '+1'),
        (-1, '-1'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='votes_for_%(app_label)s_%(class)s')
    vote = models.SmallIntegerField(choices=SCORES)
    object = None  # Should be overloaded

    objects = VoteManager()

    class Meta:
        unique_together = (('user', 'object'), )
        abstract = True

    def __str__(self):
        return '%s: %s on %s' % (self.user, self.vote, self.object)

    @classmethod
    def vote_for(cls, user, obj, vote):
        """
        Create or update a vote.

        :param user: Who votes.
        :param obj: For what votes.
        :param vote: +1, 0, or -1.

        """
        assert vote in [-1, 0, 1]

        if vote == 0:
            cls.objects.filter(user=user, object=obj).delete()
        else:
            try:
                v = cls.objects.get(user=user, object=obj)
                v.vote = vote
                v.save()
            except ObjectDoesNotExist:
                cls.objects.create(user=user, object=obj, vote=vote)
