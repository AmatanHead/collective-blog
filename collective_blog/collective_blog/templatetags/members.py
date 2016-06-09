from django import template

register = template.Library()


@register.inclusion_tag('blog/tags/member.html')
def render_membership(membership, render_karma=True):
    return dict(membership=membership, render_karma=render_karma)
