"""Auth system routing"""

from django.conf.urls import url

from .views import post, vote as vote_post

urlpatterns = [
    url(r'^p/(?P<post_id>[0-9]+)/$', post, name='view_post'),
    url(r'^a/vote_post/(?P<post_id>[0-9]+)/$', vote_post, name='vote_post')
]
