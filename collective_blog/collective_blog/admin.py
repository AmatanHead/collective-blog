from django.contrib import admin

from collective_blog.models import Blog, Post
from s_markdown.admin import MarkdownAdmin


@admin.register(Blog)
class ProfileAdmin(MarkdownAdmin, admin.ModelAdmin):
    pass


@admin.register(Post)
class ProfileAdmin(MarkdownAdmin, admin.ModelAdmin):
    pass
