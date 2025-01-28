"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path
from unittest import TestCase

from common.adapters.auth import AuthnJSONFileAdapter
from common.adapters.database import DatabaseJSONFileAdapter
from common.adapters.users import UserJSONFileAdapter
from common.stores.adapter import (
    AdapterInitializationError,
    AdapterNotFoundError,
    AdapterStore,
)
from common.stores.settings import SettingsStore
from common.utils.singleton import Singleton


TEST_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent
TEST_CONFIG = TEST_CONFIG_DIR / 'config.ini'


class TestAdapterStore(TestCase):
    """
    Tests for common.stores.adapter.AdapterStore
    """

    def tearDown(self):
        Singleton.destroy(AdapterStore)
        Singleton.destroy(SettingsStore)

    def test_is_singleton(self):
        adapter_store = AdapterStore()
        adapter_store._adapters['foo'] = 'bar'

        adapter_store2 = AdapterStore()
        expected_value = 'bar'
        self.assertEqual(
            expected_value,
            adapter_store2._adapters['foo'],
        )

    def test_init_default(self):
        adapter_store = AdapterStore()
        expected_settings_name = 'default'

        self.assertEqual(
            expected_settings_name,
            adapter_store._settings._config['config.meta']['name'],
        )

    def test_init_with_custom_settings(self):
        settings_store = SettingsStore(TEST_CONFIG)
        adapter_store = AdapterStore(settings_store)
        expected_settings_name = 'testDefault'

        self.assertEqual(
            expected_settings_name,
            adapter_store._settings._config['config.meta']['name'],
        )

    def test_initialize(self):
        settings_store = SettingsStore(TEST_CONFIG)
        adapter_store = AdapterStore(settings_store)
        expected_pre_initialize_adapters = {}

        self.assertEqual(
            expected_pre_initialize_adapters,
            adapter_store._adapters,
        )

        adapter_store.initialize()
        for port in settings_store.get('ports'):
            self.assertTrue(port in adapter_store._adapters)

    def test_initialize_doesnt_override_existing_adapters(self):
        settings_store = SettingsStore(TEST_CONFIG)
        adapter_store = AdapterStore(settings_store)
        adapter_store.initialize()

        expected_value = 'override'
        for key in adapter_store._adapters.keys():
            adapter_store._adapters[key] = expected_value

        adapter_store.initialize()
        for _, value in adapter_store._adapters.items():
            self.assertEqual(
                expected_value,
                value,
            )

    def test_initialize_some_adapters_missing(self):
        settings_store = SettingsStore(TEST_CONFIG)
        adapter_store = AdapterStore(settings_store)

        ports = settings_store.get('ports')
        overridden_ports = []
        for idx, port in enumerate(ports):
            if idx % 2:
                overridden_ports.append(port)
                adapter_store._adapters[port] = 'override'

        adapter_store.initialize()
        for port in ports:
            if port in overridden_ports:
                self.assertEqual(
                    'override',
                    adapter_store._adapters[port],
                )
            else:
                adapter_cls = adapter_store._get_adapter_cls(port)
                self.assertEqual(
                    adapter_cls,
                    type(adapter_store._adapters[port]),
                )

    def test_initialize_overrides_exising_adapters_on_force(self):
        settings_store = SettingsStore(TEST_CONFIG)
        adapter_store = AdapterStore(settings_store)

        ports = settings_store.get('ports')
        for port in ports:
            adapter_store._adapters[port] = 'override'

        adapter_store.initialize(force_rebuild=True)
        for port in ports:
            adapter_cls = adapter_store._get_adapter_cls(port)
            self.assertEqual(
                adapter_cls,
                type(adapter_store._adapters[port]),
            )

    def test_initialize_waits_to_end_to_aggregate_errors(self):
        settings_store = SettingsStore(TEST_CONFIG)
        adapter_store = AdapterStore(settings_store)

        ports = settings_store.get('ports')
        overridden_config = []
        for idx, port in enumerate(ports):
            if idx % 2:
                overridden_config.append(port)
                settings_store._config[f'{settings_store.subsection}.ports'][port] = 'override'

        with self.assertRaises(Exception) as exc:
            adapter_store.initialize()
        self.assertEqual(
            AdapterInitializationError,
            type(exc.exception),
        )

        # We expect to ports to be initialized,
        # and two ports to have errored and not initialized
        for port in ports:
            if port in overridden_config:
                self.assertFalse(port in adapter_store._adapters)
            else:
                self.assertTrue(port in adapter_store._adapters)

    def test_get(self):
        settings_store = SettingsStore(TEST_CONFIG)
        adapter_store = AdapterStore(settings_store)
        adapter_store.initialize()

        # Not testing all ports; just a few for examples
        port_to_adapter_cls = {
            'AuthnPort': AuthnJSONFileAdapter,
            'DatabasePort': DatabaseJSONFileAdapter,
            'UserPort': UserJSONFileAdapter,
        }

        for port, adapter_cls in port_to_adapter_cls.items():
            self.assertEqual(
                adapter_cls,
                type(adapter_store.get(port)),
            )

    def test_get_throws_error_if_adapter_not_found(self):
        settings_store = SettingsStore(TEST_CONFIG)
        adapter_store = AdapterStore(settings_store)
        adapter_store.initialize()

        with self.assertRaises(AdapterNotFoundError):
            adapter_store.get('FooBarPort')
