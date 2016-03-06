"""Auth system routing"""

from django.conf.urls import url

from .views import post, vote as vote_post

urlpatterns = [
    url(r'^p/(?P<post_slug>[a-zA-Z0-9_-]+)/$', post, name='view_post'),
    url(r'^a/vote_post/(?P<post_slug>[a-zA-Z0-9_-]+)/$', vote_post,
        name='vote_post')
]
