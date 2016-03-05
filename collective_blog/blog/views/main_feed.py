from django.db.models import Q, Sum
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404

from django.shortcuts import get_object_or_404

from ..models import Post, PostVote


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

def post(request, post_id=None):
    post = get_object_or_404(Post.objects.select_related('author', 'blog'),
                             pk=post_id)

    membership = post.blog.check_membership(request.user)

    if post.can_be_seen_by_user(request.user, membership):
        rating = PostVote.objects.filter(object=post).score()

        if request.user.is_anonymous():
            self_vote = None
        else:
            self_vote = PostVote.objects.filter(object=post, user=request.user).first()

        return render(request, 'blog/post.html', {
            'post': post,
            'rating': rating,
            'self_vote': self_vote,
        })
    elif post.is_draft:
        return render(request, 'blog/draft_message.html',
                      status=404)
    elif membership is None:
        return render(request, 'blog/no_access_message.html',
                      status=403)
    else:
        raise Http404()

