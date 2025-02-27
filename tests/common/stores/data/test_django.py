"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase

import common.stores.data.django
from common.stores.app import AppStore
from common.stores.data.django import DjangoDBStore
from common.stores.data.in_memory import InMemoryDBStore
from common.utils.files import get_project_dir


PROJECT_DIR = get_project_dir()
PROJECT_CONF = PROJECT_DIR / 'setup.cfg'
TEST_CONF = PROJECT_DIR / 'tests' / 'setup.cfg'


class TestDjangDBStore(TestCase):
    """
    Tests for common.stores.data.django.DjangoDBStore
    """

    @classmethod
    def setUpClass(self):
        AppStore.destroy_all()
        super().setUpClass()

    def tearDown(self):
        AppStore.destroy_all()

    def test_init(self):
        app = AppStore(config=TEST_CONF, subsection='loadtest.django')
        data_store = app.get('DataStore')
        self.assertTrue(data_store.should_load_data)
        self.assertFalse(data_store._data_is_loaded)

        data_store.load_data()
        self.assertTrue(data_store._data_is_loaded)

    def test_setup(self):
        # Verify that the command we expect is getting called
        with mock.patch('common.stores.data.django.call_command') as call_command:
            store = DjangoDBStore()
            call_command.assert_called_once_with('migrate')

        # Just ensure this doesn't error
        store = DjangoDBStore()
        try:
            store.setup()
        except Exception:
            self.assertEqual('Unexpected failure in DjangoDBStore.setup', False)

    def test_drop(self):
        # Verify that the command we expect is getting called
        with mock.patch('common.stores.data.django.call_command') as call_command:
            store = DjangoDBStore()
            store.drop()
            call_command.assert_called_with('flush', '--no-input')

        # Verify the command does what we think it should
        User.objects.create(username='some-user')
        self.assertEqual(1, User.objects.all().count())
        store = DjangoDBStore()
        store.drop()
        self.assertEqual(0, User.objects.all().count())

    def test_load_data(self):
        app = AppStore(config=TEST_CONF, subsection='dev.django')
        store = app.get('DataStore')
        self.assertTrue(isinstance(store, DjangoDBStore))
        # We have to hack this a bit for the test,
        # because the default is not to load data
        store.should_load_data = True

        self.assertEqual(0, User.objects.all().count())
        store.load_data()
        self.assertTrue(User.objects.all().count() > 0)

    def test_load_data_not_allowed(self):
        app = AppStore(config=TEST_CONF, subsection='dev.django')
        store = app.get('DataStore')
        self.assertTrue(isinstance(store, DjangoDBStore))
        self.assertFalse(store.should_load_data)

        self.assertEqual(0, User.objects.all().count())
        store.load_data()
        self.assertEqual(0, User.objects.all().count())

    def test_load_data_without_force(self):
        app = AppStore(config=TEST_CONF, subsection='dev.django')
        store = DjangoDBStore()
        # We have to hack this a bit for the test,
        # because the default is not to load data
        store.should_load_data = True
        store._data_is_loaded = True

        self.assertEqual(0, User.objects.all().count())
        store.load_data()
        self.assertEqual(0, User.objects.all().count())

    def test_load_data_with_force(self):
        app = AppStore(config=TEST_CONF, subsection='dev.django')
        store = DjangoDBStore()

        self.assertEqual(0, User.objects.all().count())
        store.load_data(force=True)
        self.assertTrue(User.objects.all().count() > 0)
