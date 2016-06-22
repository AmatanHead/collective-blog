from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import DetailView, CreateView, DeleteView, UpdateView

from collective_blog.forms import PostForm, PostCreateForm
from collective_blog.models import Post, PostVote, Blog
from s_voting.views import VoteView


class GenericPostView(DetailView):
    def dispatch(self, request, *args, **kwargs):
        self.post_slug = kwargs.pop('post_slug')

        if self.post_slug != self.post_slug.lower():
            return HttpResponsePermanentRedirect(
                reverse('view_post',
                        kwargs=dict(post_slug=self.post_slug.lower())))

        return super(GenericPostView, self).dispatch(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Post.objects.select_related('author'),
                                 slug=self.post_slug)

    def get_context_data(self, **kwargs):
        context = super(GenericPostView, self).get_context_data(**kwargs)
        context['rating'] = {
            'model': PostVote,
            'user': self.request.user,
            'obj': self.object,
            'disabled': self.request.user.is_anonymous(),
            'use_colors': False,
        }
        if self.object.blog:
            context['membership'] = self.object.blog.check_membership(self.request.user)
        context['can_delete_posts'] = self.request.user.has_perm('collective_blog.delete_post')
        context['can_edit_posts'] = self.request.user.has_perm('collective_blog.edit_post')
        return context


class PostView(GenericPostView):
    model = Post

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        if self.object.blog is not None:
            membership = self.object.blog.check_membership(self.request.user)
        else:
            membership = None

        if self.object.can_be_seen_by_user(self.request.user, membership):
            self.template_name = 'collective_blog/post_detail.html'
            self.status = 200
        else:
            self.template_name = 'collective_blog/post_denied.html'
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
        return super(VotePostView, self).dispatch(request, *args, **kwargs)

    def get_score(self):
        self.object.refresh_from_db()
        return self.object.rating

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Post.objects.select_related('author'),
                                 slug=self.post_slug)


@method_decorator(login_required, 'dispatch')
class CreatePostView(CreateView):
    form_class = PostForm
    template_name = 'collective_blog/post_create.html'
    model = Post

    def get_success_url(self, obj=None):
        return reverse('view_post',
                       kwargs=dict(post_slug=self.object.slug))

    def get_initial(self):
        return dict(author=self.request.user)

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request,
                         _('"%(post)s" post was created') % dict(post=self.object.heading))
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, 'dispatch')
class EditPostView(GenericPostView, UpdateView):
    form_class = PostCreateForm
    template_name = 'collective_blog/post_edit.html'
    model = Post
    slug_url_kwarg = 'post_slug'

    def get_success_url(self, obj=None):
        return reverse('view_post',
                       kwargs=dict(post_slug=self.object.slug))

    def get_initial(self):
        return dict(author=self.object.author,
                    blog=self.object.blog)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(created=self.object.created is not None,
                          **self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request,
                         _('"%(post)s" post was saved') % dict(post=self.object.heading))
        return HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if (self.object.author == self.request.user or
                self.request.user.has_perm('collective_blog.delete_post')):
            return super(EditPostView, self).get(request, *args, **kwargs)
        else:
            messages.error(self.request, _('You can\'t perform this action'))
            return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if (self.object.author == self.request.user or
                self.request.user.has_perm('collective_blog.delete_post')):
            return super(EditPostView, self).post(request, *args, **kwargs)
        else:
            messages.error(self.request, _('You can\'t perform this action'))
            return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, 'dispatch')
class DeletePostView(GenericPostView, DeleteView):
    template_name = 'collective_blog/post_delete_confirm.html'
    model = Post
    slug_url_kwarg = 'post_slug'

    def get_success_url(self, obj=None):
        return reverse('homepage')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.blog is not None:
            membership = self.object.blog.check_membership(request.user)
        else:
            membership = None
        if (request.user == self.object.author or
                Blog.check_can_delete_posts(membership) or
                self.request.user.has_perm('collective_blog.delete_post')):
            return super(DeletePostView, self).get(request, *args, **kwargs)
        else:
            messages.error(self.request, _('You can\'t perform this action'))
            return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.blog is not None:
            membership = self.object.blog.check_membership(request.user)
        else:
            membership = None
        if (request.user == self.object.author or
                Blog.check_can_delete_posts(membership) or
                self.request.user.has_perm('collective_blog.delete_post')):
            return super(DeletePostView, self).post(request, *args, **kwargs)
        else:
            messages.error(self.request, _('You can\'t perform this action'))
            return HttpResponseRedirect(self.get_success_url())
