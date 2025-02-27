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
    Control state of the settings in the application
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

    def get_db(self) -> AppSettingsDB:
        return self.backend_adapter.get_or_default()

    def set(self):
        settings = self.frontend_adapter.get(self.backend_adapter.get())
        app.storage.client['settings'] = settings.model_dump()

    def update(self, settings_dict: Dict[str, bool]):
        settings = AppSettingsDB(
            multiuser_mode=settings_dict.get('multiuser_mode', False),
            passwordless_login=settings_dict.get('passwordless_login', False),
            show_users_on_login_screen=settings_dict.get(
                'show_users_on_login_screen',
                False,
            ),
        )
        new_settings = self.frontend_adapter.get(
            self.backend_adapter.create_or_update(settings),
        )
        app.storage.client['settings'] = new_settings.model_dump()
