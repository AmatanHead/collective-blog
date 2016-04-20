from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from django.http import Http404, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, DetailView

from collective_blog.models import Post, PostVote
from s_voting.views import VoteView


class FeedView(ListView):
    paginate_by = 1
    template_name = 'blog/feed.html'

    def get_queryset(self):
        if self.request.user.is_anonymous():
            return (Post.objects.prefetch_related('author', 'blog')
                    .filter(blog__type='O', is_draft=False)
                    .annotate(rating=Sum('votes__vote'))
                    .all())
        else:
            return (Post.objects.prefetch_related('author', 'blog')
                    .filter(
                        Q(blog__type='O') | Q(blog__members=self.request.user),
                        is_draft=False)
                    .annotate(rating=Sum('votes__vote'))
                    .all())

    def get_context_data(self, **kwargs):
        context = super(FeedView, self).get_context_data(**kwargs)
        page_obj = context['page_obj']
        frm = max(1, page_obj.number - 5)
        to = min(page_obj.number + 5, page_obj.paginator.num_pages) + 1
        context['pages'] = range(frm, to)
        return context


class PostView(DetailView):
    model = Post
    template_name = 'blog/post.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_slug = kwargs.pop('post_slug')

        if self.post_slug != self.post_slug.lower():
            return HttpResponsePermanentRedirect(
                reverse('view_post',
                        kwargs=dict(post_slug=self.post_slug.lower())))

        return super(PostView, self).dispatch(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Post.objects.select_related('author'),
                                 slug=self.post_slug)

    def get_context_data(self, **kwargs):
        context = super(PostView, self).get_context_data(**kwargs)
        return context


def post(request, post_slug=None):
    if post_slug != post_slug.lower():
        return HttpResponsePermanentRedirect(
            reverse('view_post', kwargs=dict(post_slug=post_slug.lower())))

    post = get_object_or_404(Post.objects.select_related('author', 'blog'),
                             slug=post_slug)

    membership = post.blog.check_membership(request.user)

    if post.can_be_seen_by_user(request.user, membership):
        rating = PostVote.objects.filter(object=post).score()

        if request.user.is_anonymous():
            self_vote = None
        else:
            self_vote = PostVote.objects.filter(object=post,
                                                user=request.user).first()

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


@method_decorator(csrf_protect, 'dispatch')
class VotePostView(VoteView):
    model = PostVote

    def dispatch(self, request, *args, **kwargs):
        self.post_slug = kwargs.pop('post_slug')

        if self.post_slug != self.post_slug.lower():
            return HttpResponsePermanentRedirect(
                reverse('view_post',
                        kwargs=dict(post_slug=self.post_slug.lower())))

        return super(VotePostView, self).dispatch(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Post.objects.select_related('author'),
                                        slug=self.post_slug)
