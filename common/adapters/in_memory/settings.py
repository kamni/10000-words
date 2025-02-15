"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Union

from ...models.settings import AppSettingsDB
from ...ports.settings import AppSettingsDBPort
from ...stores.data.in_memory import InMemoryDBStore


class AppSettingsInMemoryAdapter(AppSettingsDBPort):
    """
    Uses the in-memory database store
    """

    def __init__(self, **kwargs):
        # Ignore any kwargs configuration.
        # This uses the django settings.
        super().__init__()
        self.store = InMemoryDBStore()

    def get(self) -> Union[AppSettingsDB, None]:
        """
        Get the settings.
        Only returns the first instance, because there should be only one.

        :return: AppSettingsDB object, or None
        """
        return self.store.db.app_settings

    def get_or_default(self) -> AppSettingsDB:
        """
        Get the settings.
        If they don't exist, return default settings (all false)

        :return: AppSettingsDB
        """
        app_db = self.store.db.app_settings
        if not app_db:
            app_db = AppSettingsDB()
        return app_db

    def create_or_update(self, settings: AppSettingsDB) -> AppSettingsDB:
        """
        Create a new settings item, or update if one exists.
        NOTE: There can be only one.

        :return: AppSettingsDB object.
        """
        self.store.db.app_settings = settings
        return settings
