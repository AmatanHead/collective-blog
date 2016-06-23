import json

from django import template

register = template.Library()


class VoteData(object):
    def __init__(self, model, user, obj,
                 use_colors=True, color_tags=None, color_threshold=None,
                 disabled=False,
                 score=None):
        """Holds data about object rating and user's vote

        Used in voting template tag.

        :param model: Model which store votes (derived from `AbstractVote`)
        :param user:
        :param obj:
        :param use_colors: If False, middle ('gray') color will be used
        :param color_tags: CSS tags used in template tags
          for coloring the rating box
        :param color_threshold: A range in which a color of the rating box
          becomes gray
        :param disabled: render buttons as disabled

        """
        self.model = model
        self.obj = obj
        self.user = user
        self.use_colors = use_colors
        self.disabled = disabled

        if color_tags is None:
            self.color_tags = ['green', 'gray', 'orange']
        else:
            self.color_tags = color_tags

        if color_threshold is None:
            self.color_threshold = [-10, 10]
        else:
            self.color_threshold = color_threshold

        if score is not None:
            self.score = score
        else:
            self.score = self.model.objects.filter(object=obj).score()

        self._color = None
        self._self_vote = None

    @property
    def meta(self):
        return json.dumps({
            'use_colors': self.use_colors,
            'color_tags': self.color_tags,
            'color_threshold': self.color_threshold,
            'disabled': self.disabled,
            'state': self.self_vote,
        })

    @property
    def self_vote(self):
        """Returns vote, if the user has already made his choice"""
        if self._self_vote is not None:
            return self._self_vote

        if self.user.is_anonymous():
            self._self_vote = 0
        else:
            vote = self.model.objects.filter(
                object=self.obj, user=self.user).first()
            self._self_vote = 0 if vote is None else vote.vote

        return self._self_vote


@register.inclusion_tag('s_voting/tags/vote.html')
def vote(name, prefix, url, data, score=None):
    """Display voting buttons

    :param name: Localized parameter name (e.g. rating, karma)
    :param prefix: Prefix for all html tag ids
    :param url: Where to submit data
    :param data: dict --
      * model: Model which store votes (derived from `AbstractVote`)
      * user: who votes
      * obj: for what
      * use_colors: If False, middle ('gray') color will be used
      * color_tags: CSS tags used in template tags
        for coloring the rating box
      * color_threshold: A range in which a color of the rating box
        becomes gray
      * disabled: render buttons as disabled
    :param score: int -- current rating of an object. Pass in a cached value
    to avoid dynamic lookups

    """
    return {
        'name': name,
        'prefix': prefix,
        'url': url,
        'data': VoteData(score=score, **data),
    }
