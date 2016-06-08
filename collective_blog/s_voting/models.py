"""Abstract base for implementing voting subsystems"""

from django.db import models
from django.db.models import Sum, Count, QuerySet, ObjectDoesNotExist, F, Q
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

        try:
            v = cls.objects.get(user=user, object=obj)
            delta = vote - v.vote
            if vote == 0:
                v.delete()
            else:
                v.vote = vote
                v.save()
        except ObjectDoesNotExist:
            if vote != 0:
                delta = vote
                v = cls.objects.create(user=user, object=obj, vote=vote)
            else:
                return

        if delta != 0:
            print(delta, cls._caches)
            for (base_model, field_name), query in cls._caches.items():
                query = query(v)
                base_model.objects.filter(query).update(
                    **{field_name: F(field_name) + delta}
                )

    @classmethod
    def _register(cls, field_name, base_model, query):
        if not hasattr(cls, '_caches'):
            cls._caches = {}
        cls._caches[(base_model, field_name)] = query


def _default_cache_query(v):
    return Q(pk=v.object.pk)


class VoteCacheField(models.PositiveSmallIntegerField):
    def __init__(self, vote_model, query=_default_cache_query, default=0):
        """A field that caches the sum of all votes for a particular object

        Whenever an object voted using the `vote_model` model,
        all objects that match a `query` will be updated.

        """
        self.vote_model = vote_model
        self.query = query
        super().__init__(default=default, editable=False)

    def deconstruct(self):
        """Returns enough information to recreate the field"""
        name, path, args, kwargs = super(VoteCacheField, self).deconstruct()
        kwargs.update(dict(vote_model=self.vote_model, query=self.query))
        kwargs.pop('editable')

        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, virtual_only=False):
        super(VoteCacheField, self).contribute_to_class(cls, name, virtual_only)
        # noinspection PyProtectedMember
        self.vote_model._register(self.name, cls, self.query)
