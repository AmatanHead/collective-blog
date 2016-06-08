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

        return super(GenericBlogView, self).dispatch(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Blog.objects,
                                 slug=self.blog_slug)


class BlogView(GenericBlogView, GenericFeedView):
    template_name = 'blog/blog.html'

    def get_context_data(self, **kwargs):
        context = super(BlogView, self).get_context_data(**kwargs)
        membership = self.blog.check_membership(self.request.user)
        context['blog'] = self.blog
        context['membership'] = membership
        context['is_banned'] = self.blog.is_banned(membership)
        context['can_join'] = self.blog.check_can_join(self.request.user)
        context['colors'] = Membership.COLORS
        context['current_color'] = membership.color if membership else ''
        context['members'] = Membership.objects.filter(blog=self.blog).count()
        context['posts'] = Post.objects.filter(blog=self.blog).count()
        return context

    def get_queryset(self):
        self.blog = self.get_object()
        if self.request.user.is_anonymous():
            return (Post.objects
                    .select_related('author', 'blog')
                    .filter(blog=self.blog, blog__type='O', is_draft=False)
                    .distinct()
                    .all())
        else:
            return (Post.objects
                    .select_related('author', 'blog')
                    .filter(
                        Q(blog=self.blog) &
                        (Q(blog__type='O') | Q(blog__members=self.request.user)),
                        is_draft=False)
                    .distinct()
                    .all())


@method_decorator(csrf_protect, 'dispatch')
class JoinBlogView(GenericBlogView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object(*args, **kwargs)

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
class LeaveBlogView(GenericBlogView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object(*args, **kwargs)

        self.object.leave(self.request.user)

        return HttpResponseRedirect(
            reverse('view_blog',
                    kwargs=dict(blog_slug=self.blog_slug.lower()))
        )


@method_decorator(csrf_protect, 'dispatch')
class UpdateColorBlogView(GenericBlogView):
    def post(self, request, *args, **kwargs):
        self.object = self.get_object(*args, **kwargs)

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
        obj = self.get_object()
        membership = obj.check_membership(self.request.user)
        if obj.check_can_change_settings(membership):
            return super(EditBlogView, self).dispatch(request, *args, **kwargs)
        else:
            messages.error(self.request, _('You can\'t perform this action'))
            return HttpResponseRedirect(self.get_success_url(obj))
