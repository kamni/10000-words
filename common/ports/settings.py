"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from abc import ABC, abstractmethod
from typing import Optional, Union

from ..models.settings import AppSettingsDB, AppSettingsUI


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


class AppSettingsUIPort(ABC):
    """
    Handle conversion of AppSettingsDB objects to UI format
    """

    @abstractmethod
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
