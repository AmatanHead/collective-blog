"""Root routing"""

from django.conf.urls import url, include
from django.contrib import admin

from collective_blog.views import (FeedView, VotePostView, PostView, BlogView,
                                   JoinBlogView, LeaveBlogView, UpdateColorBlogView)

urlpatterns = [
    url(r'^u/', include('user.urls')),

    url(r'^b/(?P<blog_slug>[a-zA-Z0-9_-]+)/$',
        BlogView.as_view(), name='view_blog'),
    url(r'^b/(?P<blog_slug>[a-zA-Z0-9_-]+)/(?P<page>[0-9]+)/$',
        BlogView.as_view(), name='view_blog'),
    url(r'^b/j/(?P<blog_slug>[a-zA-Z0-9_-]+)/$',
        JoinBlogView.as_view(), name='join_blog'),
    url(r'^b/l/(?P<blog_slug>[a-zA-Z0-9_-]+)/$',
        LeaveBlogView.as_view(), name='leave_blog'),
    url(r'^b/u/(?P<blog_slug>[a-zA-Z0-9_-]+)/$',
        UpdateColorBlogView.as_view(), name='update_color_blog'),

    url(r'^b/p/(?P<post_slug>[a-zA-Z0-9_-]+)/$',
        PostView.as_view(), name='view_post'),
    url(r'^b/a/vote_post/(?P<post_slug>[a-zA-Z0-9_-]+)/$',
        VotePostView.as_view(), name='vote_post'),

    url(r'^admin/', admin.site.urls),
    url(r'^messages/', include('messages_extends.urls')),

    url(r'^(?P<page>[0-9]+)/$', FeedView.as_view(), name='homepage'),
    url(r'^$', FeedView.as_view(), name='homepage')
]
