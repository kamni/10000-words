"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
import shutil
import uuid
from pathlib import Path
from unittest import TestCase

from common.models.documents import DocumentDB
from common.models.errors import ObjectNotFoundError
from common.models.files import BinaryFileData
from common.stores.app import AppStore
from common.utils.files import get_project_dir
from tests.utils.users import make_user_db


PROJECT_DIR = get_project_dir()
TEST_DATA_DIR = PROJECT_DIR / 'scripts' / 'data' / 'de'


class TestDocumentDBInMemoryAdapter(TestCase):
    """
    Tests for common.adapters.in_memory.documents.DocumentDBInMemoryAdapter
    """

    @classmethod
    def setUpClass(cls):
        AppStore.destroy_all()

    def setUp(self):
        app = AppStore(subsection='dev.in_memory')
        adapters = app.get('AdapterStore')
        self.adapter = adapters.get('DocumentDBPort')
        self.user_adapter = adapters.get('UserDBPort')

    def tearDown(self):
        AppStore.destroy_all()

    def test_create_or_update_first_creation(self):
        filepath = TEST_DATA_DIR / 'Die-Bremer-Stadtmusikanten.txt'
        with filepath.open('rb') as testfile:
            binary_data = BinaryFileData(
                name='Die-Bremer-Stadtmusikanten.txt',
                data=testfile.read(),
            )

        userdb = self.user_adapter.create(make_user_db())
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test create',
            language_code='nl',
            binary_data=binary_data,
        )
        new_docdb = self.adapter.create_or_update(doc)
        self.assertIsNotNone(new_docdb.id)

        docdb = self.adapter.get(id=new_docdb.id, user_id=userdb.id)
        self.assertEqual(userdb.id, docdb.user_id)
        self.assertEqual(doc.display_name, docdb.display_name)
        self.assertEqual(doc.language_code, docdb.language_code)
        self.assertEqual({}, docdb.attrs)

    def test_create_or_update_first_creation_with_attrs(self):
        filepath = TEST_DATA_DIR / 'Rumpelstilzchen.txt'
        with filepath.open('rb') as testfile:
            binary_data = BinaryFileData(
                name='Rumpelstilzchen.txt',
                data=testfile.read(),
            )

        userdb = self.user_adapter.create(make_user_db())
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test create',
            language_code='nl',
            binary_data=binary_data,
        )
        new_docdb = self.adapter.create_or_update(doc)
        self.assertIsNotNone(new_docdb.id)

        docdb = self.adapter.get(id=new_docdb.id, user_id=userdb.id)
        expected_attrs = {
            'Titel': 'Rumpelstilzchen',
            'Autor': 'Ein Märchen der Brüder Grimm',
            'Quelle': (
                'https://www.grimmstories.com/de/grimm_maerchen/'
                'rumpelstilzchen'
            ),
        }
        self.assertEqual(userdb.id, docdb.user_id)
        self.assertEqual(doc.display_name, docdb.display_name)
        self.assertEqual(doc.language_code, docdb.language_code)
        self.assertEqual(expected_attrs, docdb.attrs)

    def test_create_or_update_with_update(self):
        userdb = self.user_adapter.create(make_user_db())
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test create with update',
            language_code='nl',
        )
        docdb1 = self.adapter.create_or_update(doc)
        docdb2 = self.adapter.create_or_update(doc)
        self.assertEqual(docdb1, docdb2)

    def test_create_or_update_with_update_and_binary_data(self):
        userdb = self.user_adapter.create(make_user_db())
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test create with update',
            language_code='nl',
        )
        docdb1 = self.adapter.create_or_update(doc)

        filepath = TEST_DATA_DIR / 'Rumpelstilzchen.txt'
        with filepath.open('rb') as testfile:
            binary_data = BinaryFileData(
                name='Rumpelstilzchen.txt',
                data=testfile.read(),
            )

        doc = DocumentDB(
            id=docdb1.id,
            user_id=userdb.id,
            display_name='Test2 create with update',
            language_code='nl',
            binary_data=binary_data,
        )
        docdb2 = self.adapter.create_or_update(doc)

        expected_attrs = {
            'Titel': 'Rumpelstilzchen',
            'Autor': 'Ein Märchen der Brüder Grimm',
            'Quelle': (
                'https://www.grimmstories.com/de/grimm_maerchen/'
                'rumpelstilzchen'
            ),
        }
        self.assertEqual(userdb.id, docdb2.user_id)
        self.assertEqual(docdb1.id, docdb2.id)
        self.assertEqual(doc.display_name, docdb2.display_name)
        self.assertEqual(doc.language_code, docdb2.language_code)
        self.assertEqual(expected_attrs, docdb2.attrs)

    def test_create_or_update_with_update_and_new_attrs(self):
        userdb = self.user_adapter.create(make_user_db())
        expected_attrs = {'foo': 'bar'}
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test create with update and attrs',
            language_code='nl',
            attrs=expected_attrs,
        )
        docdb1 = self.adapter.create_or_update(doc)
        self.assertEqual(expected_attrs, docdb1.attrs)

        expected_attrs = {'bar': 'foo'}
        doc = DocumentDB(
            id=docdb1.id,
            user_id=userdb.id,
            display_name='Test create with update and attrs',
            language_code='nl',
            attrs=expected_attrs,
        )
        docdb2 = self.adapter.create_or_update(doc)
        self.assertEqual(docdb2.id, docdb1.id)
        self.assertEqual(expected_attrs, docdb2.attrs)

    def test_get(self):
        userdb = self.user_adapter.create(make_user_db())
        expected_attrs = {'foo': 'bar'}
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test get',
            language_code='hy',
            attrs=expected_attrs,
        )

        expected = self.adapter.create_or_update(doc)
        returned = self.adapter.get(expected.id, userdb.id)
        # Unique on user_id, display_name, and language_code
        self.assertEqual(expected, returned)
        self.assertEqual(expected_attrs, returned.attrs)

    def test_get_does_not_exist(self):
        with self.assertRaises(ObjectNotFoundError):
            self.adapter.get(uuid.uuid4(), uuid.uuid4())

    def test_get_all(self):
        userdb = self.user_adapter.create(make_user_db())
        userdb2 = self.user_adapter.create(make_user_db())
        lang_codes = ['de', 'es', 'fr']

        expected_attrs={'bar': 'foo'}
        docs = [
            DocumentDB(
                user_id=userdb.id,
                display_name='Some document',
                language_code=lang,
                attrs=expected_attrs,
            ) for lang in lang_codes
        ]
        docs2 = [
            DocumentDB(
                user_id=userdb2.id,
                display_name='Some document',
                language_code=lang,
            ) for lang in lang_codes
        ]
        docdbs = [self.adapter.create_or_update(doc) for doc in docs + docs2]

        expected1 = set(filter(lambda x: x.user_id == userdb.id, docdbs))
        returned1 = set(self.adapter.get_all(userdb.id))
        self.assertEqual(expected1, returned1)
        for doc in returned1:
            self.assertEqual(expected_attrs, doc.attrs)

        expected2 = set(filter(lambda x: x.user_id == userdb2.id, docdbs))
        returned2 = set(self.adapter.get_all(userdb2.id))
        self.assertEqual(expected2, returned2)
        for doc in returned2:
            self.assertEqual({}, doc.attrs)

    def test_get_all_no_documents(self):
        expected = []
        returned = self.adapter.get_all(uuid.uuid4())
        self.assertEqual(expected, returned)
