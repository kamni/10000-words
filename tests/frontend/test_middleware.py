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
from frontend.middleware.auth import UNRESTRICTED_PAGE_ROUTES
from tests.frontend.utils import assert_logged_in, login
from tests.utils.users import create_user_db


RESTRICTED_ROUTES = {'/edit', '/practice'}


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_auth_middleware_allows_all_pages_when_logged_in(user: User):
    userdb = create_user_db(is_admin=True)
    settings_adapter = AdapterStore().get('AppSettingsDBPort')
    settings_adapter.create_or_update(AppSettingsDB(multiuser_mode=True))

    await login(user, userdb)

    for route in RESTRICTED_ROUTES:
        await user.open(route)
        await user.should_not_see('Login', kind=ui.label)

    await user.open('/configure')
    await user.should_not_see('Login', kind=ui.label)

    # A logged-in user can't visit Login or Registration
    # and will be redirected
    for route in {'/', '/register'}:
        await user.open(route)
        await user.should_not_see('Login', kind=ui.label)
        await user.should_not_see('Registration', kind=ui.label)


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_can_visit_unrestricted_pages_when_not_authenticated(user: User):
    # We have to test this before configuring the settings.
    # After initial configuration,
    # only admin users can visit the page.
    await user.open('/configure')
    await user.should_see('Settings', kind=ui.label)

    create_user_db(is_admin=True)
    settings_adapter = AdapterStore().get('AppSettingsDBPort')
    settings_adapter.create_or_update(AppSettingsDB(multiuser_mode=True))

    await user.open('/')
    await user.should_see('Login', kind=ui.label)

    await user.open('/register')
    await user.should_see('Register for 10,000 Words', kind=ui.label)


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_middleware_redirects_to_login_for_restricted_pages(user: User):
    create_user_db(is_admin=True)
    settings_adapter = AdapterStore().get('AppSettingsDBPort')
    settings_adapter.create_or_update(AppSettingsDB(multiuser_mode=True))

    for route in RESTRICTED_ROUTES:
        await user.open(route)
        await user.should_see('Login', kind=ui.label)
