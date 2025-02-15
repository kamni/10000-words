"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Optional

from common.models.settings import AppSettingsDB
from common.stores.adapter import AdapterStore


def make_app_settings(
    multiuser_mode: Optional[bool]=False,
    passwordless_login: Optional[bool]=False,
    show_users_on_login_screen: Optional[bool]=False,
) -> AppSettingsDB:
    """
    Make an AppSettingsDB object without saving it to the database.
    """

    settings = AppSettingsDB(
        multiuser_mode=multiuser_mode,
        passwordless_login=passwordless_login,
        show_users_on_login_screen=show_users_on_login_screen,
    )
    return settings


def create_app_settings(**kwargs) -> AppSettingsDB:
    """
    Make an AppSettingsDB object and save it to the database.

    :kwargs: Arguments to pass to the AppSettingsDB init
    """

    adapter = AdapterStore().get('AppSettingsDBPort')
    settings = AppSettingsDB(**kwargs)
    new_settings = adapter.create_or_update(settings)
    return new_settings
