from django.db.models import Q, Sum
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404, HttpResponse

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect

from django.utils.translation import ugettext_lazy as _

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


def post(request, post_slug=None):
    post = get_object_or_404(Post.objects.select_related('author', 'blog'),
                             slug=post_slug)

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
        return render(request, 'blog/message_draft.html',
                      status=404)
    elif membership is None:
        return render(request, 'blog/message_no_access.html',
                      status=403)
    elif membership.is_banned():
        return render(request, 'blog/message_banned.html',
                      status=403)
    else:
        raise Http404()


@csrf_protect
def vote(request, post_slug=None):
    post = get_object_or_404(Post.objects.select_related('author'),
                             slug=post_slug)

    # noinspection PyBroadException
    try:
        v = int(request.GET['vote'])
        assert v in [0, 1, -1]
    except Exception:
        return HttpResponse(_('Wrong vote'))

    if request.user.is_anonymous():
        return HttpResponse(_("You should be logged in"))

    if not request.user.is_active:
        return HttpResponse(_("Your account is disabled"))

    if request.user.pk == post.author.pk:
        return HttpResponse(_("You can't vote for your own post"))

    membership = post.blog.check_membership(request.user)

    if post.can_be_voted_by(request.user, membership):
        PostVote.vote_for(request.user, post, v)
        return HttpResponse(str(PostVote.objects.filter(object=post).score()['score']))
    else:
        return HttpResponse(_("You can't vote for this post"))
