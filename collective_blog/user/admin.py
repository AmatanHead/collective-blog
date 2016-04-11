from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile

UserAdmin.inlines += (ProfileInline, )
