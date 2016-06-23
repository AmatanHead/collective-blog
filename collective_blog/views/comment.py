from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View
from django.views.generic.edit import BaseCreateView

from collective_blog.forms.comment import CommentForm
from collective_blog.models import Post, Comment, CommentVote
from s_voting.views import VoteView


@method_decorator(login_required, 'dispatch')
class CreateCommentView(BaseCreateView):
    form_class = CommentForm

    object = None

    def dispatch(self, request, *args, **kwargs):
        self.post_slug = kwargs.pop('post_slug')
        self.post_object = get_object_or_404(
            Post.objects.select_related('author'), slug=self.post_slug)

        return super(CreateCommentView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self, obj=None):
        url = reverse('view_post',
                      kwargs=dict(post_slug=self.post_object.slug))
        if self.object is not None:
            return '%s#comment__%s' % (url, str(self.object.id))
        else:
            return '%s#comment' % url

    def get_initial(self):
        return dict(author=self.request.user, post=self.post_object)

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if (self.post_object.blog is not None and not self.post_object.is_draft and
                self.post_object.blog.check_can_comment(self.request.user)):
            return super(CreateCommentView, self).post(request, *args, **kwargs)
        else:
            messages.error(self.request, _('You can\'t perform this action'))
            return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, _('Error when processing comment.'))
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(csrf_protect, 'dispatch')
class VoteCommentView(VoteView):
    model = CommentVote

    def dispatch(self, request, *args, **kwargs):
        self.comment_pk = kwargs.pop('pk')
        return super(VoteCommentView, self).dispatch(request, *args, **kwargs)

    def get_score(self):
        self.object.refresh_from_db()
        return self.object.rating

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Comment.objects,
                                 pk=self.comment_pk)


@method_decorator(csrf_protect, 'dispatch')
class ToggleHiddenCommentView(View):
    object = None

    def dispatch(self, request, *args, **kwargs):
        self.comment_pk = kwargs.pop('pk')
        self.object = get_object_or_404(Comment.objects,
                                        pk=self.comment_pk)

        return super(ToggleHiddenCommentView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self, obj=None):
        url = reverse('view_post',
                      kwargs=dict(post_slug=self.object.post.slug))
        return '%s#comment__%s' % (url, str(self.object.id))

    def get(self, request, *args, **kwargs):
        if self.object.post.blog:
            membership = self.object.post.blog.check_membership(self.request.user)
        else:
            membership = None
        is_admin = self.object.post.blog and self.object.post.blog.check_can_delete_comments(membership)
        if self.object.author == self.request.user or is_admin:
            if self.object.is_hidden:
                if (self.object.is_hidden_by_moderator and is_admin) or (not self.object.is_hidden_by_moderator and self.object.author == self.request.user):
                    self.object.is_hidden = False
                    self.object.is_hidden_by_moderator = False
            else:
                self.object.is_hidden = True
                self.object.is_hidden_by_moderator = is_admin
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())
