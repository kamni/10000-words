"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import configparser
import os

from django.test import TestCase

from common.adapters.ui.users import UserUIAdapter
from common.stores.adapter import AdapterStore
from common.stores.app import (
    AppStore,
    StoreNotFoundError,
    StoreInitializationError,
)
from common.stores.config import ConfigStore
from common.stores.data import DjangoDBStore, InMemoryDBStore
from common.stores.data.base import BaseDataStore
from common.utils.files import get_project_dir
from tests.utils.stores import FakeErrorStore, FakeStore


PROJECT_DIR = get_project_dir()
PROJECT_CONFIG = os.path.join(PROJECT_DIR, 'setup.cfg')
TEST_CONFIG = os.path.join(PROJECT_DIR, 'tests', 'setup.cfg')


class TestAppStore(TestCase):
    """
    Tests for common.stores.app.AppStore
    """

    @classmethod
    def setUpClass(cls):
        AppStore.destroy_all()
        super().setUpClass()

    def tearDown(self):
        AppStore.destroy_all()

    def test_init_default(self):
        app = AppStore()

        config_store = app.get('ConfigStore')
        config = configparser.ConfigParser()
        config.read(PROJECT_CONFIG)
        expected_subsection = config['config.meta']['defaultconfig']

        self.assertEqual(PROJECT_CONFIG, config_store.config)
        # We expect ConfigStore will read the section from the file
        self.assertIsNone(app._subsection)
        self.assertEqual(expected_subsection, config_store.subsection)

        for store in app.STORES:
            self.assertIsNotNone(app.get(store))

    def test_init_custom_config(self):
        app = AppStore(config=TEST_CONFIG)

        config_store = app.get('ConfigStore')
        config = configparser.ConfigParser()
        config.read(TEST_CONFIG)
        expected_subsection = config['config.meta']['defaultconfig']

        self.assertEqual(TEST_CONFIG, config_store.config)
        # We expect ConfigStore will read the section from the file
        self.assertIsNone(app._subsection)
        self.assertEqual(expected_subsection, config_store.subsection)

        for store in app.STORES:
            self.assertIsNotNone(app.get(store))

    def test_init_custom_subsection(self):
        expected_subsection = 'dev.in_memory'
        app = AppStore(subsection=expected_subsection)
        config_store = app.get('ConfigStore')

        self.assertEqual(PROJECT_CONFIG, config_store.config)
        self.assertEqual(app._subsection, expected_subsection)
        self.assertEqual(expected_subsection, config_store.subsection)

    def test_init_custom_config_and_subsection(self):
        expected_config = TEST_CONFIG
        expected_subsection = 'test'
        app = AppStore(config=expected_config, subsection=expected_subsection)
        config_store = app.get('ConfigStore')

        self.assertEqual(expected_config, app._config_file)
        self.assertEqual(expected_subsection, app._subsection)
        self.assertEqual(expected_config, config_store.config)
        self.assertEqual(expected_subsection, config_store.subsection)

    def test_init_wait_to_initialize(self):
        app = AppStore(wait_to_initialize=True)
        self.assertEqual({}, app._stores)
        self.assertFalse(app._initialized)

    def test_destroy_all(self):
        config = configparser.ConfigParser()
        config.read(PROJECT_CONFIG)
        expected_subsection = config['config.meta']['defaultconfig']

        app = AppStore()
        self.assertEqual(PROJECT_CONFIG, app._config.config)
        self.assertEqual(expected_subsection, app._config.subsection)
        # smoke test stores
        adapters = app.get('AdapterStore')
        userui_adapter = adapters.get('UserUIPort')
        self.assertTrue(isinstance(userui_adapter, UserUIAdapter))

        app2 = AppStore()

        self.assertEqual(PROJECT_CONFIG, app2._config.config)
        self.assertEqual(expected_subsection, app2._config.subsection)
        # smoke test stores
        adapters = app.get('AdapterStore')
        userui_adapter = adapters.get('UserUIPort')
        self.assertTrue(isinstance(userui_adapter, UserUIAdapter))

        # destroy_all lets us re-initialize
        AppStore.destroy_all()
        app3 = AppStore(config=TEST_CONFIG, subsection='test')
        self.assertEqual(TEST_CONFIG, app3._config.config)
        self.assertEqual('test', app3._config.subsection)
        for name, store in app3._stores.items():
            # Config store is always a ConfigStore
            if name != 'configstore':
                self.assertTrue(isinstance(store, FakeStore))

    def test_get(self):
        app = AppStore()
        for cls, cls_name in [
            (ConfigStore, 'ConfigStore'),
            (BaseDataStore, 'DataStore'),
            (AdapterStore, 'AdapterStore'),
        ]:
            self.assertTrue(isinstance(app.get(cls_name), cls))

    def test_get_store_does_not_exist(self):
        app = AppStore()
        with self.assertRaises(StoreNotFoundError):
            app.get('FooStore')

    def test_get_initializes_unconfigured_store(self):
        app = AppStore(wait_to_initialize=True)
        self.assertFalse(app._initialized)
        self.assertEqual({}, app._stores)

        adapters = app.get('AdapterStore')
        self.assertIsNotNone(adapters)
        self.assertTrue(app._initialized)

    def test_initialize_django_data_store(self):
        app = AppStore(subsection='dev.django')
        data_store = app.get('DataStore')
        self.assertTrue(isinstance(data_store, DjangoDBStore))

    def test_initialize_in_memory_data_store(self):
        app = AppStore(subsection='dev.in_memory')
        data_store = app.get('DataStore')
        self.assertTrue(isinstance(data_store, InMemoryDBStore))

    def test_initialize_store_errors(self):
        # test3 is configured with fake stores that throw errors
        with self.assertRaises(StoreInitializationError):
            AppStore(config=TEST_CONFIG, subsection='test3')

    def test_initialize_does_not_overwrite_existing_stores(self):
        app = AppStore(subsection='dev.in_memory')
        data_store = app.get('DataStore')
        self.assertTrue(isinstance(data_store, InMemoryDBStore))

        app.initialize()
        data_store = app.get('DataStore')
        self.assertTrue(isinstance(data_store, InMemoryDBStore))

    def test_initialize_overwrites_existing_stores_if_force(self):
        app = AppStore(subsection='dev.in_memory')
        data_store = app.get('DataStore')
        self.assertTrue(isinstance(data_store, InMemoryDBStore))

        app._subsection = 'dev.django'
        app.initialize(force=True)
        data_store = app.get('DataStore')
        self.assertTrue(isinstance(data_store, DjangoDBStore))

    def test_initialize_runs_custom_init_script(self):
        foo = FakeStore(foo='foo')
        self.assertEqual(foo._foo, 'foo')

        config_store = ConfigStore(config=TEST_CONFIG, subsection='test')
        AppStore()
        self.assertEqual(foo._foo, 'bar')

    def test_initialize_no_custom_init_script(self):
        foo = FakeStore(foo='foo')
        self.assertEqual(foo._foo, 'foo')

        ConfigStore(config=TEST_CONFIG, subsection='test2')
        AppStore()
        self.assertEqual(foo._foo, 'foo')
