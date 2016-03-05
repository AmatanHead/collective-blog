from django.db.models import Q, Sum
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404

from ..models import Blog, Post


def feed(request, page=1):
    if 'per_page' in request.GET:
        per_page = request.GET['per_page']
    else:
        per_page = 10

    if request.user.is_anonymous():
        all_posts = (Post.objects.prefetch_related('author', 'blog')
                     .filter(blog__type='O', is_draft=False)
                     .annotate(rating=Sum('votes__vote'))
                     .all())
    else:
        all_posts = (Post.objects.prefetch_related('author', 'blog')
                     .filter(Q(blog__type='O') | Q(blog__members=request.user), is_draft=False)
                     .annotate(rating=Sum('votes__vote'))
                     .all())

    try:
        page = int(page)
        paginator = Paginator(all_posts, per_page)
    except ValueError:
        raise Http404()

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        raise Http404()
    except EmptyPage:
        raise Http404()

    pages = range(max(1, page - 10), min(page + 10, paginator.num_pages) + 1)

    return render(request, 'blog/feed.html', {
        'pages': pages,
        'posts': posts,
        'interesting_blogs': {},
        'interesting_tags': {},
    })
