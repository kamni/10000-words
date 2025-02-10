"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path
from unittest import TestCase

from common.adapters.django_orm.users import UserDBDjangoORMAdapter
from common.adapters.ui.users import UserUIAdapter
from common.stores.adapter import (
    AdapterInitializationError,
    AdapterNotFoundError,
    AdapterStore,
)
from common.stores.config import ConfigStore
from common.utils.singleton import Singleton

from ...utils.init_scripts import FakeStore

TEST_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent
TEST_CONFIG = TEST_CONFIG_DIR / 'setup.cfg'


class TestAdapterStore(TestCase):
    """
    Tests for common.stores.adapter.AdapterStore
    """

    @classmethod
    def setUpClass(cls):
        # Get rid of lurking instances before starting tests
        Singleton.destroy(AdapterStore)
        Singleton.destroy(ConfigStore)
        Singleton.destroy(FakeStore)
        super().setUpClass()

    def tearDown(self):
        Singleton.destroy(AdapterStore)
        Singleton.destroy(ConfigStore)
        Singleton.destroy(FakeStore)

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
        adapter_store = AdapterStore(config=TEST_CONFIG)
        expected_settings_name = 'testDefault'

        self.assertEqual(
            expected_settings_name,
            adapter_store._settings._config['config.meta']['name'],
        )

    def test_initialize_at_init(self):
        adapter_store = AdapterStore(config=TEST_CONFIG)
        for port in adapter_store._settings.get('ports'):
            self.assertTrue(port in adapter_store._adapters)

    def test_initialize_custom_init_script(self):
        foo = FakeStore('foo')
        self.assertEqual(foo._foo, 'foo')

        adapter_store = AdapterStore(config=TEST_CONFIG, subsection='test')
        self.assertEqual(foo._foo, 'bar')

    def test_initialize_no_custom_init_script(self):
        foo = FakeStore('foo')
        self.assertEqual(foo._foo, 'foo')

        adapter_store = AdapterStore(config=TEST_CONFIG, subsection='test2')
        self.assertEqual(foo._foo, 'foo')

    def test_initialize_doesnt_override_existing_adapters(self):
        adapter_store = AdapterStore(config=TEST_CONFIG)

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
        adapter_store = AdapterStore(config=TEST_CONFIG)

        ports = adapter_store._settings.get('ports')
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
        adapter_store = AdapterStore(config=TEST_CONFIG)

        ports = adapter_store._settings.get('ports')
        for port in ports:
            adapter_store._adapters[port] = 'override'

        adapter_store.initialize(force=True)
        for port in ports:
            adapter_cls = adapter_store._get_adapter_cls(port)
            self.assertEqual(
                adapter_cls,
                type(adapter_store._adapters[port]),
            )

    def test_initialize_waits_to_end_to_aggregate_errors(self):
        adapter_store = AdapterStore(config=TEST_CONFIG)

        ports = adapter_store._settings.get('ports')
        overridden_config = []
        for idx, port in enumerate(ports):
            if idx % 2:
                overridden_config.append(port)
                adapter_store._settings._config[
                    f'{adapter_store._settings.subsection}.ports'
                ][port] = 'override'

        with self.assertRaises(Exception) as exc:
            adapter_store.initialize(force=True)
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
        adapter_store = AdapterStore(config=TEST_CONFIG)

        # Not testing all ports; just a few for examples
        port_to_adapter_cls = {
            'UserDBPort': UserDBDjangoORMAdapter,
            'UserUIPort': UserUIAdapter,
        }

        for port, adapter_cls in port_to_adapter_cls.items():
            self.assertEqual(
                adapter_cls,
                type(adapter_store.get(port)),
            )

    def test_get_throws_error_if_adapter_not_found(self):
        adapter_store = AdapterStore(config=TEST_CONFIG)
        with self.assertRaises(AdapterNotFoundError):
            adapter_store.get('FooBarPort')
