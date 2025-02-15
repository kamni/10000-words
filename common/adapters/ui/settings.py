"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Optional

from common.adapters.in_memory.users import UserDBInMemoryAdapter
from common.models.settings import AppSettingsDB, AppSettingsUI
from common.ports.settings import AppSettingsUIPort
from common.stores.adapter import AdapterStore


class AppSettingsUIAdapter(AppSettingsUIPort):
    """
    Handle conversion of AppSettingsDB objects to UI format
    """

    def get(self, settings: Optional[AppSettingsDB] = None) -> AppSettingsUI:
        """
        Convert an AppSettingsDB object into an AppSettingsUI object

        :settings: The settings to convert to the frontend format.
             NOTE: This is optional, because it's intended to work
                   directly with AppSettingsDBPort.get.
                   If the output is None, this method will return
                   an unconfigured AppSettingsUI.

        :return: AppSettingsUI
        """
        settings_ui = AppSettingsUI()
        if not settings:
            return settings_ui

        user_db_adapter = UserDBInMemoryAdapter()

        settings_ui.is_configured = True
        settings_ui.show_login = True
        settings_ui.show_registration = settings.multiuser_mode
        settings_ui.show_password_field = not settings.passwordless_login
        settings_ui.show_user_select = settings.show_users_on_login_screen

        userdb = user_db_adapter.get_first()
        if (
            userdb
            and settings.passwordless_login
            and not settings.multiuser_mode
        ):
            # We don't need to show this
            # because we're just logging in automatically
            # with the first user in the database
            settings_ui.show_user_select = False
            settings_ui.show_login = False
            settings_ui.automatic_login = True

        # If you can log in, you should also be able to log out
        settings_ui.show_logout = settings_ui.show_login

        # We need to be able to add a user after initial configuration.
        # Enable registration form, even if not explicitly enabled
        if not settings.multiuser_mode and not userdb:
            settings_ui.show_login = True
            settings_ui.show_registration = True
            # This is the exception to logout = login.
            # Once the user is registered, they won't need to log out,
            # because this is passwordless login.
            settings_ui.show_logout = not settings.passwordless_login

        return settings_ui
