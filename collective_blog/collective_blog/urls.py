"""Root routing"""

from django.conf.urls import url, include
from django.contrib import admin

from collective_blog.views import *
from django.views.i18n import javascript_catalog

js_info_dict = {
    'packages': ('collective_blog',),
}

urlpatterns = [
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript-catalog'),

    url(r'^u/', include('user.urls')),

    url(r'^b/v/(?P<blog_slug>[a-zA-Z0-9_-]+)/$',
        BlogView.as_view(), name='view_blog'),
    url(r'^b/v/(?P<blog_slug>[a-zA-Z0-9_-]+)/(?P<page>[0-9]+)/$',
        BlogView.as_view(), name='view_blog'),
    url(r'^b/j/(?P<blog_slug>[a-zA-Z0-9_-]+)/$',
        JoinBlogView.as_view(), name='join_blog'),
    url(r'^b/l/(?P<blog_slug>[a-zA-Z0-9_-]+)/$',
        LeaveBlogView.as_view(), name='leave_blog'),
    url(r'^b/u/(?P<blog_slug>[a-zA-Z0-9_-]+)/$',
        UpdateColorBlogView.as_view(), name='update_color_blog'),
    url(r'^b/e/(?P<blog_slug>[a-zA-Z0-9_-]+)/$',
        EditBlogView.as_view(), name='edit_blog'),
    url(r'^b/c/$',
        CreateBlogView.as_view(), name='create_blog'),
    url(r'^b/d/(?P<blog_slug>[a-zA-Z0-9_-]+)/$',
        DeleteBlogView.as_view(), name='delete_blog'),
    url(r'^b/m/(?P<blog_slug>[a-zA-Z0-9_-]+)/$',
        UsersBlogView.as_view(), name='members_blog'),
    url(r'^b/api/(?P<blog_slug>[a-zA-Z0-9_-]+)/$',
        MembershipApi.as_view(), name='blog_api'),

    url(r'^p/v/(?P<post_slug>[a-zA-Z0-9_-]+)/$',
        PostView.as_view(), name='view_post'),
    url(r'^p/a/vote_post/(?P<post_slug>[a-zA-Z0-9_-]+)/$',
        VotePostView.as_view(), name='vote_post'),
    url(r'^p/c/$',
        CreatePostView.as_view(), name='create_post'),
    url(r'^p/d/(?P<post_slug>[a-zA-Z0-9_-]+)/$',
        DeletePostView.as_view(), name='delete_post'),

    url(r'^admin/', admin.site.urls),
    url(r'^messages/', include('messages_extends.urls')),

    url(r'^(?P<page>[0-9]+)/$', FeedView.as_view(), name='homepage'),
    url(r'^$', FeedView.as_view(), name='homepage'),

    url(r'^feed-best/(?P<page>[0-9]+)/$', BestFeedView.as_view(), name='feed_best'),
    url(r'^feed-best/$', BestFeedView.as_view(), name='feed_best'),

    url(r'^feed-month-best/(?P<page>[0-9]+)/$', MonthBestFeedView.as_view(), name='feed_month_best'),
    url(r'^feed-month-best/$', MonthBestFeedView.as_view(), name='feed_month_best'),

    url(r'^feed-day-best/(?P<page>[0-9]+)/$', DayBestFeedView.as_view(), name='feed_day_best'),
    url(r'^feed-day-best/$', DayBestFeedView.as_view(), name='feed_day_best'),

    url(r'^feed/(?P<page>[0-9]+)/$', PersonalFeedView.as_view(), name='feed_personal'),
    url(r'^feed/$', PersonalFeedView.as_view(), name='feed_personal'),

    url(r'^my-posts/(?P<page>[0-9]+)/$', MyPostsFeedView.as_view(), name='my_posts'),
    url(r'^my-posts/$', MyPostsFeedView.as_view(), name='my_posts'),

    url(r'^my-blogs/$', ListBlogView.as_view(), name='my_blogs'),
]
