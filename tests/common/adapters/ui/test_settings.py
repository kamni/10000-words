"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from unittest import TestCase

from common.adapters.in_memory.users import UserDBInMemoryAdapter
from common.adapters.ui.settings import AppSettingsUIAdapter
from common.models.settings import AppSettingsDB, AppSettingsUI
from common.stores.data.in_memory import InMemoryDBStore
from common.utils.singleton import Singleton
from tests.utils.users import make_user_db


class TestAppSettingsUIAdapter(TestCase):
    """
    Tests for common.adapters.ui.settings.AppSettingsUIAdapter
    """

    def tearDown(self):
        Singleton.destroy(InMemoryDBStore)

    def test_get_settings_does_not_exist(self):
        settings = AppSettingsUIAdapter()
        expected = AppSettingsUI(
            automatic_login=False,
            is_configured=False,
            show_login=False,
            show_logout=False,
            show_registration=False,
            show_password_field=False,
            show_user_select=False,
        )
        returned = settings.get(None)
        self.assertEqual(expected, returned)

    def test_get_settings_false_false_false(self):
        """
        multiuser_mode = False
        passwordless_login = False
        show_users_on_login_screen = False
        """

        UserDBInMemoryAdapter().create(make_user_db())

        settings_db = AppSettingsDB(
            multiuser_mode=False,
            passwordless_login=False,
            show_users_on_login_screen=False,
        )
        settings = AppSettingsUIAdapter()

        expected = AppSettingsUI(
            automatic_login=False,
            is_configured=True,
            show_login=True,
            show_logout=True,
            show_registration=False,
            show_password_field=True,
            show_user_select=False,
        )
        returned = settings.get(settings_db)
        self.assertEqual(expected, returned)

    def test_get_settings_true_false_false(self):
        """
        multiuser_mode = True
        passwordless_login = False
        show_users_on_login_screen = False
        """

        UserDBInMemoryAdapter().create(make_user_db())

        settings_db = AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=False,
            show_users_on_login_screen=False,
        )
        settings = AppSettingsUIAdapter()

        expected = AppSettingsUI(
            automatic_login=False,
            is_configured=True,
            show_login=True,
            show_logout=True,
            show_registration=True,
            show_password_field=True,
            show_user_select=False,
        )
        returned = settings.get(settings_db)
        self.assertEqual(expected, returned)

    def test_get_settings_true_false_true(self):
        """
        multiuser_mode = True
        passwordless_login = False
        show_users_on_login_screen = True
        """
        UserDBInMemoryAdapter().create(make_user_db())

        settings_db = AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=False,
            show_users_on_login_screen=True,
        )
        settings = AppSettingsUIAdapter()

        expected = AppSettingsUI(
            automatic_login=False,
            is_configured=True,
            show_login=True,
            show_logout=True,
            show_registration=True,
            show_password_field=True,
            show_user_select=True,
        )
        returned = settings.get(settings_db)
        self.assertEqual(expected, returned)

    def test_get_settings_true_true_false(self):
        """
        multiuser_mode = True
        passwordless_login = True
        show_users_on_login_screen = False
        """
        UserDBInMemoryAdapter().create(make_user_db())

        settings_db = AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=False,
        )
        settings = AppSettingsUIAdapter()

        expected = AppSettingsUI(
            automatic_login=False,
            is_configured=True,
            show_login=True,
            show_logout=True,
            show_registration=True,
            show_password_field=False,
            show_user_select=False,
        )
        returned = settings.get(settings_db)
        self.assertEqual(expected, returned)

    def test_get_settings_true_true_true(self):
        """
        multiuser_mode = True
        passwordless_login = True
        show_users_on_login_screen = True
        """
        UserDBInMemoryAdapter().create(make_user_db())

        settings_db = AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )
        settings = AppSettingsUIAdapter()

        expected = AppSettingsUI(
            automatic_login=False,
            is_configured=True,
            show_login=True,
            show_logout=True,
            show_registration=True,
            show_password_field=False,
            show_user_select=True,
        )
        returned = settings.get(settings_db)
        self.assertEqual(expected, returned)

    def test_get_settings_false_true_false(self):
        """
        mutliuser_mode = False
        passwordless_login = True
        show_users_on_login_screen = False
        """
        UserDBInMemoryAdapter().create(make_user_db())

        settings_db = AppSettingsDB(
            multiuser_mode=False,
            passwordless_login=True,
            show_users_on_login_screen=False,
        )
        settings = AppSettingsUIAdapter()

        expected = AppSettingsUI(
            automatic_login=True,
            is_configured=True,
            show_login=False,
            show_logout=False,
            show_registration=False,
            show_password_field=False,
            show_user_select=False,
        )
        returned = settings.get(settings_db)
        self.assertEqual(expected, returned)

    def test_get_settings_false_true_false_no_users(self):
        """
        mutliuser_mode = False
        passwordless_login = True
        show_users_on_login_screen = False
        """

        settings_db = AppSettingsDB(
            multiuser_mode=False,
            passwordless_login=True,
            show_users_on_login_screen=False,
        )
        settings = AppSettingsUIAdapter()

        expected = AppSettingsUI(
            automatic_login=False,
            is_configured=True,
            show_login=True,
            show_logout=False,
            show_registration=True,
            show_password_field=False,
            show_user_select=False,
        )
        returned = settings.get(settings_db)
        self.assertEqual(expected, returned)

    def test_get_settings_false_true_true(self):
        """
        multiuser_mode = False
        passwordless_login = True
        show_users_on_login_screen = True
        """
        UserDBInMemoryAdapter().create(make_user_db())

        settings_db = AppSettingsDB(
            multiuser_mode=False,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )
        settings = AppSettingsUIAdapter()

        expected = AppSettingsUI(
            automatic_login=True,
            is_configured=True,
            show_login=False,
            show_logout=False,
            show_registration=False,
            show_password_field=False,
            show_user_select=False,
        )
        returned = settings.get(settings_db)
        self.assertEqual(expected, returned)

    def test_get_settings_false_false_true(self):
        """
        multiuser_mode = False
        passwordless_login = False
        show_users_on_login_screen = True
        """
        UserDBInMemoryAdapter().create(make_user_db())

        settings_db = AppSettingsDB(
            multiuser_mode=False,
            passwordless_login=False,
            show_users_on_login_screen=True,
        )
        settings = AppSettingsUIAdapter()

        expected = AppSettingsUI(
            automatic_login=False,
            is_configured=True,
            show_login=True,
            show_logout=True,
            show_registration=False,
            show_password_field=True,
            show_user_select=True,
        )
        returned = settings.get(settings_db)
        self.assertEqual(expected, returned)
