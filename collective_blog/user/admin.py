from django.contrib import admin
from .models import Profile

from s_markdown.admin import MarkdownAdmin


@admin.register(Profile)
class ProfileAdmin(MarkdownAdmin):
    pass
