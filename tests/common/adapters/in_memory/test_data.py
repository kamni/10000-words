"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
from pathlib import Path
from unittest import TestCase

from common.adapters.in_memory.data import DataInMemoryAdapter
from common.models.database import Database
from common.models.documents import DocumentDB
from common.models.settings import AppSettingsDB
from common.models.users import UserDB
from common.ports.data import DataExportError, DataLoadError
from common.stores.adapter import AdapterStore
from common.stores.app import AppStore
from common.utils.files import get_project_dir


PROJECT_DIR = get_project_dir()
TEST_CONFIG = (PROJECT_DIR / 'tests' / 'setup.cfg').as_posix()
TEST_DATA_DIR = PROJECT_DIR / 'tests' / 'data'


class TestDataInMemoryAdapter(TestCase):
    """
    Tests for common.adapters.in_memory.data.DataInMemoryAdapter
    """

    @classmethod
    def setUpClass(cls):
        AppStore.destroy_all()
        super().setUpClass()

    def setUp(self):
        stores = AppStore(config=TEST_CONFIG, subsection='dev.in_memory')
        self.adapters = AdapterStore()
        self.store = stores.get('DataStore')
        self.adapter = self.adapters.get('DataPort')

    def tearDown(cls):
        AppStore.destroy_all()
        (TEST_DATA_DIR / 'deleteme.toml').unlink(missing_ok=True)

    def test_load_from_config(self):
        blank_db = Database()
        self.assertEqual(blank_db, self.store.db)

        self.adapter.load()
        users = self.adapters.get('UserDBPort')
        usersdb = users.get_all()
        self.assertEqual(3, len(usersdb))
        settings = self.adapters.get('AppSettingsDBPort')
        self.assertIsNotNone(settings.get())
        docs = self.adapters.get('DocumentDBPort')
        for user in usersdb:
            self.assertNotEqual([], docs.get_all(user.id))

    def test_load_data_file_specified_at_init(self):
        adapter = DataInMemoryAdapter(
            datafile=(TEST_DATA_DIR / 'users.toml').as_posix(),
        )
        adapter.load()

        users = self.adapters.get('UserDBPort')
        usersdb = users.get_all()
        self.assertEqual(1, len(usersdb))
        settings = self.adapters.get('AppSettingsDBPort')
        self.assertIsNone(settings.get())
        docs = self.adapters.get('DocumentDBPort')
        for user in usersdb:
            self.assertEqual([], docs.get_all(user.id))

    def test_load_data_file_specified_at_load(self):
        blank_db = Database()
        self.assertEqual(blank_db, self.store.db)

        self.adapter.load(TEST_DATA_DIR / 'users.toml')
        users = self.adapters.get('UserDBPort')
        usersdb = users.get_all()
        self.assertEqual(1, len(usersdb))
        settings = self.adapters.get('AppSettingsDBPort')
        self.assertIsNone(settings.get())
        docs = self.adapters.get('DocumentDBPort')
        for user in usersdb:
            self.assertEqual([], docs.get_all(user.id))

    def test_load_data_file_not_specified(self):
        adapter = DataInMemoryAdapter()
        with self.assertRaises(DataLoadError):
            adapter.load()

    def test_load_data_empty_file(self):
        expected_db = Database()
        self.adapter.load(TEST_DATA_DIR / 'blank.toml')
        returned_db = self.store.db

    def test_load_data_file_does_not_exist(self):
        with self.assertRaises(DataLoadError):
            self.adapter.load(TEST_DATA_DIR / 'not-a-file.toml')

    def test_load_data_invalid_toml_file(self):
        with self.assertRaises(DataLoadError):
            self.adapter.load(TEST_DATA_DIR / 'invalid.toml')

    def test_load_data_invalid_database_object(self):
        with self.assertRaises(DataLoadError):
            self.adapter.load(TEST_DATA_DIR / 'invalid-document.toml')

    def test_load_data_wrong_file_permissions(self):
        data_file = Path('/root') / 'bad-file.toml'
        with self.assertRaises(DataLoadError):
            self.adapter.load(data_file)

    def test_export_data_file_specified_at_init(self):
        data_file = TEST_DATA_DIR / 'deleteme.toml'
        data_file.touch()
        adapter = DataInMemoryAdapter(datafile=data_file.as_posix())

        users = self.adapters.get('UserDBPort')
        userdb = users.create(UserDB(username='foo'))
        settings = self.adapters.get('AppSettingsDBPort')
        settingsdb = settings.create_or_update(AppSettingsDB())
        documents = self.adapters.get('DocumentDBPort')
        docdb = documents.create_or_update(
            DocumentDB(
                user_id=userdb.id,
                display_name='Foo',
                language_code='fr',
            ),
        )

        adapter.export()
        self.store.db = Database()
        self.assertEqual([], self.store.db.users)
        self.assertEqual({}, self.store.db.documents)
        self.assertIsNone(self.store.db.app_settings)

        adapter2 = DataInMemoryAdapter(datafile=data_file.as_posix())
        adapter2.load()
        self.assertEqual([userdb], self.store.db.users)
        self.assertEqual(settingsdb, self.store.db.app_settings)
        self.assertEqual({str(userdb.id): [docdb]}, self.store.db.documents)

    def test_export_data_file_specified_at_export(self):
        data_file = TEST_DATA_DIR / 'deleteme.toml'
        data_file.touch()

        users = self.adapters.get('UserDBPort')
        userdb = users.create(UserDB(username='foo'))
        documents = self.adapters.get('DocumentDBPort')
        docdb = documents.create_or_update(
            DocumentDB(
                user_id=userdb.id,
                display_name='Foo',
                language_code='fr',
            ),
        )

        self.adapter.export(data_file)
        self.store.db = Database()
        self.assertEqual([], self.store.db.users)
        self.assertEqual({}, self.store.db.documents)

        adapter2 = DataInMemoryAdapter(datafile=data_file.as_posix())
        adapter2.load()
        self.assertEqual([userdb], self.store.db.users)
        self.assertEqual({str(userdb.id): [docdb]}, self.store.db.documents)

    def test_export_data_file_not_specified(self):
        adapter = DataInMemoryAdapter()
        with self.assertRaises(DataExportError):
            adapter.export()

    def test_export_data_empty_database(self):
        blank_db = Database()
        data_file = TEST_DATA_DIR / 'deleteme.toml'
        adapter = DataInMemoryAdapter(datafile=data_file.as_posix())

        self.assertEqual(blank_db, self.store.db)
        adapter.export()

        adapter2 = DataInMemoryAdapter(datafile=data_file.as_posix())
        adapter2.load()
        self.assertEqual(blank_db, self.store.db)

    def test_export_data_file_does_not_exist(self):
        data_file = TEST_DATA_DIR / 'deleteme.toml'
        self.assertFalse(data_file.exists())

        users = self.adapters.get('UserDBPort')
        userdb = users.create(UserDB(username='foo'))
        documents = self.adapters.get('DocumentDBPort')
        docdb = documents.create_or_update(
            DocumentDB(
                user_id=userdb.id,
                display_name='Foo',
                language_code='fr',
            ),
        )

        self.adapter.export(data_file)
        self.store.db = Database()
        self.adapter.load(data_file)

        self.assertEqual([userdb], self.store.db.users)
        self.assertEqual({str(userdb.id): [docdb]}, self.store.db.documents)

    def test_export_data_wrong_file_permissions(self):
        data_file = Path('/root') / 'bad-file.toml'
        with self.assertRaises(DataExportError):
            self.adapter.export(data_file)
