"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid

from django.contrib.auth.models import User
from django.test import TestCase

from common.adapters.django_orm.auth import AuthDjangoORMAdapter
from common.models.app import AppSettingsDB
from common.models.users import UserUI, UserDB
from common.ports.auth import AuthInvalidError
from common.stores.adapter import AdapterStore


class TestAuthDjangoORMAdapter(TestCase):
    """
    Tests for common.adapters.auth.AuthDjangoORMAdapter
    """

    @classmethod
    def setUpClass(cls):
        adapters = AdapterStore(subsection='dev.django')
        cls.app_settings = adapters.get('AppSettingsDBPort')
        cls.auth_adapter = adapters.get('AuthPort')
        cls.user_db_adapter = adapters.get('UserDBPort')
        cls.user_ui_adapter = adapters.get('UserUIPort')
        super().setUpClass()

    def test_login(self):
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

    def test_login_user_does_not_have_settings(self):
        # This might happen if an admin user was created
        # for the django admin
        username = 'test_login_user_no_settings'
        password = 'fakepass390'
        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()

        with self.assertRaises(AuthInvalidError):
            self.auth_adapter.login(username, password)

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
