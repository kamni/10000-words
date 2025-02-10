"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from pathlib import Path
from unittest import TestCase

from common.adapters.in_memory.auth import AuthInMemoryAdapter
from common.models.app import AppSettingsDB
from common.models.users import UserUI, UserDB
from common.ports.auth import AuthInvalidError
from common.stores.adapter import AdapterStore
from common.stores.config import ConfigStore
from common.stores.in_memory import InMemoryDBStore
from common.utils.singleton import Singleton


TEST_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEST_CONFIG = TEST_CONFIG_DIR / 'setup.cfg'


class TestAuthInMemoryAdapter(TestCase):
    """
    Tests for common.adapters.in_memory.auth.AuthInMemoryAdapter
    """

    @classmethod
    def setUpClass(cls):
        # Clean up from other tests
        Singleton.destroy(ConfigStore)
        Singleton.destroy(AdapterStore)
        Singleton.destroy(InMemoryDBStore)

        super().setUpClass()

    def setUp(self):
        adapters = AdapterStore(config=TEST_CONFIG, subsection='dev.in_memory')
        self.app_settings = adapters.get('AppSettingsDBPort')
        self.auth_adapter = adapters.get('AuthPort')
        self.user_db_adapter = adapters.get('UserDBPort')
        self.user_ui_adapter = adapters.get('UserUIPort')

    def tearDown(self):
        Singleton.destroy(ConfigStore)
        Singleton.destroy(AdapterStore)
        Singleton.destroy(InMemoryDBStore)

    def test_login(self):
        self.app_settings.create_or_update(AppSettingsDB())
        user = UserDB(
            username='test_login',
            password='fakepass390',
            display_name='Test User',
        )
        userdb = self.user_db_adapter.create(user)

        expected = self.user_ui_adapter.get(userdb)
        returned = self.auth_adapter.login(user.username, user.password)
        self.assertEqual(expected, returned)

    def test_login_passwordless(self):
        self.app_settings.create_or_update(
            AppSettingsDB(passwordless_login=True),
        )
        user = UserDB(username='test_login_passwordless')
        userdb = self.user_db_adapter.create(user)

        expected = self.user_ui_adapter.get(userdb)
        returned = self.auth_adapter.login(user.username)
        self.assertEqual(expected, returned)

    def test_login_passwordless_user_does_not_exist(self):
        self.app_settings.create_or_update(
            AppSettingsDB(passwordless_login=True),
        )
        with self.assertRaises(AuthInvalidError):
            self.auth_adapter.login('user-does-not-exist')

    def test_login_no_password_but_not_passwordless(self):
        self.app_settings.create_or_update(
            AppSettingsDB(passwordless_login=False),
        )
        user = UserDB(username='test_login_passwordless')
        # Note that we're not setting a password
        userdb = self.user_db_adapter.create(user)

        with self.assertRaises(AuthInvalidError):
            self.auth_adapter.login(userdb.username)

    def test_login_user_does_not_exist(self):
        with self.assertRaises(AuthInvalidError):
            self.auth_adapter.login('foo', 'bar')

    def test_logout(self):
        user = UserDB(
            username='test_logout',
            password='fakepass390',
            display_name='Test User',
        )
        userdb = self.user_db_adapter.create(user)
        userui = self.user_ui_adapter.get(userdb)

        self.assertIsNone(self.auth_adapter.logout(userui))

    def test_logout_user_does_not_exist(self):
        userui = UserUI(
            id=uuid.uuid4(),
            username='test_logout_doesnt_exist',
            display_name='Test User',
        )
        self.assertIsNone(self.auth_adapter.logout(userui))
