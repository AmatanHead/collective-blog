"""Profile views

Note that for auth process, default views are used. See `urls.py`.

"""

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import DetailView, RedirectView, View
from django.views.generic.base import TemplateResponseMixin
from django.utils.translation import ugettext_lazy as _

from collective_blog.utils.errors import PermissionCheckFailed
from collective_blog.models import Membership, Post, Blog
from s_voting.views import VoteView
from .models import Karma
from .forms import ProfileForm, UserForm

User = get_user_model()


class ProfileView(DetailView):
    slug_field = 'username'
    slug_url_kwarg = 'username'

    template_name = 'user/profile.html'

    # TODO check iexact here
    queryset = User.objects.select_related('profile').distinct()

    def get_context_data(self, **kwargs):
        context = {}  # No need to call super. There's nothing interesting

        user = kwargs['object']

        context['user_display'] = user
        context['karma'] = {
            'model': Karma,
            'user': self.request.user,
            'obj': user,
            'disabled': self.request.user.is_anonymous(),
            # 'color_threshold': [0, 0],
            # 'use_colors': False,
        }
        context['visible_email'] = user.profile.email_as_seen_by(self.request.user)
        context['is_moderator'] = user.profile.can_be_moderated_by(self.request.user)
        context['is_self_profile'] = user.pk == self.request.user.pk
        context['editable'] = user.profile.can_be_edited_by(self.request.user)

        membership = (
            Membership.objects
            .exclude(role__in=['W', 'B', 'L', 'LB'])
            .filter(user=user)
            .select_related('blog')
            .distinct()
            .with_rating()
            .order_by('-rating')
        )
        context['blogs'] = membership

        posts = (
            Post.objects
            .filter(
                Q(blog__type='O') | (
                    Q(blog__members=self.request.user) &
                    Q(blog__membership__role__in=['O', 'M', 'A'])
                ) if not self.request.user.is_anonymous() else (
                    Q(blog__type='O')
                ),
                is_draft=False,
                author=user)
            .distinct()
            .order_by('-rating')
        )
        context['posts'] = posts

        return context


@method_decorator(login_required, name='dispatch')
class SelfProfileView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        list(Blog.objects.annotate(n=Count('members'), m=Count('members')))
        return reverse('view_profile',
                       kwargs=dict(username=self.request.user.username))


class EditProfileView(View, TemplateResponseMixin):
    # Have to use two forms in the same <form> tag:
    # on for `Profile` model and the other one for `User` motel.
    # Thus, this class can't be derived from the `FormView` class
    # because the `FormView` works with one form only.

    template_name = 'user/edit_profile.html'

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(
            User.objects.select_related('profile'),
            username=kwargs.pop('username'))

        return super(EditProfileView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        if not self.user.profile.can_be_edited_by(self.request.user):
            return self.denied()

        form = ProfileForm(instance=self.user.profile)
        user_form = UserForm(instance=self.user)

        return self.render_forms(request, form, user_form)

    def post(self, request):
        if not self.user.profile.can_be_edited_by(self.request.user):
            return self.denied()

        form = ProfileForm(request.POST, instance=self.user.profile)
        user_form = UserForm(request.POST, instance=self.user)

        if form.is_valid() and user_form.is_valid():
            return self.success(request, form, user_form)
        else:
            return self.render_forms(request, form, user_form)

    def render_forms(self, request, form, user_form):
        """Render the main editing template"""
        return self.render_to_response({
            'user_display': self.user,
            'form': form,
            'form_user': user_form,
            'is_self_profile': self.user.pk == request.user.pk,
            'is_moderator': self.user.profile.can_be_moderated_by(request.user),
        })

    def success(self, request, form, user_form):
        """Save and redirect"""
        form.save()
        user_form.save()

        message = _("%(username)s's profile was saved") % dict(username=self.user.username)
        messages.success(request, message)

        return HttpResponseRedirect(
            reverse('view_profile',
                    kwargs=dict(username=self.user.username))
        )

    def denied(self):
        """Render the `denied` message"""
        messages.error(self.request, _('You can\'t perform this action'))
        return HttpResponseRedirect(
            reverse('view_profile',
                    kwargs=dict(username=self.user.username))
        )


@method_decorator(csrf_protect, 'dispatch')
class VoteProfileView(VoteView):
    model = Karma

    def get_score(self):
        self.object.profile.refresh_from_db()
        return self.object.profile.karma

    def get_object(self, *args, **kwargs):
        return get_object_or_404(
            User.objects.select_related('profile'),
            username=kwargs.pop('username'))


@method_decorator(csrf_protect, 'dispatch')
class SwitchIsActiveView(View, TemplateResponseMixin):
    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(
            User.objects.select_related('profile'),
            username=kwargs.pop('username'))

        return super(SwitchIsActiveView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        try:
            self.user.profile.switch_is_active(request.user)
        except PermissionCheckFailed as e:
            messages.error(self.request, e.note)
            return HttpResponseRedirect(
                reverse('view_profile',
                        kwargs=dict(username=self.user.username))
            )

        if self.user.is_active:
            messages.success(
                self.request,
                _("%(username)s's account activated")
                % dict(username=self.user.username))
        else:
            messages.success(
                self.request,
                _("%(username)s's account deactivated")
                % dict(username=self.user.username))

        return HttpResponseRedirect(
            reverse('view_profile', kwargs=dict(username=self.user.username)))
