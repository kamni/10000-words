"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from abc import ABC, abstractmethod
from typing import Union

from ..models.app import AppSettingsDB


class AppSettingsDBPort(ABC):
    """
    Get global settings for apps
    """

    @abstractmethod
    def get(self) -> Union[AppSettingsDB, None]:
        """
        Get the settings.
        Only returns the first instance, because there should be only one.

        :return: AppSettingsDB object, or None
        """
        pass

    @abstractmethod
    def get_or_default(self) -> AppSettingsDB:
        """
        Get the settings.
        If they don't exist, return default settings (all false)

        :return: AppSettingsDB
        """
        pass

    @abstractmethod
    def create_or_update(self, settings: AppSettingsDB) -> AppSettingsDB:
        """
        Create a new settings item, or update if one exists.
        NOTE: There can be only one.

        :return: AppSettingsDB object.
        """
        pass
