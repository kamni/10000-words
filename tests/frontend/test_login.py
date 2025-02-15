"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Optional

import pytest
from nicegui import ui
from nicegui.testing import User

from common.stores.adapter import AdapterStore
from frontend import main
from tests.frontend.utils import (
    assert_logged_in,
    assert_not_logged_in,
    login,
)
from tests.utils.settings import create_app_settings
from tests.utils.users import create_user_db


@pytest.mark.asyncio
@pytest.mark.module_under_test(main)
async def test_initial_setup_flow(user: User):
    """
    Here are the steps we expect the first time things are launched:

    1. Redirect to configure view.
    2. After configuring, redirect to create a user (who is an admin).
    3. Login form now shows.
    4. Redirect to edit view on successful login.
    """
    await user.open('/')
    # Redirect to configure view
    await user.should_see('Settings', kind=ui.label)
    await assert_not_logged_in(user)

    # Configure the app
    user.find('Save', kind=ui.button).click()
    await user.should_see('Settings Saved!', kind=ui.notify)

    await user.open('/')
    # After configuring, redirect to create a user (who is an admin)
    await assert_not_logged_in(user)

    username = 'user'
    password = '8765432Wsx#'

    await user.should_see('Register for 10,000 Words', kind=ui.label)
    user.find('Name (Optional)').type(username.title())
    user.find('Username').type(username)
    user.find('Password').type(password)
    user.find('Confirm password').type(password)
    user.find('Join', kind=ui.button).click()
    await user.should_see('Success!', kind=ui.notify)

    userdb = AdapterStore().get('UserDBPort').get_by_username(username)

    # Login form now shows
    await user.open('/')
    await assert_not_logged_in(user)
    await user.should_see('Login', kind=ui.label)

    user.find('Username').type(username)
    user.find('Password').type(password)
    await user.should_not_see('Register for 10,000 Words', kind=ui.link)
    user.find('Log In', kind=ui.button).click()
    await user.should_see(f'Welcome!', kind=ui.notify)

    # Should redirect to '/edit' screen once logged in
    await user.open('/')
    await assert_logged_in(user, userdb)


@pytest.mark.asyncio
async def test_login_config_false_false_false(user: User):
    """
    multiuser_mode = False
    passwordless_login = False
    show_users_on_login_screen = False
    """
    userdb = create_user_db()
    create_app_settings()

    await user.open('/')
    await assert_not_logged_in(user)

    await user.should_see('Login', kind=ui.label)
    user.find('Username', kind=ui.input).type(userdb.username)
    user.find('Password', kind=ui.input).type(userdb.password)
    await user.should_not_see('Register for 10,000 Words', kind=ui.link)
    user.find('Log In', kind=ui.button).click()
    await user.should_see('Welcome!', kind=ui.notify)


@pytest.mark.asyncio
async def test_login_config_true_false_false(user: User):
    """
    multiuser_mode = True
    passwordless_login = False
    show_users_on_login_screen = False
    """
    userdb = create_user_db()
    # Testing a multiuser system
    userdb2 = create_user_db()
    create_app_settings(multiuser_mode=True)

    await user.open('/')
    await assert_not_logged_in(user)

    await user.should_see('Login', kind=ui.label)
    user.find('Username', kind=ui.input).type(userdb.username)
    user.find('Password', kind=ui.input).type(userdb.password)
    await user.should_see('Register for 10,000 Words', kind=ui.link)
    user.find('Log In', kind=ui.button).click()
    await user.should_see('Welcome!', kind=ui.notify)

    await user.open('/')
    await assert_logged_in(user, userdb)
    await user.should_not_see('Login')


@pytest.mark.asyncio
async def test_login_config_true_true_false(user: User):
    """
    multiuser_mode = True
    passwordless_login = True
    show_users_on_login_screen = False
    """
    userdb = create_user_db()
    # Testing a multiuser system
    userdb2 = create_user_db()

    create_app_settings(
        multiuser_mode=True,
        passwordless_login=True,
    )

    await user.open('/')
    await assert_not_logged_in(user)

    await user.should_see('Login')
    user.find('Username', kind=ui.input).type(userdb.username)
    await user.should_not_see('Password', kind=ui.input)
    await user.should_see('Register for 10,000 Words', kind=ui.link)
    user.find('Log In', kind=ui.button).click()
    await user.should_see('Welcome!', kind=ui.notify)

    await user.open('/')
    await assert_logged_in(user, userdb)
    await user.should_not_see('Login')


@pytest.mark.asyncio
async def test_login_config_true_false_true(user: User):
    """
    multiuser_mode = True
    passwordless_login = False
    show_users_on_login_screen = True
    """
    userdb = create_user_db()
    # Multiuser system
    userdb2 = create_user_db()

    create_app_settings(
        multiuser_mode=True,
        passwordless_login=False,
        show_users_on_login_screen=True,
    )

    await user.open('/')
    await assert_not_logged_in(user)

    await user.should_see('Login', kind=ui.label)
    user.find('Username', kind=ui.select).click()
    await user.should_see(userdb2.username)
    user.find(userdb.username).click()
    user.find('Password', kind=ui.input).type(userdb.password)
    await user.should_see('Register for 10,000 Words', kind=ui.link)
    user.find('Log In', kind=ui.button).click()
    await user.should_see('Welcome!', kind=ui.notify)

    await user.open('/')
    await assert_logged_in(user, userdb)
    await user.should_not_see('Login')


