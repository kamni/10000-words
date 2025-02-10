"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from django.test import TestCase

from app.models.app import AppSettings
from common.adapters.django_orm.app import AppSettingsDjangoORMAdapter
from common.models.app import AppSettingsDB
from common.stores.adapter import AdapterStore


class TestAppSettingsDjangoORMAdapter(TestCase):
    """
    Tests for common.adapters.app.AppSettingsDjangoORMAdapter
    """

    @classmethod
    def setUpClass(cls):
        adapters = AdapterStore(subsection='dev.django')
        cls.adapter = adapters.get('AppSettingsDBPort')
        super().setUpClass()

    def test_get(self):
        app_db = AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=False,
            show_users_on_login_screen=True,
        )
        AppSettings.objects.create(**app_db.model_dump())

        expected = app_db
        returned = self.adapter.get()
        self.assertEqual(expected, returned)

    def test_get_does_not_exist(self):
        self.assertIsNone(self.adapter.get())

    def test_get_when_multiple_exist(self):
        app_db1 = AppSettingsDB(
            multiuser_mode=False,
            passwordless_login=True,
            show_users_on_login_screen=False,
        )
        AppSettings.objects.create(**app_db1.model_dump())

        app_db2 = AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )
        AppSettings.objects.create(**app_db2.model_dump())

        expected = app_db1
        returned = self.adapter.get()
        self.assertEqual(expected, returned)
        self.assertNotEqual(app_db2, returned)

    def test_get_or_default_settings_exist(self):
        app_db1 = AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )
        AppSettings.objects.create(**app_db1.model_dump())

        expected = app_db1
        returned = self.adapter.get_or_default()
        self.assertEqual(expected, returned)

    def test_get_or_default_no_settings(self):
        expected = AppSettingsDB()
        returned = self.adapter.get_or_default()
        self.assertEqual(expected, returned)

    def test_create_or_update_when_created(self):
        app_db = AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=False,
            show_users_on_login_screen=False,
        )

        expected = app_db
        returned1 = self.adapter.create_or_update(app_db)
        self.assertEqual(expected, returned1)

        returned2 = self.adapter.get()
        self.assertEqual(expected, returned2)

    def test_create_or_update_when_updated(self):
        app_db1 = AppSettingsDB(
            multiuser_mode=False,
            passwordless_login=True,
            show_users_on_login_screen=False,
        )
        AppSettings.objects.create(**app_db1.model_dump())

        app_db2 = AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=False,
        )

        expected = app_db2
        returned = self.adapter.create_or_update(app_db2)
        self.assertEqual(expected, returned)
        self.assertEqual(1, AppSettings.objects.count())
