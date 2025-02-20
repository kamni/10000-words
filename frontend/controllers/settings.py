"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Dict

from nicegui import app

from common.models.settings import AppSettingsDB, AppSettingsUI
from frontend.controllers.base import BaseController


class SettingsController(BaseController):
    """
    Manages logic for the settings between the backend and frontend.
    """

    @property
    def backend_adapter(self):
        if not self._backend_adapter:
            self._backend_adapter = self.adapters.get('AppSettingsDBPort')
        return self._backend_adapter

    @property
    def frontend_adapter(self):
        if not self._frontend_adapter:
            self._frontend_adapter = self.adapters.get('AppSettingsUIPort')
        return self._frontend_adapter

    def get(self) -> AppSettingsUI:
        settings_dict = app.storage.client.get('settings', {})
        settings = AppSettingsUI(**settings_dict)
        return settings

    def set(self):
        settings = self.frontend_adapter.get(self.backend_adapter.get())
        app.storage.client['settings'] = settings.model_dump()

    def update(self, **kwargs):
        settings = AppSettingsDB(
            multiuser_mode=kwargs.get('multiuserMode', False),
            passwordless_login=kwargs.get('passwordlessLogin', False),
            show_users_on_login_screen=kwargs.get('showUsersOnLoginScreen', False),
        )
        new_settings = self.frontend_adapter.get(
            self.backend_adapter.create_or_update(settings),
        )
        app.storage.client['settings'] = new_settings.model_dump()
