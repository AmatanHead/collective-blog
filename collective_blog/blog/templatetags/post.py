from django import template

register = template.Library()

@register.inclusion_tag('blog/tags/post_preview.html')
def post_preview(post):
    return dict(post=post)
