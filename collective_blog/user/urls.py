"""Auth system routing"""

import django.contrib.auth.views as v
from django.conf.urls import include, url

from .views import ProfileView, SelfProfileView, EditProfileView, VoteProfileView, SwitchActiveProfileView
from .forms import AuthenticationForm, PasswordResetForm, PasswordChangeForm, SetPasswordForm

urlpatterns = [
    url(r'^a/login/$', v.login,
        {'authentication_form': AuthenticationForm}, name='login'),

    url(r'^a/logout/$', v.logout, name='logout'),

    url(r'^a/password_change/$', v.password_change,
        {'post_change_redirect': 'password_change_done',
         'password_change_form': PasswordChangeForm}, name='password_change'),
    url(r'^a/password_change/done/$', v.password_change_done, name='password_change_done'),

    url(r'^a/password_reset/$', v.password_reset,
        {'post_reset_redirect': 'password_reset_done',
         'password_reset_form': PasswordResetForm}, name='password_reset'),
    url(r'^a/password_reset/done/$', v.password_reset_done, name='password_reset_done'),
    url(r'^a/password_reset/confirm/(?P<uidb64>[a-zA-Z0-9]+)/(?P<token>.+)/$', v.password_reset_confirm,
        {'post_reset_redirect': 'password_reset_complete',
         'set_password_form': SetPasswordForm}, name='password_reset_confirm'),
    url(r'^a/password_reset/complete/$', v.password_reset_complete, name='password_reset_complete'),
    url(r'^a/', include('registration.backends.default.urls')),

    url(r'^a/e/(?P<username>[a-zA-Z0-9@.+-_]+)/$', EditProfileView.as_view(), name='edit_profile'),
    url(r'^a/ac/(?P<username>[a-zA-Z0-9@.+-_]+)/$', SwitchActiveProfileView.as_view(), name='switch_active'),
    url(r'^a/vt/(?P<username>[a-zA-Z0-9@.+-_]+)/$', VoteProfileView.as_view(), name='vote_user'),

    url(r'^(?P<username>[a-zA-Z0-9@.+-_]+)/$', ProfileView.as_view(), name='view_profile'),

    url(r'^$', SelfProfileView.as_view(), name='view_self_profile'),
]
