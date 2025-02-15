"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path

from django.contrib.auth.models import User
from django.test import TestCase

from common.adapters.in_memory.users import UserDBInMemoryAdapter
from common.models.database import Database
from common.stores.app import AppStore
from common.stores.data.django import DjangoDBStore
from common.stores.data.in_memory import InMemoryDBStore
from common.utils.files import get_project_dir
from tests.utils.documents import make_document_db
from tests.utils.users import make_user_db


PROJECT_DIR = Path(get_project_dir())
PROJECT_CONF = PROJECT_DIR / 'setup.cfg'
TEST_CONF = PROJECT_DIR / 'tests' / 'setup.cfg'


class TestInMemoryDBStore(TestCase):
    """
    Tests for common.stores.data.in_memory.InMemoryDBStore
    """

    @classmethod
    def setUpClass(self):
        AppStore.destroy_all()
        super().setUpClass()

    def tearDown(self):
        AppStore.destroy_all()

    def test_init(self):
        app = AppStore(config=TEST_CONF, subsection='loadtest.in_memory')
        data_store = app.get('DataStore')
        self.assertTrue(data_store.should_load_data)
        self.assertFalse(data_store._data_is_loaded)

        data_store.load_data()
        self.assertTrue(data_store._data_is_loaded)

    def test_setup(self):
        store = InMemoryDBStore()
        expected = Database(users=[], documents=[])
        self.assertEqual(expected, store.db)

    def test_drop(self):
        store = InMemoryDBStore()
        store.db.users.append(make_user_db())
        store.db.documents.append(make_document_db())
        self.assertEqual(1, len(store.db.users))
        self.assertEqual(1, len(store.db.documents))

        store.drop()
        self.assertEqual(0, len(store.db.users))
        self.assertEqual(0, len(store.db.documents))

    def test_load_data(self):
        app = AppStore(config=TEST_CONF, subsection='dev.in_memory')
        store = app.get('DataStore')
        self.assertTrue(isinstance(store, InMemoryDBStore))
        # We have to hack this a bit for the test,
        # because the default is not to load data
        store.should_load_data = True

        self.assertEqual(0, len(store.db.users))
        self.assertEqual(0, len(store.db.documents))
        self.assertIsNone(store.db.app_settings)
        store.load_data()
        self.assertTrue(len(store.db.users) > 0)
        self.assertTrue(len(store.db.documents) > 0)
        self.assertIsNotNone(store.db.app_settings)

    def test_load_data_not_allowed(self):
        app = AppStore(config=TEST_CONF, subsection='dev.in_memory')
        store = app.get('DataStore')
        self.assertTrue(isinstance(store, InMemoryDBStore))
        self.assertFalse(store.should_load_data)

        self.assertEqual(0, len(store.db.users))
        store.load_data()
        self.assertEqual(0, len(store.db.users))

    def test_load_data_without_force(self):
        app = AppStore(config=TEST_CONF, subsection='dev.django')
        store = InMemoryDBStore()
        other_store = DjangoDBStore()
        # We have to hack this a bit for the test,
        # because the default is not to load data
        store.should_load_data = True

        self.assertEqual(0, User.objects.all().count())
        self.assertEqual(0, len(store.db.users))
        store.load_data()
        self.assertEqual(0, len(store.db.users))

        # Calling this will load data into the in-memory store,
        # which is why we have the warnings in the docstring.
        self.assertTrue(User.objects.all().count() > 0)

    def test_load_data_with_force(self):
        app = AppStore(config=TEST_CONF, subsection='dev.django')
        store = InMemoryDBStore()
        # When we use the `force` flag,
        # it loads the corrrect database,
        # although it also destroys the server's app configuration.
        # Once again, heed the warnings!
        self.assertEqual(0, len(store.db.users))
        store.load_data(force=True)
        store = AppStore().get('DataStore')
        self.assertTrue(len(store.db.users) > 0)
