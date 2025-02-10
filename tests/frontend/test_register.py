"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import pytest
import string
from nicegui import ui
from nicegui.testing import User

from common.models.app import AppSettingsDB
from common.models.errors import ObjectNotFoundError
from common.stores.adapter import AdapterStore
from common.stores.app import AppSettingsStore
from tests.frontend.utils import assert_logged_in, login
from tests.utils.users import create_user_db


@pytest.mark.asyncio
async def test_all_fields_filled_in(user: User):
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB())
    AppSettingsStore().initialize(force=True)

    username='user'
    password='8765432Wsx#'

    await user.open('/register')
    await user.should_see('Register for 10,000 Words')
    user.find('Name (Optional)', kind=ui.input).type(username.title())
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type(password)
    user.find('Join', kind=ui.button).click()

    await user.should_see(content=None, kind=ui.html, marker='display-name-errors')
    await user.should_see(content=None, kind=ui.html, marker='username-errors')
    await user.should_see(content=None, kind=ui.html, marker='password-errors')
    await user.should_see(
        content=None,
        kind=ui.html,
        marker='confirm-password-errors',
    )

    user_adapter = AdapterStore().get('UserDBPort')
    userdb = user_adapter.get_by_username(username)
    assert userdb.display_name == username.title()
    assert userdb.username == username
    # First user is admin
    assert userdb.is_admin == True

    # Password wasn't returned.
    # We'll manually add it.
    userdb.password = password
    await login(user, userdb)
    await user.open('/edit')
    await assert_logged_in(user, userdb)


@pytest.mark.asyncio
async def test_second_user_is_not_automatically_admin(user: User):
    create_user_db(is_admin=True)
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB(multiuser_mode=True))
    AppSettingsStore().initialize(force=True)

    username='user'
    password='8765432Wsx#'

    await user.open('/register')
    await user.should_see('Register for 10,000 Words')
    user.find('Name (Optional)', kind=ui.input).type(username.title())
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type(password)
    user.find('Join', kind=ui.button).click()

    user_adapter = AdapterStore().get('UserDBPort')
    userdb = user_adapter.get_by_username(username)
    assert userdb.display_name == username.title()
    assert userdb.username == username
    # Additional users aren't automatically admins
    assert userdb.is_admin == False

    # Password wasn't returned.
    # We'll manually add it
    userdb.password = password
    await login(user, userdb)
    await user.open('/edit')
    await assert_logged_in(user, userdb)


@pytest.mark.asyncio
async def test_display_name_optional(user: User):
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB())
    AppSettingsStore().initialize(force=True)

    username='user'
    password='8765432Wsx#'

    await user.open('/register')
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type(password)
    user.find('Join', kind=ui.button).click()

    await user.should_see(content=None, kind=ui.html, marker='display-name-errors')
    await user.should_see(content=None, kind=ui.html, marker='username-errors')
    await user.should_see(content=None, kind=ui.html, marker='password-errors')
    await user.should_see(
        content=None,
        kind=ui.html,
        marker='confirm-password-errors',
    )

    user_adapter = AdapterStore().get('UserDBPort')
    userdb = user_adapter.get_by_username(username)
    assert userdb.display_name == ''
    assert userdb.username == username
    # First user is admin
    assert userdb.is_admin == True

    # Password wasn't returned.
    # We'll manually add it
    userdb.password = password
    await login(user, userdb)
    await user.open('/edit')
    await assert_logged_in(user, userdb)


@pytest.mark.asyncio
async def test_username_must_be_4_characters_long(user: User):
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB())
    AppSettingsStore().initialize(force=True)

    username='foo'
    password='8765432Wsx#'

    await user.open('/register')
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type(password)
    user.find('Join', kind=ui.button).click()

    await user.should_see(
        content='Username must be at least 4 characters long.',
        kind=ui.html,
        marker='username-errors',
    )
    user_adapter = AdapterStore().get('UserDBPort')
    assert user_adapter.get_first() is None

    username='fooo'
    await user.open('/register')
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type(password)
    user.find('Join', kind=ui.button).click()
    userdb = user_adapter.get_first()
    assert userdb.username == username

@pytest.mark.asyncio
async def test_username_cannot_contain_spaces(user: User):
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB())
    AppSettingsStore().initialize(force=True)

    username='f oo'
    password='8765432Wsx#'

    await user.open('/register')
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type(password)
    user.find('Join', kind=ui.button).click()

    await user.should_see(
        content='Username must not contain spaces.',
        kind=ui.html,
        marker='username-errors',
    )
    user_adapter = AdapterStore().get('UserDBPort')
    assert user_adapter.get_first() is None


@pytest.mark.asyncio
async def test_username_cannot_contain_punctuation(user: User):
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB())
    AppSettingsStore().initialize(force=True)

    username = string.punctuation + string.ascii_lowercase
    password='8765432Wsx#'

    await user.open('/register')
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type(password)
    user.find('Join', kind=ui.button).click()

    await user.should_see(
        content=(
            'Username must have only ASCII letters, numbers, and dashes or '
            'underscores.'
        ),
        kind=ui.html,
        marker='username-errors',
    )
    user_adapter = AdapterStore().get('UserDBPort')
    assert user_adapter.get_first() is None


@pytest.mark.asyncio
async def test_username_cannot_contain_upercase_letters(user: User):
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB())
    AppSettingsStore().initialize(force=True)

    username = string.ascii_uppercase
    password='8765432Wsx#'

    await user.open('/register')
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type(password)
    user.find('Join', kind=ui.button).click()

    await user.should_see(
        content='Username must be lowercase',
        kind=ui.html,
        marker='username-errors',
    )
    user_adapter = AdapterStore().get('UserDBPort')
    assert user_adapter.get_first() is None


