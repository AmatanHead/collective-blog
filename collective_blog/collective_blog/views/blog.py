from operator import itemgetter

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponsePermanentRedirect, HttpResponse, \
    HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View, UpdateView
from django.views.generic.base import TemplateResponseMixin

from collective_blog.models import Blog, Membership, Post
from collective_blog.utils.errors import PermissionCheckFailed

from .feed import GenericFeedView
from ..forms import BlogForm


class GenericBlogView(View):
    def dispatch(self, request, *args, **kwargs):
        self.blog_slug = kwargs.pop('blog_slug')

        if self.blog_slug != self.blog_slug.lower():
            return HttpResponsePermanentRedirect(
                reverse('view_blog',
                        kwargs=dict(blog_slug=self.blog_slug.lower())))

        self.object = self.get_object(*args, **kwargs)

        return super(GenericBlogView, self).dispatch(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Blog.objects,
                                 slug=self.blog_slug)


class BlogView(GenericBlogView, GenericFeedView):
    template_name = 'blog/blog.html'

    def get_context_data(self, **kwargs):
        context = super(BlogView, self).get_context_data(**kwargs)
        membership = self.object.check_membership(self.request.user)
        context['blog'] = self.object
        context['membership'] = membership
        context['is_banned'] = self.object.is_banned(membership)
        context['can_join'] = self.object.check_can_join(self.request.user)
        context['colors'] = Membership.COLORS
        context['current_color'] = membership.color if membership else ''
        context['members'] = Membership.objects.filter(blog=self.object).count()
        context['posts'] = Post.objects.filter(blog=self.object).count()
        context['is_moderator'] = Blog.can_be_moderated_by(self.request.user)
        return context

    def get_queryset(self):
        return super(BlogView, self).get_queryset().filter(blog=self.object)


@method_decorator(csrf_protect, 'dispatch')
class JoinBlogView(GenericBlogView):
    def post(self, request, *args, **kwargs):
        try:
            msg = self.object.join(self.request.user)
            messages.success(self.request, msg)
        except PermissionCheckFailed as e:
            return HttpResponse(e.note, status=400)

        return HttpResponseRedirect(
            reverse('view_blog',
                    kwargs=dict(blog_slug=self.blog_slug.lower()))
        )


@method_decorator(csrf_protect, 'dispatch')
class LeaveBlogView(GenericBlogView, TemplateResponseMixin):
    template_name = "blog/blog_leave.html"

    def post(self, request, *args, **kwargs):
        self.object.leave(self.request.user)

        return HttpResponseRedirect(
            reverse('view_blog',
                    kwargs=dict(blog_slug=self.blog_slug.lower()))
        )

    def get(self, request, *args, **kwargs):
        membership = self.object.check_membership(self.request.user)
        if membership is None or membership.is_left() or membership.role == 'O':
            return HttpResponseRedirect(
                reverse('view_blog',
                        kwargs=dict(blog_slug=self.blog_slug.lower()))
            )

        return self.render_to_response(dict(
            blog=self.object,
            membership=membership
        ))


@method_decorator(csrf_protect, 'dispatch')
class UpdateColorBlogView(GenericBlogView):
    def post(self, request, *args, **kwargs):
        membership = self.object.check_membership(self.request.user)
        try:
            color = request.POST['color']
            assert color in map(itemgetter(0), Membership.COLORS)
        except (KeyError, AssertionError):
            return HttpResponse('Wrong color', status=400)
        if membership is not None:
            membership.color = color
            membership.save()

        return HttpResponseRedirect(
            reverse('view_blog',
                    kwargs=dict(blog_slug=self.blog_slug.lower()))
        )


class EditBlogView(UpdateView):
    form_class = BlogForm
    template_name = 'blog/blog_update.html'
    model = Blog
    slug_url_kwarg = 'blog_slug'

    def get_success_url(self, obj=None):
        if obj is None:
            obj = self.object
        return reverse('view_blog',
                       kwargs=dict(blog_slug=obj.slug))

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.membership = self.object.check_membership(self.request.user)
        if (self.object.check_can_change_settings(self.membership) or
                Blog.can_be_moderated_by(self.request.user)):
            return super(EditBlogView, self).dispatch(request, *args, **kwargs)
        else:
            messages.error(self.request, _('You can\'t perform this action'))
            return HttpResponseRedirect(self.get_success_url(self.object))

    def get_context_data(self, **kwargs):
        context = super(EditBlogView, self).get_context_data(**kwargs)
        context.update(dict(
            membership=self.membership,
            is_moderator=Blog.can_be_moderated_by(self.request.user)
        ))
        return context
