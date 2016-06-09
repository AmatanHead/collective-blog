from operator import itemgetter

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect, HttpResponse, \
    HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View, UpdateView, ListView
from django.views.generic.base import TemplateResponseMixin

from collective_blog.models import Blog, Membership, Post
from collective_blog.utils.errors import PermissionCheckFailed

from .feed import GenericFeedView
from ..forms import BlogForm


class GenericBlogView(View):
    """This view provides basic functionality to work with a blog

    It provides `self.blog_slug`, `self.blog`, `self.membership` objects
    by default.

    It redirects wrong-cased requests so `view_name` should be set correctly.

    """
    view_name = 'view_blog'

    def dispatch(self, request, *args, **kwargs):
        self.blog_slug = kwargs.pop('blog_slug')

        if self.blog_slug != self.blog_slug.lower():
            return HttpResponsePermanentRedirect(
                reverse(self.view_name,
                        kwargs=dict(blog_slug=self.blog_slug.lower())))

        self.blog = get_object_or_404(Blog.objects,
                                      slug=self.blog_slug)
        self.membership = self.blog.check_membership(self.request.user)

        return super(GenericBlogView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if hasattr(super(GenericBlogView, self), 'get_context_data'):
            context = super(GenericBlogView, self).get_context_data(**kwargs)
        else:
            context = {}
        context['blog'] = self.blog
        context['membership'] = self.membership
        return context


class BlogView(GenericBlogView, GenericFeedView):
    view_name = 'view_blog'

    template_name = 'blog/blog.html'

    def get_context_data(self, **kwargs):
        context = super(BlogView, self).get_context_data(**kwargs)
        context['is_banned'] = self.blog.is_banned(self.membership)
        context['can_join'] = self.blog.check_can_join(self.request.user)
        context['colors'] = Membership.COLORS
        context['current_color'] = self.membership.color if self.membership else ''
        context['members'] = Membership.objects.filter(blog=self.blog).count()
        context['posts'] = Post.objects.filter(blog=self.blog).count()
        context['is_moderator'] = Blog.can_be_moderated_by(self.request.user)

        if self.membership.role in ['O', 'A'] and self.membership.can_accept_new_users():
            context['pending'] = Membership.objects.filter(role='W', blog=self.blog).count()

        return context

    def get_queryset(self):
        return super(BlogView, self).get_queryset().filter(blog=self.blog)


@method_decorator(csrf_protect, 'dispatch')
class JoinBlogView(GenericBlogView):
    view_name = 'join_blog'

    def post(self, request, *args, **kwargs):
        try:
            msg = self.blog.join(self.request.user)
            messages.success(self.request, msg)
        except PermissionCheckFailed as e:
            return HttpResponse(e.note, status=400)

        return HttpResponseRedirect(
            reverse('view_blog',
                    kwargs=dict(blog_slug=self.blog_slug.lower()))
        )


@method_decorator(csrf_protect, 'dispatch')
class LeaveBlogView(GenericBlogView, TemplateResponseMixin):
    view_name = 'leave_blog'

    template_name = "blog/blog_leave.html"

    def post(self, request, *args, **kwargs):
        self.blog.leave(self.request.user)

        return HttpResponseRedirect(
            reverse('view_blog',
                    kwargs=dict(blog_slug=self.blog_slug.lower()))
        )

    def get(self, request, *args, **kwargs):
        if self.membership is None or self.membership.is_left() or self.membership.role == 'O':
            return HttpResponseRedirect(
                reverse('view_blog',
                        kwargs=dict(blog_slug=self.blog_slug.lower()))
            )

        return self.render_to_response(dict(
            blog=self.blog,
            membership=self.membership
        ))


@method_decorator(csrf_protect, 'dispatch')
class UpdateColorBlogView(GenericBlogView):
    view_name = 'update_color_blog'

    def post(self, request, *args, **kwargs):
        try:
            color = request.POST['color']
            assert color in map(itemgetter(0), Membership.COLORS)
        except (KeyError, AssertionError):
            return HttpResponse('Wrong color', status=400)
        if self.membership is not None:
            self.membership.color = color
            self.membership.save()

        return HttpResponseRedirect(
            reverse('view_blog',
                    kwargs=dict(blog_slug=self.blog_slug.lower()))
        )


class EditBlogView(GenericBlogView, UpdateView):
    view_name = 'edit_blog'

    form_class = BlogForm
    template_name = 'blog/blog_update.html'
    model = Blog
    slug_url_kwarg = 'blog_slug'

    def get_success_url(self, obj=None):
        if obj is None:
            obj = self.blog
        return reverse('view_blog',
                       kwargs=dict(blog_slug=obj.slug))

    def get(self, request, *args, **kwargs):
        if (self.blog.check_can_change_settings(self.membership) or
                Blog.can_be_moderated_by(self.request.user)):
            return super(EditBlogView, self).get(request, *args, **kwargs)
        else:
            messages.error(self.request, _('You can\'t perform this action'))
            return HttpResponseRedirect(self.get_success_url(self.blog))

    def post(self, request, *args, **kwargs):
        if (self.blog.check_can_change_settings(self.membership) or
                Blog.can_be_moderated_by(self.request.user)):
            return super(EditBlogView, self).post(request, *args, **kwargs)
        else:
            messages.error(self.request, _('You can\'t perform this action'))
            return HttpResponseRedirect(self.get_success_url(self.blog))


class UsersBlogView(GenericBlogView, TemplateResponseMixin):
    view_name = 'members_blog'

    template_name = "blog/blog_users.html"

    def get_context_data(self, **kwargs):
        context = super(UsersBlogView, self).get_context_data(**kwargs)
        context.update({
            'owners': (
                Membership.objects
                .select_related('user', 'user__profile')
                .filter(blog=self.blog, role='O')
                .with_rating()
                .distinct()
                .order_by('user')
            ),
            'admins': (
                Membership.objects
                .select_related('user', 'user__profile')
                .filter(blog=self.blog, role='A')
                .with_rating()
                .distinct()
                .order_by('user')
            ),
            'members': (
                Membership.objects
                .select_related('user', 'user__profile')
                .filter(blog=self.blog, role='M')
                .with_rating()
                .distinct()
                .order_by('-rating')
            )[:50],
        })

        if self.membership.role in ['O', 'A'] and self.membership.can_accept_new_users():
            context.update(dict(
                waiting=(
                    Membership.objects
                    .select_related('user', 'user__profile')
                    .filter(blog=self.blog, role='W')
                    .with_rating()
                    .distinct()
                    .order_by('-user__karma')
                )
            ))

        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))
