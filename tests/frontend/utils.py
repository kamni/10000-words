"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Optional

from nicegui import ui
from nicegui.testing import User

from common.models.users import UserDB
from common.stores.adapter import AdapterStore


async def login(user: User, userdb: UserDB):
    """
    Logs the given user in.

    :user: Nicegui testing user
    :userdb: User profile data from the database
    :app_settings: Settings for the app

    :raises: AssertionError if user is in an unexpected state
    """

    adapters = AdapterStore()
    settings_db = adapters.get('AppSettingsDBPort')
    settings_ui = adapters.get('AppSettingsUIPort')
    settings = settings_ui.get(settings_db.get())

    await user.open('/')
    try:
        await assert_not_logged_in(user)
    except AssertionError as exc1:
        # This is probably fine.
        # Single users in a passwordless system get auto-login
        try:
            await assert_logged_in(user, userdb)
            return
        except AssertionError:
            # Okay, maybe it's not fine...
            raise exc1

    user.find('Username', kind=ui.input).clear().type(userdb.username)
    if settings.show_password_field:
        user.find('Password', kind=ui.input).type(userdb.password)
    user.find('Log In', kind=ui.button).click()
    if settings.show_password_field:
        await user.should_not_see('Invalid username or password.', kind=ui.label)
    else:
        await user.should_not_see('Invalid username.', kind=ui.label)


async def assert_not_logged_in(user: User):
    """
    Verify the user can't see what should be visible after login.

    :user: Nicegui testing user

    :raises: AssertionError if user is in an unexpected state
    """
    await user.should_not_see('Edit', kind=ui.link)
    await user.should_not_see('Practice', kind=ui.link)
    await user.should_not_see(marker='user-menu')
    await user.should_not_see(kind=ui.right_drawer)


async def assert_logged_in(user: User, userdb: UserDB):
    """
    Verify what the user should see after login

    :user: Nicegui testing user
    :userdb: User profile data from the database

    :raises: AssertionError if user is in an unexpected state
    """
    adapters = AdapterStore()
    settings_db = adapters.get('AppSettingsDBPort')
    settings_ui = adapters.get('AppSettingsUIPort')
    settings = settings_ui.get(settings_db.get())

    await user.should_see('Edit', kind=ui.link)
    await user.should_see('Practice', kind=ui.link)
    await user.should_see(userdb.display_name, kind=ui.label)

    if userdb.is_admin or settings.show_logout:
        user.find(marker='header-user-menu').click()
        if userdb.is_admin:
            await user.should_see('App Settings', kind=ui.label)
        if settings.show_logout:
            await user.should_see('Logout', kind=ui.label)
    else:
        await user.should_not_see(kind=ui.right_drawer)
        user.find(userdb.display_name, kind=ui.label, marker='header-username')


