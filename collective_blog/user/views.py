"""Profile views

Note that for auth process, default views are used. See `urls.py`.

"""

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import DetailView, RedirectView, View
from django.views.generic.base import TemplateResponseMixin
from django.utils.translation import ugettext as _

from .models import Karma
from .forms import ProfileForm, UserForm

User = get_user_model()


class ProfileView(DetailView):
    slug_field = 'username'
    slug_url_kwarg = 'username'

    template_name = 'user/profile.html'

    # TODO check iexact here
    queryset = User.objects.select_related('profile')

    def get_context_data(self, **kwargs):
        context = {}  # No need to call super. There's nothing interesting

        user = kwargs['object']
        karma = self.get_karma(user)

        context['user_display'] = user
        context['karma'] = karma
        context['karma_color'] = self.get_color(karma)
        context['karma_vote'] = self.get_self_vote(user)
        context['karma_color_threshold'] = self.get_color_threshold()
        context['visible_email'] = user.profile.email_as_seen_by(self.request.user)
        context['is_moderator'] = user.profile.can_be_moderated_by(self.request.user)
        context['is_self_profile'] = user.pk == self.request.user.pk
        context['editable'] = user.profile.can_be_edited_by(self.request.user)

        return context

    def get_karma(self, user):
        return Karma.objects.filter(object=user).score()['score']

    def get_color_threshold(self):
        """Returns a range in which a color of the karma box becomes gray"""
        return getattr(self, 'color_threshold', [-10, 10])

    def get_color(self, karma):
        """Returns the current color tag of the karma box"""
        color_threshold = self.get_color_threshold()

        if karma >= color_threshold[1]:
            return 'green'
        elif karma <= color_threshold[0]:
            return 'orange'
        else:
            return 'gray'

    def get_self_vote(self, user):
        """Returns the vote object, if the user has already made his voice"""
        if self.request.user.is_anonymous():
            return None
        else:
            return Karma.objects.filter(
                object=user, user=self.request.user).first()


@method_decorator(login_required, name='dispatch')
class SelfProfileView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
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
        """Dave and redirect"""
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
        self.template_name = 'user/edit_profile_fail.html'
        return self.render_to_response({
            'user_display': self.user
        }, status=403)


@method_decorator(csrf_protect, 'dispatch')
class VoteProfileView(View):
    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(
            User.objects.select_related('profile'),
            username=kwargs.pop('username'))

        return super(VoteProfileView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        if not request.is_ajax():
            return HttpResponse('This page is ajax-only', status=418)

        # noinspection PyBroadException
        try:
            v = int(request.GET['vote'])
            assert v in [0, 1, -1]
        except Exception:
            return HttpResponse(_('Wrong vote'))

        if request.user.is_anonymous():
            return HttpResponse(_("You should be logged in"))

        if not request.user.is_active:
            return HttpResponse(_("Your account is disabled"))

        if self.user.pk == request.user.pk:
            return HttpResponse(_("You can't vote for yourself"))

        if self.user.profile.can_be_voted_by(request.user):
            Karma.vote_for(request.user, self.user, v)
            return HttpResponse(
                str(Karma.objects.filter(object=self.user).score()['score']))
        else:
            return HttpResponse(_("You can't vote for this user"))


@method_decorator(csrf_protect, 'dispatch')
class SwitchActiveProfileView(View, TemplateResponseMixin):
    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(
            User.objects.select_related('profile'),
            username=kwargs.pop('username'))

        return super(SwitchActiveProfileView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        if self.user.pk == request.user.pk:
            return self.denied_self()
        elif self.user.profile.can_be_moderated_by(request.user):
            return self.process()
        else:
            return self.denied()

    def process(self):
        """Process the request and switch user state"""
        self.user.is_active = not self.user.is_active
        self.user.save()

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

    def denied(self):
        """Render the `denied` message"""
        self.template_name = 'user/edit_profile_fail.html'
        return self.render_to_response({
            'user_display': self.user
        }, status=403)

    def denied_self(self):
        """Render the `denied` message"""
        self.template_name = 'user/edit_profile_fail_self_action.html'
        return self.render_to_response({
            'user_display': self.user
        }, status=403)
