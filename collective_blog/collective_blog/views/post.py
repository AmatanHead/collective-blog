from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import DetailView

from collective_blog.models import Post, PostVote
from s_voting.views import VoteView


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
            self.template_name = 'blog/post_detail.html'
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