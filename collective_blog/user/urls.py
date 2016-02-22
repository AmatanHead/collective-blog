import django.contrib.auth.views as v
from django.conf.urls import include, url

from user.forms import AuthenticationForm

urlpatterns = [
    url(r'a/login/$', v.login,
        {'authentication_form': AuthenticationForm}, name='login'),

    url(r'a/logout/$', v.logout, name='logout'),

    url(r'a/password_change/$', v.password_change,
        {'post_change_redirect': 'password_change_done'}, name='password_change'),
    url(r'a/password_change/done/$', v.password_change_done, name='password_change_done'),

    url(r'a/password_reset/$', v.password_reset,
        {'post_reset_redirect': 'password_reset_done'}, name='password_reset'),
    url(r'a/password_reset/done/$', v.password_reset_done, name='password_reset_done'),
    url(r'a/password_reset/confirm/(?P<uidb64>[a-zA-Z0-9]+)/(?P<token>.+)/$', v.password_reset_confirm,
        {'post_reset_redirect': 'password_reset_complete'}, name='password_reset_confirm'),
    url(r'a/password_reset/complete/$', v.password_reset_complete, name='password_reset_complete'),
    url(r'a/', include('registration.backends.default.urls')),

    url(r'$', v.login, name='self'),
]
