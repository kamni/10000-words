"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from django.test import TestCase

from app.models.app import AppSettings
from common.adapters.auth import AuthnInvalidError
from common.adapters.users import (
    UserDBDjangoORMAdapter,
    UserUIDjangoORMAdapter,
)
from common.stores.adapter import AdapterStore
from common.stores.auth import AuthStore
from common.stores.settings import SettingsStore
from common.utils.singleton import Singleton

from ...utils_for_tests.users import make_user_db


class TestAuthStore(TestCase):
    """
    Tests for common.stores.auth.AuthStore
    """

    @classmethod
    def setUpClass(cls):
        # Get rid of lurking instances before starting tests
        Singleton.destroy(AdapterStore)
        Singleton.destroy(AuthStore)
        Singleton.destroy(SettingsStore)

        adapter_store = AdapterStore(subsection='dev.django')
        super().setUpClass()

    def tearDown(self):
        Singleton.destroy(AuthStore)

    def test_is_singleton(self):
        auth_store1 = AuthStore()
        self.assertFalse(auth_store1.get(AuthStore.IS_CONFIGURED))

        AppSettings.objects.create(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )
        auth_store2 = AuthStore()
        self.assertFalse(auth_store2.get(AuthStore.IS_CONFIGURED))

    def test_initialize_already_initialized(self):
        AppSettings.objects.create(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )

        auth_store = AuthStore()
        self.assertTrue(auth_store.get(AuthStore.IS_CONFIGURED))

        AppSettings.objects.all().delete()
        auth_store.initialize()
        self.assertTrue(auth_store.get(AuthStore.IS_CONFIGURED))

    def test_initialize_forced(self):
        AppSettings.objects.create(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )

        auth_store = AuthStore()
        self.assertTrue(auth_store.get(AuthStore.IS_CONFIGURED))

        AppSettings.objects.all().delete()
        auth_store.initialize(force=True)
        self.assertFalse(auth_store.get(AuthStore.IS_CONFIGURED))

    def test_init_settings_does_not_exist(self):
        usersdb = [
            UserDBDjangoORMAdapter().create(make_user_db())
            for i in range(3)
        ]
        usersui = UserUIDjangoORMAdapter().get_all(usersdb)

        auth_store = AuthStore()
        expected = {
            AuthStore.LOGGED_IN_USER: None,
            AuthStore.IS_CONFIGURED: False,
            AuthStore.USER_SELECT_OPTIONS: [],
            AuthStore.SHOW_REGISTRATION: False,
            AuthStore.SHOW_PASSWORD_FIELD: False,
            AuthStore.SHOW_USER_SELECT: False,
        }
        returned = auth_store._settings
        self.assertEqual(expected, returned)

    def test_init_settings_false_false_false(self):
        """
        multiuser_mode = False
        passwordless_login = False
        show_users_on_login_screen = False
        """

        usersdb = [
            UserDBDjangoORMAdapter().create(make_user_db())
            for i in range(3)
        ]
        usersui = UserUIDjangoORMAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=False,
            passwordless_login=False,
            show_users_on_login_screen=False,
        )
        auth_store = AuthStore()

        expected = {
            AuthStore.LOGGED_IN_USER: None,
            AuthStore.IS_CONFIGURED: True,
            AuthStore.USER_SELECT_OPTIONS: [],
            AuthStore.SHOW_REGISTRATION: False,
            AuthStore.SHOW_PASSWORD_FIELD: True,
            AuthStore.SHOW_USER_SELECT: False,
        }
        returned = auth_store._settings
        self.assertEqual(expected, returned)

    def test_init_settings_true_false_false(self):
        """
        multiuser_mode = True
        passwordless_login = False
        show_users_on_login_screen = False
        """

        usersdb = [
            UserDBDjangoORMAdapter().create(make_user_db())
            for i in range(3)
        ]
        usersui = UserUIDjangoORMAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=True,
            passwordless_login=False,
            show_users_on_login_screen=False,
        )
        auth_store = AuthStore()

        expected = {
            AuthStore.LOGGED_IN_USER: None,
            AuthStore.IS_CONFIGURED: True,
            AuthStore.USER_SELECT_OPTIONS: [],
            AuthStore.SHOW_REGISTRATION: True,
            AuthStore.SHOW_PASSWORD_FIELD: True,
            AuthStore.SHOW_USER_SELECT: False,
        }
        returned = auth_store._settings
        self.assertEqual(expected, returned)

    def test_init_settings_true_true_false(self):
        """
        multiuser_mode = True
        passwordless_login = True
        show_users_on_login_screen = False
        """

        usersdb = [
            UserDBDjangoORMAdapter().create(make_user_db())
            for i in range(3)
        ]
        usersui = UserUIDjangoORMAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=False,
        )
        auth_store = AuthStore()

        expected = {
            AuthStore.LOGGED_IN_USER: None,
            AuthStore.IS_CONFIGURED: True,
            AuthStore.USER_SELECT_OPTIONS: [],
            AuthStore.SHOW_REGISTRATION: True,
            AuthStore.SHOW_PASSWORD_FIELD: False,
            AuthStore.SHOW_USER_SELECT: False,
        }
        returned = auth_store._settings
        self.assertEqual(expected, returned)

    def test_init_settings_true_true_true(self):
        """
        multiuser_mode = True
        passwordless_login = True
        show_users_on_login_screen = True
        """

        usersdb = [
            UserDBDjangoORMAdapter().create(make_user_db())
            for i in range(3)
        ]
        usersui = UserUIDjangoORMAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )
        auth_store = AuthStore()

        expected = {
            AuthStore.LOGGED_IN_USER: None,
            AuthStore.IS_CONFIGURED: True,
            AuthStore.USER_SELECT_OPTIONS: usersui,
            AuthStore.SHOW_REGISTRATION: True,
            AuthStore.SHOW_PASSWORD_FIELD: False,
            AuthStore.SHOW_USER_SELECT: True,
        }
        returned = auth_store._settings
        self.assertEqual(expected, returned)

    def test_init_settings_false_true_false(self):
        """
        mutliuser_mode = False
        passwordless_login = True
        show_users_on_login_screen = False
        """

        usersdb = [
            UserDBDjangoORMAdapter().create(make_user_db())
            for i in range(3)
        ]
        usersui = UserUIDjangoORMAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=False,
            passwordless_login=True,
            show_users_on_login_screen=False,
        )
        auth_store = AuthStore()

        expected = {
            AuthStore.LOGGED_IN_USER: usersui[0],
            AuthStore.IS_CONFIGURED: True,
            AuthStore.USER_SELECT_OPTIONS: [],
            AuthStore.SHOW_REGISTRATION: False,
            AuthStore.SHOW_PASSWORD_FIELD: False,
            AuthStore.SHOW_USER_SELECT: False,
        }
        returned = auth_store._settings
        self.assertEqual(expected, returned)

    def test_init_settings_false_true_false_no_users(self):
        """
        mutliuser_mode = False
        passwordless_login = True
        show_users_on_login_screen = False
        """

        AppSettings.objects.create(
            multiuser_mode=False,
            passwordless_login=True,
            show_users_on_login_screen=False,
        )
        auth_store = AuthStore()

        expected = {
            AuthStore.LOGGED_IN_USER: None,
            AuthStore.IS_CONFIGURED: True,
            AuthStore.USER_SELECT_OPTIONS: [],
            AuthStore.SHOW_REGISTRATION: True,
            AuthStore.SHOW_PASSWORD_FIELD: False,
            AuthStore.SHOW_USER_SELECT: False,
        }
        returned = auth_store._settings
        self.assertEqual(expected, returned)

    def test_init_settings_false_true_true(self):
        """
        multiuser_mode = False
        passwordless_login = True
        show_users_on_login_screen = True
        """

        usersdb = [
            UserDBDjangoORMAdapter().create(make_user_db())
            for i in range(3)
        ]
        usersui = UserUIDjangoORMAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=False,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )
        auth_store = AuthStore()

        expected = {
            AuthStore.LOGGED_IN_USER: usersui[0],
            AuthStore.IS_CONFIGURED: True,
            AuthStore.USER_SELECT_OPTIONS: [],
            AuthStore.SHOW_REGISTRATION: False,
            AuthStore.SHOW_PASSWORD_FIELD: False,
            AuthStore.SHOW_USER_SELECT: False,
        }
        returned = auth_store._settings
        self.assertEqual(expected, returned)

    def test_init_settings_false_false_true(self):
        """
        multiuser_mode = False
        passwordless_login = False
        show_users_on_login_screen = True
        """

        usersdb = [
            UserDBDjangoORMAdapter().create(make_user_db())
            for i in range(3)
        ]
        usersui = UserUIDjangoORMAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=False,
            passwordless_login=False,
            show_users_on_login_screen=True,
        )
        auth_store = AuthStore()

        expected = {
            AuthStore.LOGGED_IN_USER: None,
            AuthStore.IS_CONFIGURED: True,
            AuthStore.USER_SELECT_OPTIONS: [usersui[0]],
            AuthStore.SHOW_REGISTRATION: False,
            AuthStore.SHOW_PASSWORD_FIELD: True,
            AuthStore.SHOW_USER_SELECT: True,
        }
        returned = auth_store._settings
        self.assertEqual(expected, returned)

    def test_login(self):
        auth_store = AuthStore()
        user = make_user_db()
        userdb = UserDBDjangoORMAdapter().create(user)

        expected = UserUIDjangoORMAdapter().get(userdb)
        returned = auth_store.login(user.username, user.password)
        self.assertEqual(expected, returned)

        self.assertEqual(expected, auth_store.get(AuthStore.LOGGED_IN_USER))

    def test_login_user_does_not_exist(self):
        auth_store = AuthStore()
        with self.assertRaises(AuthnInvalidError):
            auth_store.login('foo', 'bar')

    def test_login_user_has_no_password(self):
        auth_store = AuthStore()
        user = make_user_db(password=None)
        userdb = UserDBDjangoORMAdapter().create(user)

        with self.assertRaises(AuthnInvalidError):
            auth_store.login(user.username, user.password)

    def test_login_passwordless_login(self):
        pass

    def test_login_passwordless_login_user_does_not_exist(self):
        pass

    def test_get_setting_does_not_exist(self):
        pass

    def test_logout(self):
        pass

    def test_logout_user_not_logged_in(self):
        pass
