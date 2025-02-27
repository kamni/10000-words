"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path

from django.test import TestCase

from common.adapters.django_orm.data import DataDjangoORMAdapter
from common.models.documents import DocumentDB
from common.models.settings import AppSettingsDB
from common.models.users import UserDB
from common.ports.data import DataExportError, DataLoadError
from common.stores.adapter import AdapterStore
from common.stores.app import AppStore
from common.utils.files import get_project_dir
from words.models.documents import Document


PROJECT_DIR = get_project_dir()
TEST_CONFIG = (PROJECT_DIR / 'tests' / 'setup.cfg').as_posix()
TEST_DATA_DIR = PROJECT_DIR / 'tests' / 'data'


class TestDataDjangoORMAdapter(TestCase):
    """
    Tests for common.adapters.django_orm.data.DataDjangoORMAdapter
    """

    @classmethod
    def setUpClass(cls):
        AppStore.destroy_all()
        super().setUpClass()

    def setUp(self):
        stores = AppStore(config=TEST_CONFIG, subsection='dev.django')
        self.store = stores.get('DataStore')
        self.adapters = AdapterStore()
        self.adapter = self.adapters.get('DataPort')

    def tearDown(cls):
        AppStore.destroy_all()
        (TEST_DATA_DIR / 'deleteme.toml').unlink(missing_ok=True)

    def test_load_from_config(self):
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
        adapter = DataDjangoORMAdapter(
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
        adapter = DataDjangoORMAdapter()
        with self.assertRaises(DataLoadError):
            adapter.load()

    def test_load_data_empty_file(self):
        self.adapter.load(TEST_DATA_DIR / 'blank.toml')

        # We don't need to test documents here,
        # because documents need existing users as a foreign key
        users = self.adapters.get('UserDBPort')
        usersdb = users.get_all()
        self.assertEqual(0, len(usersdb))
        settings = self.adapters.get('AppSettingsDBPort')
        self.assertIsNone(settings.get())

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
        adapter = DataDjangoORMAdapter(datafile=data_file.as_posix())

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
        self.store.drop()
        self.assertEqual([], users.get_all())
        self.assertIsNone(settings.get())
        self.assertEqual(0, Document.objects.all().count())

        adapter2 = DataDjangoORMAdapter(datafile=data_file.as_posix())
        adapter2.load()
        self.assertEqual(settingsdb, settings.get())
        new_usersdb = users.get_all()
        self.assertEqual([userdb], new_usersdb)
        # The UUIDs will have changed on.
        # We need to get the new ones.
        for userdb in new_usersdb:
            new_docdb = DocumentDB(
                user_id=userdb.id,
                display_name='Foo',
                language_code='fr',
            )
            self.assertEqual([new_docdb], documents.get_all(userdb.id))

    def test_export_data_file_specified_at_export(self):
        data_file = TEST_DATA_DIR / 'deleteme.toml'
        data_file.touch()

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

        self.adapter.export(data_file)
        self.store.drop()
        self.assertEqual([], users.get_all())
        self.assertIsNone(settings.get())
        self.assertEqual(0, Document.objects.all().count())

        adapter2 = DataDjangoORMAdapter(datafile=data_file.as_posix())
        adapter2.load()
        self.assertEqual(settingsdb, settings.get())
        new_usersdb = users.get_all()
        self.assertEqual([userdb], new_usersdb)
        # The UUIDs will have changed on.
        # We need to get the new ones.
        for userdb in new_usersdb:
            new_docdb = DocumentDB(
                user_id=userdb.id,
                display_name='Foo',
                language_code='fr',
            )
            self.assertEqual([new_docdb], documents.get_all(userdb.id))

    def test_export_data_file_not_specified(self):
        adapter = DataDjangoORMAdapter()
        with self.assertRaises(DataExportError):
            adapter.export()

    def test_export_data_empty_database(self):
        data_file = TEST_DATA_DIR / 'deleteme.toml'
        adapter = DataDjangoORMAdapter(datafile=data_file.as_posix())
        adapter.export()

        self.store.drop()
        users = self.adapters.get('UserDBPort')
        settings = self.adapters.get('AppSettingsDBPort')

        adapter2 = DataDjangoORMAdapter(datafile=data_file.as_posix())
        adapter2.load()
        self.assertEqual([], users.get_all())
        self.assertIsNone(settings.get())
        self.assertEqual(0, Document.objects.all().count())

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
        self.store.drop()
        self.adapter.load(data_file)

        new_usersdb = users.get_all()
        self.assertEqual([userdb], new_usersdb)
        # The UUIDs will have changed on.
        # We need to get the new ones.
        for userdb in new_usersdb:
            new_docdb = DocumentDB(
                user_id=userdb.id,
                display_name='Foo',
                language_code='fr',
            )
            self.assertEqual([new_docdb], documents.get_all(userdb.id))

    def test_export_data_wrong_file_permissions(self):
        data_file = Path('/root') / 'bad-file.toml'
        with self.assertRaises(DataExportError):
            self.adapter.export(data_file)
