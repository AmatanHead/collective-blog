from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile
from s_markdown.admin import MarkdownAdmin


class ProfileInline(MarkdownAdmin, admin.StackedInline):
    model = Profile
    max_num = 1
    can_delete = False


class _UserAdmin(UserAdmin):
    def add_view(self, *args, **kwargs):
        self.inlines = []
        return super(UserAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines = [ProfileInline]
        return super(UserAdmin, self).change_view(*args, **kwargs)


admin.site.unregister(User)
admin.site.register(User, _UserAdmin)
