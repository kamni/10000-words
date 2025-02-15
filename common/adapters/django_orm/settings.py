"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Union

from app.models import AppSettings

from ...models.settings import AppSettingsDB
from ...ports.settings import AppSettingsDBPort


class AppSettingsDjangoORMAdapter(AppSettingsDBPort):
    """
    Uses the Django ORM to manage settings
    """

    def __init__(self, **kwargs):
        # Ignore any kwargs configuration.
        # This uses the django settings.
        super().__init__()

    def _django_to_pydantic(self, app_settings: AppSettings):
        app_settings_db = AppSettingsDB(
            multiuser_mode=app_settings.multiuser_mode,
            passwordless_login=app_settings.passwordless_login,
            show_users_on_login_screen=app_settings.show_users_on_login_screen,
        )
        return app_settings_db

    def get(self) -> Union[AppSettingsDB, None]:
        """
        Get the settings.
        Only returns the first instance, because there should be only one.

        :return: AppSettingsDB object, or None
        """
        app = AppSettings.objects.first()
        if not app:
            return None

        app_db = self._django_to_pydantic(app)
        return app_db

    def get_or_default(self) -> AppSettingsDB:
        """
        Get the settings.
        If they don't exist, return default settings (all false)

        :return: AppSettingsDB
        """
        app = AppSettings.objects.first()
        if app:
            app_db = self._django_to_pydantic(app)
        else:
            app_db = AppSettingsDB()

        return app_db

    def create_or_update(self, settings: AppSettingsDB) -> AppSettingsDB:
        """
        Create a new settings item, or update if one exists.
        NOTE: There can be only one.

        :return: AppSettingsDB object.
        """
        existing_settings = AppSettings.objects.first()
        if existing_settings:
            existing_settings.multiuser_mode = settings.multiuser_mode
            existing_settings.passwordless_login = settings.passwordless_login
            existing_settings.show_users_on_login_screen = \
                    settings.show_users_on_login_screen
            existing_settings.save()
            app_db = self._django_to_pydantic(existing_settings)
        else:
            app = AppSettings.objects.create(
                multiuser_mode=settings.multiuser_mode,
                passwordless_login=settings.passwordless_login,
                show_users_on_login_screen=settings.show_users_on_login_screen,
            )
            app_db = self._django_to_pydantic(app)

        return app_db