@pytest.mark.asyncio
async def test_login_config_true_true_true(user: User):
    """
    multiuser_mode = True
    passwordless_login = True
    show_users_on_login_screen = True
    """
    userdb = create_user_db()
    # Multiuser system
    userdb2 = create_user_db()

    create_app_settings(
        multiuser_mode=True,
        passwordless_login=True,
        show_users_on_login_screen=True,
    )

    await user.open('/')
    await assert_not_logged_in(user)

    await user.should_see('Login', kind=ui.label)
    user.find('Username', kind=ui.select).click()
    await user.should_see(userdb2.username)
    user.find(userdb.username).click()
    await user.should_not_see('Password', kind=ui.input)
    user.find('Log In', kind=ui.button).click()
    await user.should_see('Welcome!', kind=ui.notify)

    await user.open('/')
    await assert_logged_in(user, userdb)
    await user.should_not_see('Login')


@pytest.mark.asyncio
async def test_login_config_false_true_false(user: User):
    """
    multiuser_mode = False
    passwordless_login = True
    show_users_on_login_screen = False
    """
    # Single user system
    userdb = create_user_db()
    # This sets up automatic login
    create_app_settings(passwordless_login=True)

    await user.open('/')
    await assert_logged_in(user, userdb)
    await user.should_not_see('Login')


@pytest.mark.asyncio
async def test_login_config_false_true_true(user: User):
    """
    multiuser_mode = False
    passwordless_login = True
    show_users_on_login_screen = True
    """
    # Single user system
    userdb = create_user_db()

    create_app_settings(
        multiuser_mode=False,
        passwordless_login=True,
        show_users_on_login_screen=True,
    )

    await user.open('/')
    await assert_logged_in(user, userdb)
    await user.should_not_see('Login')


@pytest.mark.asyncio
async def test_login_config_false_false_true(user: User):
    """
    multiuser_mode = False
    passwordless_login = False
    show_users_on_login_screen = True
    """
    # Single user system
    userdb = create_user_db()

    create_app_settings(
        multiuser_mode=False,
        passwordless_login=False,
        show_users_on_login_screen=True,
    )

    await user.open('/')
    await assert_not_logged_in(user)

    await user.should_see('Login', kind=ui.label)
    await user.should_see('Username', kind=ui.input, content=userdb.username)
    user.find('Password', kind=ui.input).type(userdb.password)
    user.find('Log In', kind=ui.button).click()
    await user.should_see('Welcome!', kind=ui.notify)

    await user.open('/')
    await assert_logged_in(user, userdb)
    await user.should_not_see('Login')


@pytest.mark.asyncio
async def test_login_redirects_to_signup_when_no_other_users(user: User):
    create_app_settings(
        multiuser_mode=False,
        passwordless_login=False,
        show_users_on_login_screen=False,
    )

    await user.open('/')
    await assert_not_logged_in(user)
    await user.should_see('Register for 10,000 Words', kind=ui.label)
    await user.should_not_see('No account?')


@pytest.mark.asyncio
async def test_login_redirects_already_logged_in(user: User):
    userdb = create_user_db()
    create_app_settings()

    await login(user, userdb)
    await user.open('/')
    await assert_logged_in(user, userdb)


@pytest.mark.asyncio
async def test_validate_username_bad_user(user: User):
    create_user_db()
    create_app_settings()

    await user.open('/')
    user.find('Username', kind=ui.input).type('not-a-user')
    user.find('Password', kind=ui.input).type('not-the-password')
    user.find('Log In', kind=ui.button).click()
    await user.should_see('Invalid username or password.', kind=ui.label)

@pytest.mark.asyncio
async def test_validate_username_bad_user_passwordless(user: User):
    create_user_db()
    create_app_settings(multiuser_mode=True, passwordless_login=True)

    await user.open('/')
    user.find('Username', kind=ui.input).type('not-a-user')
    await user.should_not_see('Password', kind=ui.input)
    user.find('Log In', kind=ui.button).click()
    await user.should_see('Invalid username.', kind=ui.label)

@pytest.mark.asyncio
async def test_validate_username_bad_password(user: User):
    userdb = create_user_db()
    create_app_settings()

    await user.open('/')
    user.find('Username', kind=ui.input).type(userdb.username)
    user.find('Password', kind=ui.input).type('not-the-password')
    user.find('Log In', kind=ui.button).click()
    await user.should_see('Invalid username or password.', kind=ui.label)


@pytest.mark.asyncio
async def test_registration_link(user: User):
    create_user_db()
    create_app_settings(multiuser_mode=True)

    await user.open('/')
    user.find('Register for 10,000 Words', kind=ui.link).click()

    # Smoke test for registration page
    await user.should_see('Register for 10,000 Words', kind=ui.label)
    await user.should_see('Join', kind=ui.button)


@pytest.mark.asyncio
async def test_logout(user: User):
    userdb = create_user_db(is_admin=True)
    create_app_settings(multiuser_mode=True)

    await login(user, userdb)

    await user.open('/configure')
    await user.should_see('Settings', kind=ui.label)
    user.find(kind=ui.button, marker='header-user-menu').click()
    await user.should_see(kind=ui.right_drawer)
    user.find('Logout', kind=ui.button).click()

    await user.should_see('Login', kind=ui.label)
