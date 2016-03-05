from django.contrib import admin
from .models import Blog, Post


from dj_markdown.admin import MarkdownAdmin


@admin.register(Blog)
class ProfileAdmin(MarkdownAdmin):
    pass


@admin.register(Post)
class ProfileAdmin(MarkdownAdmin):
    pass
