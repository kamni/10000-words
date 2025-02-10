"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from django.test import TestCase

from app.models.app import AppSettings
from common.adapters.django_orm.auth import AuthInvalidError
from common.adapters.django_orm.users import UserDBDjangoORMAdapter
from common.adapters.ui.users import UserUIAdapter
from common.stores.adapter import AdapterStore
from common.stores.app import AppSettingsStore
from common.stores.config import ConfigStore
from common.utils.singleton import Singleton

from ...utils.users import make_user_db, make_user_ui


class TestAppSettingsStore(TestCase):
    """
    Tests for common.stores.auth.AppSettingsStore
    """

    @classmethod
    def setUpClass(cls):
        # Get rid of lurking instances before starting tests
        Singleton.destroy(AdapterStore)
        Singleton.destroy(AppSettingsStore)
        Singleton.destroy(ConfigStore)

        adapter_store = AdapterStore(subsection='dev.django')
        super().setUpClass()

    def tearDown(self):
        Singleton.destroy(AppSettingsStore)

    def test_is_singleton(self):
        app_store1 = AppSettingsStore()
        self.assertFalse(app_store1.get(AppSettingsStore.IS_CONFIGURED))

        AppSettings.objects.create(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )
        app_store2 = AppSettingsStore()
        self.assertFalse(app_store2.get(AppSettingsStore.IS_CONFIGURED))

    def test_initialize_already_initialized(self):
        AppSettings.objects.create(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )

        app_store = AppSettingsStore()
        self.assertTrue(app_store.get(AppSettingsStore.IS_CONFIGURED))

        AppSettings.objects.all().delete()
        app_store.initialize()
        self.assertTrue(app_store.get(AppSettingsStore.IS_CONFIGURED))

    def test_initialize_forced(self):
        AppSettings.objects.create(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )

        app_store = AppSettingsStore()
        self.assertTrue(app_store.get(AppSettingsStore.IS_CONFIGURED))

        AppSettings.objects.all().delete()
        app_store.initialize(force=True)
        self.assertFalse(app_store.get(AppSettingsStore.IS_CONFIGURED))

    def test_init_settings_does_not_exist(self):
        usersdb = [
            UserDBDjangoORMAdapter().create(make_user_db())
            for i in range(3)
        ]
        usersui = UserUIAdapter().get_all(usersdb)

        app_store = AppSettingsStore()
        expected = {
            AppSettingsStore.AUTOMATIC_LOGIN: False,
            AppSettingsStore.IS_CONFIGURED: False,
            AppSettingsStore.SHOW_LOGIN: False,
            AppSettingsStore.SHOW_LOGOUT: False,
            AppSettingsStore.SHOW_REGISTRATION: False,
            AppSettingsStore.SHOW_PASSWORD_FIELD: False,
            AppSettingsStore.SHOW_USER_SELECT: False,
        }
        returned = app_store._settings
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
        usersui = UserUIAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=False,
            passwordless_login=False,
            show_users_on_login_screen=False,
        )
        app_store = AppSettingsStore()

        expected = {
            AppSettingsStore.AUTOMATIC_LOGIN: False,
            AppSettingsStore.IS_CONFIGURED: True,
            AppSettingsStore.SHOW_LOGIN: True,
            AppSettingsStore.SHOW_LOGOUT: True,
            AppSettingsStore.SHOW_REGISTRATION: False,
            AppSettingsStore.SHOW_PASSWORD_FIELD: True,
            AppSettingsStore.SHOW_USER_SELECT: False,
        }
        returned = app_store._settings
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
        usersui = UserUIAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=True,
            passwordless_login=False,
            show_users_on_login_screen=False,
        )
        app_store = AppSettingsStore()

        expected = {
            AppSettingsStore.AUTOMATIC_LOGIN: False,
            AppSettingsStore.IS_CONFIGURED: True,
            AppSettingsStore.SHOW_LOGIN: True,
            AppSettingsStore.SHOW_LOGOUT: True,
            AppSettingsStore.SHOW_REGISTRATION: True,
            AppSettingsStore.SHOW_PASSWORD_FIELD: True,
            AppSettingsStore.SHOW_USER_SELECT: False,
        }
        returned = app_store._settings
        self.assertEqual(expected, returned)

    def test_init_settings_true_false_true(self):
        """
        multiuser_mode = True
        passwordless_login = False
        show_users_on_login_screen = True
        """

        usersdb = [
            UserDBDjangoORMAdapter().create(make_user_db())
            for i in range(3)
        ]
        usersui = UserUIAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=True,
            passwordless_login=False,
            show_users_on_login_screen=True,
        )
        app_store = AppSettingsStore()

        expected = {
            AppSettingsStore.AUTOMATIC_LOGIN: False,
            AppSettingsStore.IS_CONFIGURED: True,
            AppSettingsStore.SHOW_LOGIN: True,
            AppSettingsStore.SHOW_LOGOUT: True,
            AppSettingsStore.SHOW_REGISTRATION: True,
            AppSettingsStore.SHOW_PASSWORD_FIELD: True,
            AppSettingsStore.SHOW_USER_SELECT: True,
        }
        returned = app_store._settings
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
        usersui = UserUIAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=False,
        )
        app_store = AppSettingsStore()

        expected = {
            AppSettingsStore.AUTOMATIC_LOGIN: False,
            AppSettingsStore.IS_CONFIGURED: True,
            AppSettingsStore.SHOW_LOGIN: True,
            AppSettingsStore.SHOW_LOGOUT: True,
            AppSettingsStore.SHOW_REGISTRATION: True,
            AppSettingsStore.SHOW_PASSWORD_FIELD: False,
            AppSettingsStore.SHOW_USER_SELECT: False,
        }
        returned = app_store._settings
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
        usersui = UserUIAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )
        app_store = AppSettingsStore()

        expected = {
            AppSettingsStore.AUTOMATIC_LOGIN: False,
            AppSettingsStore.IS_CONFIGURED: True,
            AppSettingsStore.SHOW_LOGIN: True,
            AppSettingsStore.SHOW_LOGOUT: True,
            AppSettingsStore.SHOW_REGISTRATION: True,
            AppSettingsStore.SHOW_PASSWORD_FIELD: False,
            AppSettingsStore.SHOW_USER_SELECT: True,
        }
        returned = app_store._settings
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
        usersui = UserUIAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=False,
            passwordless_login=True,
            show_users_on_login_screen=False,
        )
        app_store = AppSettingsStore()

        expected = {
            AppSettingsStore.AUTOMATIC_LOGIN: True,
            AppSettingsStore.IS_CONFIGURED: True,
            AppSettingsStore.SHOW_LOGIN: False,
            AppSettingsStore.SHOW_LOGOUT: False,
            AppSettingsStore.SHOW_REGISTRATION: False,
            AppSettingsStore.SHOW_PASSWORD_FIELD: False,
            AppSettingsStore.SHOW_USER_SELECT: False,
        }
        returned = app_store._settings
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
        app_store = AppSettingsStore()

        expected = {
            AppSettingsStore.AUTOMATIC_LOGIN: False,
            AppSettingsStore.IS_CONFIGURED: True,
            AppSettingsStore.SHOW_LOGIN: True,
            AppSettingsStore.SHOW_LOGOUT: False,
            AppSettingsStore.SHOW_REGISTRATION: True,
            AppSettingsStore.SHOW_PASSWORD_FIELD: False,
            AppSettingsStore.SHOW_USER_SELECT: False,
        }
        returned = app_store._settings
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
        usersui = UserUIAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=False,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )
        app_store = AppSettingsStore()

        expected = {
            AppSettingsStore.AUTOMATIC_LOGIN: True,
            AppSettingsStore.IS_CONFIGURED: True,
            AppSettingsStore.SHOW_LOGIN: False,
            AppSettingsStore.SHOW_LOGOUT: False,
            AppSettingsStore.SHOW_REGISTRATION: False,
            AppSettingsStore.SHOW_PASSWORD_FIELD: False,
            AppSettingsStore.SHOW_USER_SELECT: False,
        }
        returned = app_store._settings
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
        usersui = UserUIAdapter().get_all(usersdb)

        AppSettings.objects.create(
            multiuser_mode=False,
            passwordless_login=False,
            show_users_on_login_screen=True,
        )
        app_store = AppSettingsStore()

        expected = {
            AppSettingsStore.AUTOMATIC_LOGIN: False,
            AppSettingsStore.IS_CONFIGURED: True,
            AppSettingsStore.SHOW_LOGIN: True,
            AppSettingsStore.SHOW_LOGOUT: True,
            AppSettingsStore.SHOW_REGISTRATION: False,
            AppSettingsStore.SHOW_PASSWORD_FIELD: True,
            AppSettingsStore.SHOW_USER_SELECT: True,
        }
        returned = app_store._settings
        self.assertEqual(expected, returned)

    def test_automatic_login(self):
        app_store = AppSettingsStore()
        app_store._settings[AppSettingsStore.AUTOMATIC_LOGIN] = True
        self.assertTrue(app_store.automatic_login)

        app_store._settings[AppSettingsStore.AUTOMATIC_LOGIN] = False
        self.assertFalse(app_store.automatic_login)

    def test_is_configured(self):
        app_store = AppSettingsStore()
        app_store._settings[AppSettingsStore.IS_CONFIGURED] = True
        self.assertTrue(app_store.is_configured)

        app_store._settings[AppSettingsStore.IS_CONFIGURED] = False
        self.assertFalse(app_store.is_configured)

    def test_show_login(self):
        app_store = AppSettingsStore()
        app_store._settings[AppSettingsStore.SHOW_LOGIN] = True
        self.assertTrue(app_store.show_login)

        app_store._settings[AppSettingsStore.SHOW_LOGIN] = False
        self.assertFalse(app_store.show_login)

    def test_show_logout(self):
        app_store = AppSettingsStore()
        app_store._settings[AppSettingsStore.SHOW_LOGOUT] = True
        self.assertTrue(app_store.show_logout)

        app_store._settings[AppSettingsStore.SHOW_LOGOUT] = False
        self.assertFalse(app_store.show_logout)

    def test_show_registration(self):
        app_store = AppSettingsStore()
        app_store._settings[AppSettingsStore.SHOW_REGISTRATION] = True
        self.assertTrue(app_store.show_registration)

        app_store._settings[AppSettingsStore.SHOW_REGISTRATION] = False
        self.assertFalse(app_store.show_registration)

    def test_show_password_field(self):
        app_store = AppSettingsStore()
        app_store._settings[AppSettingsStore.SHOW_PASSWORD_FIELD] = True
        self.assertTrue(app_store.show_password_field)

        app_store._settings[AppSettingsStore.SHOW_PASSWORD_FIELD] = False
        self.assertFalse(app_store.show_password_field)

    def test_show_user_select(self):
        app_store = AppSettingsStore()
        app_store._settings[AppSettingsStore.SHOW_USER_SELECT] = True
        self.assertTrue(app_store.show_user_select)

        app_store._settings[AppSettingsStore.SHOW_USER_SELECT] = False
        self.assertFalse(app_store.show_user_select)

    def test_get(self):
        app_store = AppSettingsStore()
        for key, value in app_store._settings.items():
            expected = value
            returned = app_store.get(key)
            self.assertEqual(expected, returned)

    def test_get_setting_does_not_exist(self):
        app_store = AppSettingsStore()
        with self.assertRaises(KeyError):
            app_store.get('foo')
