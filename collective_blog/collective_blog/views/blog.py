from operator import itemgetter

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect, HttpResponse, \
    HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View, UpdateView, DeleteView, CreateView, \
    ListView
from django.views.generic.base import TemplateResponseMixin

from collective_blog.models import Blog, Membership, Post
from collective_blog.utils.errors import PermissionCheckFailed

from .feed import GenericFeedView
from ..forms import BlogForm, BlogFormCreate


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

    template_name = 'collective_blog/blog_detail.html'

    def get_context_data(self, **kwargs):
        context = super(BlogView, self).get_context_data(**kwargs)
        context['is_banned'] = self.blog.is_banned(self.membership)
        context['can_join'] = self.blog.check_can_join(self.request.user)
        context['colors'] = Membership.COLORS
        context['current_color'] = self.membership.color if self.membership else ''
        context['members'] = Membership.objects.filter(blog=self.blog).exclude(role__in=['L', 'LB']).count()
        context['posts'] = Post.objects.filter(blog=self.blog, is_draft=False).count()
        context['is_moderator'] = Blog.can_be_moderated_by(self.request.user)

        if self.membership and self.membership.role in ['O', 'A'] and self.membership.can_accept_new_users():
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

    template_name = "collective_blog/blog_leave_confirm.html"

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


class UsersBlogView(GenericBlogView, TemplateResponseMixin):
    view_name = 'members_blog'

    template_name = "collective_blog/blog_list_users.html"

    def get_context_data(self, **kwargs):
        context = super(UsersBlogView, self).get_context_data(**kwargs)
        context.update({
            'owners': (
                Membership.objects
                .prefetch_related('user', 'user__profile', 'blog')
                .distinct()
                .filter(blog=self.blog, role='O')
                .with_rating()
                .order_by('user')
            ),
            'admins': (
                Membership.objects
                .prefetch_related('user', 'user__profile', 'blog')
                .distinct()
                .filter(blog=self.blog, role='A')
                .with_rating()
                .order_by('user')
            ),
            'members': (
                Membership.objects
                .prefetch_related('user', 'user__profile', 'blog')
                .distinct()
                .filter(blog=self.blog, role__in=['M', 'B'])
                .with_rating()
                .order_by('-rating')
            ),
        })

        if self.membership and self.membership.role in ['O', 'A'] and self.membership.can_accept_new_users():
            context.update(dict(
                waiting=(
                    Membership.objects
                    .prefetch_related('user', 'user__profile', 'blog')
                    .distinct()
                    .filter(blog=self.blog, role='W')
                    .with_rating()
                    .order_by('-user__karma')
                )
            ))

        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))


class EditBlogView(GenericBlogView, UpdateView):
    view_name = 'edit_blog'

    form_class = BlogForm
    template_name = 'collective_blog/blog_edit.html'
    model = Blog
    slug_url_kwarg = 'blog_slug'

    def get_context_data(self, **kwargs):
        context = super(EditBlogView, self).get_context_data(**kwargs)
        context['is_moderator'] = Blog.can_be_moderated_by(self.request.user)
        return context

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

    def form_valid(self, form):
        messages.success(self.request,
                         _('"%(blog)s" blog was saved') % dict(blog=self.blog.name))
        return super(EditBlogView, self).form_valid(form)


class CreateBlogView(CreateView):
    form_class = BlogFormCreate
    template_name = 'collective_blog/blog_create.html'
    model = Blog

    def get_success_url(self, obj=None):
        return reverse('view_blog',
                       kwargs=dict(blog_slug=self.blog.slug))

    def form_valid(self, form):
        self.blog = form.save()
        self.blog.join(self.request.user, role='O')
        messages.success(self.request,
                         _('"%(blog)s" blog was created') % dict(blog=self.blog.name))
        return HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        if self.request.user.profile.karma >= 0:
            return super(CreateBlogView, self).get(request, *args, **kwargs)
        else:
            messages.error(self.request, _('Your karma should be positive to create a blog'))
            return HttpResponseRedirect(reverse('homepage'))

    def post(self, request, *args, **kwargs):
        if self.request.user.profile.karma >= 0:
            return super(CreateBlogView, self).post(request, *args, **kwargs)
        else:
            messages.error(self.request, _('Your karma should be positive to create a blog'))
            return HttpResponseRedirect(reverse('homepage'))


class DeleteBlogView(GenericBlogView, DeleteView):
    template_name = 'collective_blog/blog_delete_confirm.html'
    model = Blog
    slug_url_kwarg = 'blog_slug'

    def get_success_url(self, obj=None):
        return reverse('homepage')

    def get(self, request, *args, **kwargs):
        if self.membership.role == 'O' and not self.membership.is_banned():
            return super(DeleteBlogView, self).get(request, *args, **kwargs)
        else:
            messages.error(self.request, _('You can\'t perform this action'))
            return HttpResponseRedirect(self.get_success_url(self.blog))

    def post(self, request, *args, **kwargs):
        if self.membership.role == 'O' and not self.membership.is_banned():
            return super(DeleteBlogView, self).post(request, *args, **kwargs)
        else:
            messages.error(self.request, _('You can\'t perform this action'))
            return HttpResponseRedirect(self.get_success_url(self.blog))


class ListBlogView(ListView):
    paginate_by = None

    template_name = 'collective_blog/blog_list.html'
    context_object_name = 'membership_list'

    def get_queryset(self):
        """Returns a queryset of posts that are visible to a user"""
        return sorted(
            Membership.objects
            .exclude(role__in=['L'])
            .filter(user=self.request.user)
            .select_related('blog')
            .distinct()
            .with_rating()
            .distinct(),
            key=lambda x: (Membership.ROLE_ORDERING[x.role], x.rating)
        )
