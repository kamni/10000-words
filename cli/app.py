"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
import sys

from textual.app import App
from textual.reactive import reactive

from common.stores.auth import AuthStore

from .views.app_settings import AppSettingsScreen
from .views.edit import EditScreen
from .views.learn import LearnScreen
from .views.login import LoginScreen
from .views.permissions import PermissionDeniedModal
from .views.registration import RegistrationModal
from .views.upload import UploadModal


class TenThousandWordsApp(App):
    """
    CLI app for the 10,000 Words project
    """

    BINDINGS = [
        ('e', 'edit', 'Edit'),
        ('l', 'learn', 'Learn'),
        ('q', 'logout', 'Log Out'),
    ]

    MODES = {
        'edit': EditScreen,
        'learn': LearnScreen,
        'login': LoginScreen,
        'settings': AppSettingsScreen,
    }

    SCREENS = {
        'upload': UploadModal,
        'register': RegistrationModal,
        'permission_denied': PermissionDeniedModal,
    }

    current_user = reactive(None)

    @property
    def auth(self):
        if not hasattr(self, '_auth') or self._auth is None:
            self._auth = AuthStore()
        return self._auth

    def on_mount(self):
        self.theme = 'flexoki'

        if not self.auth.is_configured:
            self.action_settings()
        elif self.auth.logged_in_user:
            self.action_edit()
        else:
            self.action_login()

    def action_edit(self):
        if not self.auth.logged_in_user:
            return self.action_login()
        self.switch_mode('edit')

    def action_learn(self):
        if not self.auth.logged_in_user:
            return self.action_login()
        self.switch_mode('learn')

    def action_login(self):
        if not self.auth.is_configured:
            self.action_settings()
        self.switch_mode('login', self.update_current_user)

    def action_logout(self):
        self.auth.logout()
        self.update_current_user()
        self.switch_mode('login')

    def action_settings(self):
        if not self.auth.is_configured:
            return self.switch_mode('settings')

        user = self.auth.logged_in_user
        if not user:
            self.action_login()
        elif not user.is_admin:
            self.push_screen('permission_denied')
        else:
            self.switch_mode('settings')

    def update_current_user(self):
        self.current_user = self.auth.logged_in_user

    def watch_current_user(self):
        settings_bindings = ('s', 'settings', 'Settings')
        if self.current_user and self.current_user.is_admin:
            if settings_bindings not in self.BINDINGS:
                self.BINDINGS.append(settings_bindings)
        else:
            if settings_bindings in self.BINDINGS:
                self.BINDINGS.pop(self.BINDING.index(settings_bindings))
