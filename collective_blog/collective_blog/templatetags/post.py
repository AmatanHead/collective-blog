from django import template
from django.core.urlresolvers import reverse
from django.utils import timezone

from datetime import timedelta

register = template.Library()


@register.inclusion_tag('blog/tags/post_preview.html')
def post_preview(post, interesting_blogs, hide_threshold=-20):
    color = ''
    if post.blog and post.blog.id in interesting_blogs:
        color = interesting_blogs[post.blog.id].color
    return dict(post=post, color=color, hide_threshold=hide_threshold)

@register.inclusion_tag('blog/tags/post_header.html')
def post_header(post, color='', big_title=False):
    if post.created:
        show_full_date = timezone.now() - timedelta(days=2) > post.created
    else:
        show_full_date = True
    return dict(post=post, show_full_date=show_full_date, color=color, big_title=big_title)

@register.inclusion_tag('blog/tags/post_navigation.html')
def post_navigation(current_page, pages, view_name, **url_kwargs):
    context = {
        'current_page': current_page,
        'view_name': view_name,
    }
    # {% url view_name page=current_page.next_page_number %}

    if current_page.has_previous():
        context['prev_url'] = reverse(
            view_name, kwargs=dict(
                page=current_page.previous_page_number(), **url_kwargs))

    if current_page.has_next():
        context['next_url'] = reverse(
            view_name, kwargs=dict(
                page=current_page.next_page_number(), **url_kwargs))

    context['pages'] = [(page,
                         reverse(view_name,
                                 kwargs=dict(page=page, **url_kwargs)))
                        for page in pages]

    return context
