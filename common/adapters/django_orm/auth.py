"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Optional

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from ...models.errors import ObjectNotFoundError
from ...models.users import UserUI
from ...ports.auth import AuthInvalidError, AuthPort
from ...stores.adapter import AdapterStore


class AuthDjangoORMAdapter(AuthPort):
    """
    Handles authentication of a user using the Django ORM.

    NOTE: This adapter presumes that it is running locally
          as a desktop application.
          This authenticates directly with the Django database,
          and does not rely on http requests.
          For this reason the logged-in status of the user
          is managed by the frontend app
          and not via Django requests.

          Please create an AuthDjangoAPIAdapter
          if you wish to authenticate via http requests
          and let Django manage the session.
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
        user = None
        if password:
            user = authenticate(
                request=None,
                username=username,
                password=password,
            )
        elif self.app_settings.get().passwordless_login:
            # The app is configured with passwordless login.
            # We only need to get the user with the right username.
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # We'll thow an error in a sec...
                pass

        if not user:
            # This message is only for internal logging.
            # Do not show the message to users,
            # as it reveals the internals of the system
            # and may encourage hacking.
            raise AuthInvalidError('Failed to authenticate with Django')

        try:
            userdb = self.user_db_adapter.get_by_username(username)
        except ObjectNotFoundError:
            # This message is only for internal logging.
            # Do not show to users.
            raise AuthInvalidError('Django user found, but UserSettings missing')

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
