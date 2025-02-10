"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Optional

from ...models.errors import ObjectNotFoundError
from ...models.users import UserUI
from ...ports.auth import AuthInvalidError, AuthPort
from ...stores.adapter import AdapterStore


class AuthInMemoryAdapter(AuthPort):
    """
    Handles authentication of a user using the Django ORM.

    NOTE: Not secure! For test purposes only.
        Do not use in production!
    """
    def __init__(self, **kwargs):
        # Ignore any kwargs configuration.
        # This uses the django settings.
        super().__init__()
        self._app_settings = None
        self._user_db_adapter = None
        self._user_ui_adapter = None

    @property
    def app_settings(self):
        # We can't instantiate these during __init__
        # because it interferes with AdapterStore.initialize.
        # Lazy load this adapters.
        if not self._app_settings:
            self._app_settings = AdapterStore().get('AppSettingsDBPort')
        return self._app_settings

    @property
    def user_db_adapter(self):
        # We can't instantiate these during __init__
        # because it interferes with AdapterStore.initialize.
        # Lazy load this adapters.
        if not self._user_db_adapter:
            self._user_db_adapter = AdapterStore().get('UserDBPort')
        return self._user_db_adapter

    @property
    def user_ui_adapter(self):
        # We can't instantiate these during __init__
        # because it interferes with AdapterStore.initialize.
        # Lazy load this adapters.
        if not self._user_ui_adapter:
            self._user_ui_adapter = AdapterStore().get('UserUIPort')
        return self._user_ui_adapter

    def login(self, username: str, password: Optional[str]=None) -> UserUI:
        """
        Log a user in.

        :username: Username of the user.
        :password: Password of the user.

        :return: UserUI:
        :raises: AuthInvalidError if user is not sucessfully authenticated.
        """
        try:
            userdb = self.user_db_adapter.get_by_username(username)
        except ObjectNotFoundError:
            raise AuthInvalidError('Invalid user')

        # The userdb object isn't returned with a password,
        # so we need to get this manually
        userdb_password = self.user_db_adapter.get_password(userdb.id)

        if not self.app_settings.get_or_default().passwordless_login:
            if password is None or userdb_password != password:
                raise AuthInvalidError('Invalid password')

        userui = self.user_ui_adapter.get(userdb)
        return userui

    def logout(self, user: UserUI):
        """
        Log a user out.
        Should not error if user is no longer logged in
        or was never logged in.

        :user: UserUI object that was logged in
        """
        # Nothing to do.
        # The frontend is handling the session
        return None
