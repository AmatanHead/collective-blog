"""Auth system routing"""

from django.conf.urls import url

from .views import post

urlpatterns = [
    url(r'^p/(?P<post_id>[0-9]+)/$', post, name='view_post')
]
