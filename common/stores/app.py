"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Any, Optional, Union

from ..ports.auth import AuthInvalidError
from ..models.errors import ObjectNotFoundError
from ..models.users import UserUI
from ..ports.auth import AuthInvalidError
from ..stores.adapter import AdapterStore
from ..utils.singleton import Singleton


class AppSettingsStore(metaclass=Singleton):
    """
    Tracks auth settings and current authenticated user
    """

    AUTOMATIC_LOGIN = 'automatic_login'
    IS_CONFIGURED = 'is_configured'
    SHOW_LOGIN = 'show_login'
    SHOW_LOGOUT = 'show_logout'
    SHOW_REGISTRATION = 'show_registration'
    SHOW_PASSWORD_FIELD = 'show_password_field'
    SHOW_USER_SELECT = 'show_user_select'

    def __init__(self):
        self._settings = {}
        self.initialize()

    @property
    def automatic_login(self):
        return self.get(self.AUTOMATIC_LOGIN)

    @property
    def is_configured(self):
        return self.get(self.IS_CONFIGURED)

    @property
    def show_login(self):
        return self.get(self.SHOW_LOGIN)

    @property
    def show_logout(self):
        return self.get(self.SHOW_LOGOUT)

    @property
    def show_registration(self):
        return self.get(self.SHOW_REGISTRATION)

    @property
    def show_password_field(self):
        return self.get(self.SHOW_PASSWORD_FIELD)

    @property
    def show_user_select(self):
        return self.get(self.SHOW_USER_SELECT)

    def initialize(self, force: Optional[bool]=False):
        """
        Initialize this store.
        This is a singleton,
        so if you want to re-initialize the settings,
        you should use `force=True`.

        :force: Even if this has been initialized, re-initialize it
        """

        if self._settings and not force:
            return

        adapter_store = AdapterStore()
        self._settings_adapter = adapter_store.get('AppSettingsDBPort')
        self._user_db_adapter = adapter_store.get('UserDBPort')

        self._settings = {
            self.AUTOMATIC_LOGIN: False,
            self.IS_CONFIGURED: False,
            self.SHOW_LOGIN: False,
            self.SHOW_LOGOUT: False,
            self.SHOW_REGISTRATION: False,
            self.SHOW_PASSWORD_FIELD: False,
            self.SHOW_USER_SELECT: False,
        }

        settings = self._settings_adapter.get()
        if settings:
            self._settings.update({
                self.IS_CONFIGURED: True,
                self.SHOW_LOGIN: True,
                self.SHOW_LOGOUT: True,
                self.SHOW_REGISTRATION: settings.multiuser_mode,
                self.SHOW_PASSWORD_FIELD: not settings.passwordless_login,
                self.SHOW_USER_SELECT: settings.show_users_on_login_screen,
            })

            userdb = self._user_db_adapter.get_first()
            if (
                userdb
                and settings.passwordless_login
                and not settings.multiuser_mode
            ):
                # We don't need to show this
                # because we're just logging in automatically
                # with the first user in the database
                self._settings[self.SHOW_USER_SELECT] = False
                self._settings[self.SHOW_LOGIN] = False
                self._settings[self.SHOW_LOGOUT] = False
                self._settings[self.AUTOMATIC_LOGIN] = True

            # We need to be able to add a user after initial configuration.
            # Enable registration form, even if not explicitly enabled
            if not settings.multiuser_mode and not userdb:
                self._settings[self.SHOW_LOGIN] = True
                self._settings[self.SHOW_REGISTRATION] = True
                self._settings[self.SHOW_LOGOUT] = not settings.passwordless_login


    def get(self, setting: str) -> Union[Any, None]:
        """
        Get specified setting.

        Available settings:

        * automatic_login
        * is_configured
        * show_login
        * show_logout
        * show_registration
        * show_password_field
        * show_user_select

        :setting: One of the available settings

        :return: Specified setting, if exists; otherwise None
        """

        setting = self._settings[setting]
        return setting
