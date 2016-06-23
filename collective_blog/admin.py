from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from collective_blog.models import Blog, Post, Membership, Comment
from s_markdown.admin import MarkdownAdmin


@admin.register(Blog)
class BlogAdmin(MarkdownAdmin, admin.ModelAdmin):
    pass


@admin.register(Post)
class PostAdmin(MarkdownAdmin, admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(MarkdownAdmin, MPTTModelAdmin):
    pass


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    pass
