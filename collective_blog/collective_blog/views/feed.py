from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, DetailView
from django.utils.translation import ugettext_lazy as _

from collective_blog.models import Post, PostVote, Membership
from s_voting.views import VoteView


class GenericFeedView(ListView):
    """This is the mixin for displaying a feed

    Overload `get_queryset` and `get_context_data` to alter the results.

    """

    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(GenericFeedView, self).get_context_data(**kwargs)

        if self.paginate_by:
            page_obj = context['page_obj']
            frm = max(1, page_obj.number - 5)
            to = min(page_obj.number + 5, page_obj.paginator.num_pages) + 1
            context['pages'] = range(frm, to)

        if self.request.user.is_anonymous():
            context['interesting_blogs'] = []
        else:
            context['interesting_blogs'] = {
                m.blog.id: m for m in Membership.objects.filter(user=self.request.user).exclude(role__in=['L', 'LB'])
            }

        return context

    def get_queryset(self):
        """Returns a queryset of posts that are visible to a user"""
        return (Post.objects
                .select_related('author', 'blog')
                .filter(
                    Q(blog__type='O') | (
                        Q(blog__members=self.request.user) &
                        Q(blog__membership__role__in=['O', 'M', 'A'])
                    ) if not self.request.user.is_anonymous() else (
                        Q(blog__type='O')
                    ),
                    is_draft=False)
                .distinct())


class FeedView(GenericFeedView):
    template_name = 'blog/feed.html'


class PostView(DetailView):
    model = Post

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
        context['rating'] = {
            'model': PostVote,
            'user': self.request.user,
            'obj': self.object,
            'disabled': self.request.user.is_anonymous(),
            # 'color_threshold': [0, 0],
            'use_colors': False,
        }
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if self.object.blog is not None:
            membership = self.object.blog.check_membership(self.request.user)
        else:
            membership = None

        if self.object.can_be_seen_by_user(self.request.user, membership):
            self.template_name = 'blog/post.html'
            self.status = 200
        else:
            self.template_name = 'blog/post_message_fail.html'
            self.status = 403
            if self.object.is_draft:
                context['note'] = _('The author has hidden this post.')
            elif membership is None:
                context['note'] = _('You should be a member of the '
                                    '"%(blog)s" blog to view this post.' %
                                    {'blog': self.object.blog.name})
            elif membership.is_banned():
                context['note'] = _('Your account is banned in the '
                                    '"%(blog)s" blog. You can\'t '
                                    'see this post.' %
                                    {'blog': self.object.blog.name})
            else:
                context['note'] = _('You have no access to this page.')

        return self.render_to_response(context)


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

    def get_score(self):
        self.object.refresh_from_db()
        return self.object.rating

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Post.objects.select_related('author'),
                                 slug=self.post_slug)
