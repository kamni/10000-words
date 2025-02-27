"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import pytest
from nicegui import ui
from nicegui.testing import User

from common.models.settings import AppSettingsDB
from common.stores.adapter import AdapterStore
from frontend import main
from tests.frontend.utils import login
from tests.utils.users import create_user_db


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_configure_first_time_all_false(user: User):
    """
    This is testing the first time the app runs,
    using the default configuration.
    """
    await user.open('/configure')
    await user.should_not_see('Cancel', kind=ui.button)
    user.find('Save', kind=ui.button).click()

    adapter = AdapterStore().get('AppSettingsDBPort')
    settings = adapter.get()
    assert settings is not None
    assert settings.multiuser_mode == False
    assert settings.passwordless_login == False
    assert settings.show_users_on_login_screen == False


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_configure_first_time_all_true(user: User):
    """
    This is testing the first time the app runs,
    setting all settings to True to ensure the switches save correctly.
    """
    await user.open('/configure')
    await user.should_not_see('Cancel', kind=ui.button)
    user.find(kind=ui.switch, marker='multiuser').click()
    user.find(kind=ui.switch, marker='passwordless').click()
    user.find(kind=ui.switch, marker='show-user').click()
    user.find('Save', kind=ui.button).click()

    adapter = AdapterStore().get('AppSettingsDBPort')
    settings = adapter.get()
    assert settings is not None
    assert settings.multiuser_mode == True
    assert settings.passwordless_login == True
    assert settings.show_users_on_login_screen == True


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_configure_second_time(user: User):
    userdb = create_user_db(is_admin=True)
    adapter = AdapterStore().get('AppSettingsDBPort')
    settings = adapter.create_or_update(
        AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        ),
    )

    await login(user, userdb)
    await user.open('/configure')
    await user.should_see('Cancel', kind=ui.button)
    user.find(kind=ui.switch, marker='multiuser').click()
    user.find(kind=ui.switch, marker='passwordless').click()
    user.find(kind=ui.switch, marker='show-user').click()
    user.find('Save', kind=ui.button).click()

    settings = adapter.get()
    assert settings is not None
    assert settings.multiuser_mode == False
    assert settings.passwordless_login == False
    assert settings.show_users_on_login_screen == False


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_configure_second_time_cancel(user: User):
    userdb = create_user_db(is_admin=True)
    adapter = AdapterStore().get('AppSettingsDBPort')
    settings = adapter.create_or_update(
        AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        ),
    )

    await login(user, userdb)
    await user.open('/configure')
    user.find(kind=ui.switch, marker='multiuser').click()
    user.find(kind=ui.switch, marker='passwordless').click()
    user.find(kind=ui.switch, marker='show-user').click()
    user.find('Cancel', kind=ui.button).click()

    # Settings should not have changed
    settings = adapter.get()
    assert settings is not None
    assert settings.multiuser_mode == True
    assert settings.passwordless_login == True
    assert settings.show_users_on_login_screen == True


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_redirects_to_register_if_settings_exist_but_no_user(user: User):
    adapter = AdapterStore().get('AppSettingsDBPort')
    settings = adapter.create_or_update(
        AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        ),
    )

    await user.open('/configure')
    await user.should_not_see('Settings', kind=ui.label)
    await user.should_see('Register for 10,000 Words', kind=ui.label)


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_redirects_if_user_not_logged_in_and_not_first_run(user: User):
    create_user_db(is_admin=True)
    adapter = AdapterStore().get('AppSettingsDBPort')
    settings = adapter.create_or_update(
        AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        ),
    )

    await user.open('/configure')
    await user.should_not_see('Settings', kind=ui.label)
    await user.should_see('Login', kind=ui.label)


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_redirects_when_not_admin_user(user: User):
    userdb = create_user_db()
    adapter = AdapterStore().get('AppSettingsDBPort')
    settings = adapter.create_or_update(
        AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        ),
    )

    await login(user, userdb)
    await user.open('/configure')
    await user.should_not_see('Settings', kind=ui.label)
