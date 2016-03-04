from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import Profile
from .forms import ProfileForm, UserForm

User = get_user_model()


def view_profile(request, username=None):
    if username is None:
        user = request.user
    else:
        user = get_object_or_404(User.objects.select_related('profile'),
                                 username=username)

    is_self_profile = username is None or user.pk == request.user.pk

    return render(request, 'profile/view_profile.html', {
        'user': user,
        'self_profile': is_self_profile,
        'editable': Profile.can_edit_profile(request.user, user.profile),
        'show_email': Profile.can_see_email(request.user, user.profile),
        'visible_email': Profile.visible_email(request.user, user.profile),
    })


@login_required
def self_profile(request):
    return view_profile(request)


def edit_profile(request, username=None):
    user = get_object_or_404(User.objects.select_related('profile'),
                             username=username)

    if Profile.can_edit_profile(request.user, user.profile):

        if request.POST:
            form = ProfileForm(request.POST, instance=user.profile)
            user_form = UserForm(request.POST, instance=user)
            if form.is_valid() and user_form.is_valid():
                form.save()
                user_form.save()
                return HttpResponseRedirect(
                    reverse('view_profile',
                            kwargs=dict(username=user.username))
                )
        else:
            form = ProfileForm(instance=user.profile)
            user_form = UserForm(instance=user)

        return render(request, 'profile/edit_profile.html', {
            'user': user,
            'form': form,
            'user_form': user_form,
            'self_profile': username is None or user.pk == request.user.pk,
        })

    else:
        return render(request, 'profile/edit_profile_fail.html', {
            'user': user
        }, status=403)
