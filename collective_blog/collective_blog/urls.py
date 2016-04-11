"""Root routing"""

from django.conf.urls import url, include
from django.contrib import admin

from collective_blog.views import feed, post, vote as vote_post

urlpatterns = [
    url(r'^u/', include('user.urls')),

    url(r'^b/p/(?P<post_slug>[a-zA-Z0-9_-]+)/$', post, name='view_post'),
    url(r'^b/a/vote_post/(?P<post_slug>[a-zA-Z0-9_-]+)/$', vote_post,
        name='vote_post'),

    url(r'^admin/', admin.site.urls),
    url(r'^messages/', include('messages_extends.urls')),

    url(r'^(?P<page>[0-9]+)/$', feed, name='homepage'),
    url(r'^$', feed, name='homepage')
]
