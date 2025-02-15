"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path

import pytest
from django.test import TestCase

from common.adapters.django_orm.users import UserDBDjangoORMAdapter
from common.adapters.ui.users import UserUIAdapter
from common.stores.adapter import (
    AdapterInitializationError,
    AdapterNotFoundError,
    AdapterStore,
)
from common.stores.app import AppStore


TEST_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent
TEST_CONFIG = TEST_CONFIG_DIR / 'setup.cfg'


class TestAdapterStore(TestCase):
    """
    Tests for common.stores.adapter.AdapterStore
    """

    @classmethod
    def setUpClass(cls):
        AppStore.destroy_all()
        super().setUpClass()

    def setUp(self):
        AppStore(config=TEST_CONFIG, subsection='dev.in_memory')

    def tearDown(self):
        AppStore.destroy_all()

    def test_is_singleton(self):
        adapter_store = AdapterStore()
        adapter_store._adapters['foo'] = 'bar'

        adapter_store2 = AdapterStore()
        expected_value = 'bar'
        self.assertEqual(
            expected_value,
            adapter_store2._adapters['foo'],
        )

    def test_initialize_at_init(self):
        adapter_store = AdapterStore()
        for port in adapter_store._config.get('ports'):
            self.assertTrue(port in adapter_store._adapters)

    def test_initialize_doesnt_override_existing_adapters(self):
        adapter_store = AdapterStore()

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
        adapter_store = AdapterStore()

        ports = adapter_store._config.get('ports')
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
        adapter_store = AdapterStore()

        ports = adapter_store._config.get('ports')
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
        adapter_store = AdapterStore()

        ports = adapter_store._config.get('ports')
        overridden_config = []
        for idx, port in enumerate(ports):
            if idx % 2:
                overridden_config.append(port)
                adapter_store._config._config[
                    f'{adapter_store._config.subsection}.ports'
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
        AppStore.destroy_all()
        AppStore(config=TEST_CONFIG, subsection='dev.django')
        adapter_store = AdapterStore()

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
        AppStore.destroy_all()

    def test_get_throws_error_if_adapter_not_found(self):
        adapter_store = AdapterStore()
        with self.assertRaises(AdapterNotFoundError):
            adapter_store.get('FooBarPort')