@pytest.mark.asyncio
async def test_username_is_valid(user: User):
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB())
    AppSettingsStore().initialize(force=True)

    username = string.ascii_lowercase + '_' + '-' + string.digits
    password='8765432Wsx#'

    await user.open('/register')
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type(password)
    user.find('Join', kind=ui.button).click()

    await user.should_see(content=None, kind=ui.html, marker='username-errors')
    user_adapter = AdapterStore().get('UserDBPort')
    userdb = user_adapter.get_first()
    assert userdb.username == username

    # The adapter doesn't return passwords,
    # so we'll add it.
    userdb.password = password
    await login(user, userdb)
    await user.open('/edit')
    await assert_logged_in(user, userdb)


@pytest.mark.asyncio
async def test_password_must_be_8_characters_long(user: User):
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB())
    AppSettingsStore().initialize(force=True)

    username='user'
    password='1234567'

    await user.open('/register')
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type(password)
    user.find('Join', kind=ui.button).click()

    await user.should_see(
        content='Password must be at least 8 characters long.',
        kind=ui.html,
        marker='password-errors',
    )
    user_adapter = AdapterStore().get('UserDBPort')
    assert user_adapter.get_first() is None

    # We're testing with the in-memory database adapter,
    # which has minimal validation.
    # This password won't fly with Django.
    password ='12345678'
    await user.open('/register')
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type(password)
    user.find('Join', kind=ui.button).click()
    userdb = user_adapter.get_first()
    assert userdb.username == username


@pytest.mark.asyncio
async def test_password_cannot_contain_spaces(user: User):
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB())
    AppSettingsStore().initialize(force=True)

    username='user'
    password='876543 2Wsx#'

    await user.open('/register')
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type(password)
    user.find('Join', kind=ui.button).click()

    await user.should_see(
        content='Password must not contain spaces.',
        kind=ui.html,
        marker='password-errors',
    )
    user_adapter = AdapterStore().get('UserDBPort')
    assert user_adapter.get_first() is None


@pytest.mark.asyncio
async def test_password_confirm_matches(user: User):
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB())
    AppSettingsStore().initialize(force=True)

    username='user'
    password='8765432Wsx#'

    await user.open('/register')
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type('mismatch')
    user.find('Join', kind=ui.button).click()

    await user.should_see(
        content="Confirm password doesn't match.",
        kind=ui.html,
        marker='confirm-password-errors',
    )
    user_adapter = AdapterStore().get('UserDBPort')
    assert user_adapter.get_first() is None


@pytest.mark.asyncio
async def test_dont_show_password_fields_if_passwordless_system(user: User):
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB(passwordless_login=True))
    AppSettingsStore().initialize(force=True)

    username='user'

    await user.open('/register')
    await user.should_not_see('Password', kind=ui.input)
    await user.should_not_see('Confirm password', kind=ui.input)
    user.find('Username', kind=ui.input).type(username)
    user.find('Join', kind=ui.button).click()

    await user.should_not_see(
        content='Password must be at least 8 characters long.',
        kind=ui.html,
        marker='password-errors',
    )
    await user.should_not_see(
        content="Confirm password doesn't match.",
        kind=ui.html,
        marker='confirm-password-errors',
    )
    user_adapter = AdapterStore().get('UserDBPort')
    userdb = user_adapter.get_first()
    assert userdb.username == username

    # No password should be needed
    await login(user, userdb)
    await user.open('/edit')
    await assert_logged_in(user, userdb)


@pytest.mark.asyncio
async def test_redirects_if_no_app_settings(user: User):
    await user.open('/register')
    await user.should_not_see('Register for 10,000 Words', kind=ui.label)
    await user.should_not_see('Login', kind=ui.label)
    await user.should_see('Settings', kind=ui.label)


@pytest.mark.asyncio
async def test_redirects_if_not_multiuser_system_and_user_exists(user: User):
    create_user_db()
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB())
    AppSettingsStore().initialize(force=True)

    await user.open('/register')
    await user.should_not_see('Register for 10,000 Words', kind=ui.label)
    await user.should_see('Login', kind=ui.label)


@pytest.mark.asyncio
async def test_redirects_if_already_logged_in_as_another_user(user: User):
    userdb = create_user_db()
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB(multiuser_mode=True))
    AppSettingsStore().initialize(force=True)

    await login(user, userdb)
    await user.open('/register')
    await assert_logged_in(user, userdb)
    await user.should_not_see('Register for 10,000 Words', kind=ui.label)
    await user.should_not_see('Login', kind=ui.label)


@pytest.mark.asyncio
async def test_cancel(user: User):
    create_user_db()
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB(multiuser_mode=True))
    AppSettingsStore().initialize(force=True)

    username = 'user'
    password = '8765432Wsx#'

    await user.open('/register')
    user.find('Username', kind=ui.input).type(username)
    user.find('Password', kind=ui.input).type(password)
    user.find('Confirm password', kind=ui.input).type(password)
    user.find('Cancel', kind=ui.button).click()

    user_adapter = AdapterStore().get('UserDBPort')
    try:
        userdb = user_adapter.get_by_username(username)
    except ObjectNotFoundError:
        assert True
    else:
        assert False, 'Userdb exists!'


@pytest.mark.asyncio
async def test_cancel_unavailable_for_first_user(user: User):
    adapter = AdapterStore().get('AppSettingsDBPort')
    adapter.create_or_update(AppSettingsDB(multiuser_mode=True))
    AppSettingsStore().initialize(force=True)

    await user.open('/register')
    await user.should_not_see('Cancel', kind=ui.button())
