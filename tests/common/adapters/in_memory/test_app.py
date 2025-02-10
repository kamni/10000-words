"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path
from unittest import TestCase

from common.adapters.in_memory.app import AppSettingsInMemoryAdapter
from common.models.app import AppSettingsDB
from common.stores.adapter import AdapterStore
from common.stores.config import ConfigStore
from common.stores.in_memory import InMemoryDBStore
from common.utils.singleton import Singleton

TEST_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEST_CONFIG = TEST_CONFIG_DIR / 'setup.cfg'


class TestAppSettingsInMemoryAdapter(TestCase):
    """
    Tests for common.adapters.app.AppSettingsDjangoORMAdapter
    """

    @classmethod
    def setUpClass(cls):
        # Cleanup, in case other tests missed it
        Singleton.destroy(ConfigStore)
        Singleton.destroy(AdapterStore)

        adapters = AdapterStore(config=TEST_CONFIG, subsection='dev.in_memory')
        cls.adapter = adapters.get('AppSettingsDBPort')
        cls.store = InMemoryDBStore()
        super().setUpClass()

    def tearDown(self):
        Singleton.destroy(ConfigStore)
        Singleton.destroy(AdapterStore)
        self.store.drop()

    def test_get(self):
        app_db = AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=False,
            show_users_on_login_screen=True,
        )
        self.store.db.app_settings = app_db

        expected = app_db
        returned = self.adapter.get()
        self.assertEqual(expected, returned)

    def test_get_does_not_exist(self):
        self.assertIsNone(self.adapter.get())

    def test_get_or_default_settings_exist(self):
        app_db = AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )
        self.store.db.app_settings = app_db

        expected = app_db
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
        self.store.db.app_settings = app_db1

        app_db2 = AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=False,
        )

        expected = app_db2
        returned = self.adapter.create_or_update(app_db2)
        self.assertEqual(expected, returned)
