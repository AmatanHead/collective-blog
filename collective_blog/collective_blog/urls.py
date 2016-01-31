from django.conf.urls import url, include
from django.contrib import admin
import user.urls

urlpatterns = [
    url(r'^u/', include('user.urls')),
    url(r'^admin/', admin.site.urls),
]
