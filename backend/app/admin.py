"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from django.contrib import admin

from .models.settings import AppSettings


@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'multiuser_mode',
        'passwordless_login',
        'show_users_on_login_screen',
    ]
