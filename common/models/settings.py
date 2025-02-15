"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Optional

from pydantic import BaseModel

from .base import HashableMixin


class AppSettingsDB(HashableMixin, BaseModel):
    """
    Tracks global settings for the application
    """

    # Whether app is used by more than one user.
    # Provides form to add new user, if True.
    multiuser_mode: Optional[bool] = False

    # Whether app requires a password to log on.
    # If running locally on a computer with trusted users,
    # then set this to True.
    # Set False if running as a web server
    # or local privacy is desired.
    passwordless_login: Optional[bool] = False

    # Show or hide the available users.
    # If running in single-user mode with passwordless login,
    # set this to True.
    # If running on the web or with untrusted users,
    # set this to False.
    show_users_on_login_screen: Optional[bool] = False

    @property
    def unique_fields(self):
        return [
            'multiuser_mode',
            'passwordless_login',
            'show_users_on_login_screen',
        ]


class AppSettingsUI(HashableMixin, BaseModel):
    """
    The way the app settings are displayed in the frontend.
    """
    # True when multiuser mode is off and passwordless login is enabled.
    automatic_login: Optional[bool] = False

    # True when an AppSettingsDB object exists in the database
    is_configured: Optional[bool] = False

    # False when multiuser mode is off and passwordless login is enabled.
    show_login: Optional[bool] = False

    # Matches the show_login setting
    show_logout: Optional[bool] = False

    # True when there are no users in the system,
    # and when multiuser mode is enabled.
    show_registration: Optional[bool] = False

    # False when passwordless login is enabled
    show_password_field: Optional[bool] = False

    # True when showing users on the login screen is enabled.
    show_user_select: Optional[bool] = False

    @property
    def unique_fields(self):
        return [
            'automatic_login',
            'is_configured',
            'show_login',
            'show_logout',
            'show_registration',
            'show_password_field',
            'show_user_select',
        ]

