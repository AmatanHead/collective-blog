"""Profile views

Note that for auth process, default views are used. See `urls.py`.

"""

from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import (HttpResponseRedirect,
                         HttpResponse)
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_protect
from django.utils.translation import ugettext as _

# from messages_extends import constants as constants_messages
# from messages_extends.models import Message

from .models import Karma
from .forms import ProfileForm, UserForm

User = get_user_model()


def view_profile(request, username=None):
    if username is None:
        user = request.user
    else:
        # TODO check iexact here
        user = get_object_or_404(User.objects.select_related('profile'),
                                 username=username)

    is_self_profile = username is None or user.pk == request.user.pk

    karma = Karma.objects.filter(object=user).score()

    if karma['score'] >= 10:
        color = 'green'
    elif karma['score'] <= -10:
        color = 'orange'
    else:
        color = 'gray'

    if request.user.is_anonymous():
        self_vote = None
    else:
        self_vote = Karma.objects.filter(object=user, user=request.user).first()

    return render(request, 'profile/profile.html', {
        'user_display': user,

        # Access
        'is_self_profile': is_self_profile,
        'editable': user.profile.can_be_edited_by(request.user),
        'is_moderator': user.profile.can_be_moderated_by(request.user),

        # Private data
        'visible_email': user.profile.email_as_seen_by(request.user),

        # Karma buttons
        'karma': karma,
        'karma_vote': self_vote,
        'karma_color': color,
        'karma_color_threshold': [-10, 10],
    })


@login_required
def self_profile(request):
    return view_profile(request)


def edit_profile(request, username=None):
    # TODO check iexact here
    user = get_object_or_404(User.objects.select_related('profile'),
                             username=username)

    if user.profile.can_be_edited_by(request.user):
        if request.POST:
            form = ProfileForm(request.POST, instance=user.profile)
            user_form = UserForm(request.POST, instance=user)
            if form.is_valid() and user_form.is_valid():
                form.save()
                user_form.save()

                messages.success(
                    request,
                    _("%(username)s's profile was saved")
                    % dict(username=user.username))

                # Message.objects.create(
                #     user=request.user,
                #     level=constants_messages.SUCCESS_PERSISTENT,
                #     message=_("%(username)s's profile was saved") % dict(username=user.username))

                return HttpResponseRedirect(
                    reverse('view_profile',
                            kwargs=dict(username=user.username))
                )
        else:
            form = ProfileForm(instance=user.profile)
            user_form = UserForm(instance=user)

        return render(request, 'profile/edit_profile.html', {
            'user_display': user,
            'form': form,
            'form_user': user_form,
            'is_self_profile': username is None or user.pk == request.user.pk,
            'is_moderator': user.profile.can_be_moderated_by(request.user),
        })

    else:
        return render(request, 'profile/edit_profile_fail.html', {
            'user_display': user
        }, status=403)


@csrf_protect
def vote(request, username=None):
    # TODO check iexact here
    user = get_object_or_404(User.objects.select_related('profile'),
                             username=username)

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

    if user.pk == request.user.pk:
        return HttpResponse(_("You can't vote for yourself"))

    if user.profile.can_be_voted_by(request.user):
        Karma.vote_for(request.user, user, v)
        return HttpResponse(str(Karma.objects.filter(object=user).score()['score']))
    else:
        return HttpResponse(_("You can't vote for this user"))


@csrf_protect
def switch_active(request, username=None):
    # TODO check iexact here
    user = get_object_or_404(User.objects.select_related('profile'),
                             username=username)

    if user.profile.can_be_moderated_by(request.user):
        user.is_active = not user.is_active
        user.save()

        if user.is_active:
            messages.success(
                request,
                _("%(username)s's account activated")
                % dict(username=user.username))
        else:
            messages.success(
                request,
                _("%(username)s's account deactivated")
                % dict(username=user.username))

        return HttpResponseRedirect(
            reverse('view_profile', kwargs=dict(username=user.username)))
    else:
        return render(request, 'profile/edit_profile_fail.html', {
            'user_display': user
        }, status=403)
