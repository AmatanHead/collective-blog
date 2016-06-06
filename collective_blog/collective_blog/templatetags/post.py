from django import template
from django.utils import timezone

from datetime import timedelta

register = template.Library()


@register.inclusion_tag('blog/tags/post_preview.html')
def post_preview(post):
    return dict(post=post)

@register.inclusion_tag('blog/tags/post_header.html')
def post_header(post):
    show_full_date = timezone.now() - timedelta(days=2) > post.created
    return dict(post=post, show_full_date=show_full_date)
