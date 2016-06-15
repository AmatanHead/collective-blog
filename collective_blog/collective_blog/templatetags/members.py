from django import template

register = template.Library()


@register.inclusion_tag('blog/tags/member.html')
def render_membership(membership, self_membership, render_rating=True, render_karma=True):
    return dict(
        membership=membership,
        self_membership=self_membership,
        render_karma=render_karma,
        render_rating=render_rating,
    )
