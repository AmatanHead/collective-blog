"""Root routing"""

from django.conf.urls import url, include
from django.contrib import admin

from blog.views import feed

urlpatterns = [
    url(r'^u/', include('user.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^messages/', include('messages_extends.urls')),

    url(r'^$', feed, name='homepage')
]
