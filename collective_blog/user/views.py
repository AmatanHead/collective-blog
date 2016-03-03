from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from user.models import Profile

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
    })


@login_required
def self_profile(request):
    return view_profile(request)


def edit_profile(request, username=None):
    pass
