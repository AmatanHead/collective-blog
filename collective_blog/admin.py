from django.contrib import admin

from mptt.admin import MPTTModelAdmin
from taggit.models import Tag as TaggitTag

from collective_blog.models import Blog, Post, Membership, Comment, Tag
from s_markdown.admin import MarkdownAdmin


admin.site.unregister(TaggitTag)


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


@admin.register(Tag)
class MembershipAdmin(admin.ModelAdmin):
    pass
