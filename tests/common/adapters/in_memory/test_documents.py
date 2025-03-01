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
from tests.utils.documents import make_sentence_db
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

    def test_create_or_update_binary_create_and_binary_update(self):
        # Creation from a binary file
        filepath = TEST_DATA_DIR / 'Die-Bremer-Stadtmusikanten.txt'
        with filepath.open('rb') as testfile:
            binary_data = BinaryFileData(
                name='Die-Bremer-Stadtmusikanten.txt',
                data=testfile.read(),
            )

        userdb = self.user_adapter.create(make_user_db())
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test create binary-to-binary',
            language_code='de',
            binary_data=binary_data,
        )
        new_docdb = self.adapter.create_or_update(doc)
        self.assertIsNotNone(new_docdb.id)

        self.assertEqual(userdb.id, new_docdb.user_id)
        self.assertEqual(doc.display_name, new_docdb.display_name)
        self.assertEqual(doc.language_code, new_docdb.language_code)
        self.assertEqual(54, len(new_docdb.sentences))
        self.assertEqual({}, new_docdb.attrs)

        # Update from a binary file
        # We can't update this attribute:
        bad_language_code = 'es'
        # These attributes can be updated:
        good_display_name = 'Test update binary-to-binary'
        filepath = TEST_DATA_DIR / 'Rumpelstilzchen.txt'
        with filepath.open('rb') as testfile:
            good_binary_data = BinaryFileData(
                name='Rumpelstilzchen.txt',
                data=testfile.read(),
            )
        expected_attrs = {
            'Titel': 'Rumpelstilzchen',
            'Autor': 'Ein Märchen der Brüder Grimm',
            'Quelle': (
                'https://www.grimmstories.com/de/grimm_maerchen/rumpelstilzchen'
            ),
        }

        doc = DocumentDB(
            id=new_docdb.id,
            user_id=userdb.id,
            display_name=good_display_name,
            language_code=bad_language_code,
            binary_data=good_binary_data,
        )
        new_docdb2 = self.adapter.create_or_update(doc)

        self.assertEqual(new_docdb.id, new_docdb2.id)
        self.assertEqual(new_docdb.user_id, new_docdb2.user_id)
        self.assertEqual(good_display_name, new_docdb2.display_name)
        self.assertEqual(new_docdb.language_code, new_docdb2.language_code)
        self.assertEqual(expected_attrs, new_docdb2.attrs)
        self.assertEqual(48, len(new_docdb2.sentences))

    def test_create_or_update_binary_create_and_sentences_update(self):
        filepath = TEST_DATA_DIR / 'Rumpelstilzchen.txt'
        with filepath.open('rb') as testfile:
            binary_data = BinaryFileData(
                name='Rumpelstilzchen.txt',
                data=testfile.read(),
            )
        expected_attrs = {
            'Titel': 'Rumpelstilzchen',
            'Autor': 'Ein Märchen der Brüder Grimm',
            'Quelle': (
                'https://www.grimmstories.com/de/grimm_maerchen/rumpelstilzchen'
            ),
        }

        userdb = self.user_adapter.create(make_user_db())
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test create binary-to-sentences',
            language_code='de',
            binary_data=binary_data,
        )
        new_docdb = self.adapter.create_or_update(doc)
        self.assertEqual(expected_attrs, new_docdb.attrs)
        # This shouldn't be stored
        self.assertIsNone(new_docdb.binary_data)

        # These attributes can be updated:
        new_display_name = 'Test update binary-to-sentences'
        new_attrs = {'foo': 'bar'}
        new_sentences = [
            make_sentence_db(
                user_id=userdb.id,
                document_id=new_docdb.id,
                language_code=new_docdb.language_code,
            ),
        ]

        doc = DocumentDB(
            id=new_docdb.id,
            user_id=userdb.id,
            language_code=new_docdb.language_code,
            display_name=new_display_name,
            attrs=new_attrs,
            sentences=new_sentences,
        )
        new_docdb2 = self.adapter.create_or_update(doc)

        self.assertEqual(new_docdb.id, new_docdb2.id)
        self.assertEqual(new_docdb.user_id, new_docdb2.user_id)
        self.assertEqual(new_display_name, new_docdb2.display_name)
        self.assertEqual(new_docdb.language_code, new_docdb2.language_code)
        self.assertEqual(new_attrs, new_docdb2.attrs)
        self.assertEqual(new_sentences, new_docdb2.sentences)

    def test_create_or_update_sentences_create_and_binary_update(self):
        userdb = self.user_adapter.create(make_user_db())
        sentences = [make_sentence_db()]
        attrs = {'foo': 'bar'}
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test create sentences-to-binary',
            language_code='de',
            attrs=attrs,
            sentences=sentences,
        )
        new_docdb = self.adapter.create_or_update(doc)

        self.assertIsNotNone(doc.id)
        self.assertEqual(1, len(new_docdb.sentences))
        self.assertIsNotNone(new_docdb.sentences[0].id)
        self.assertEqual(userdb.id, new_docdb.sentences[0].user_id)
        self.assertEqual(new_docdb.id, new_docdb.sentences[0].document_id)
        self.assertEqual(attrs, new_docdb.attrs)

        filepath = TEST_DATA_DIR / 'Die-Bremer-Stadtmusikanten.txt'
        with filepath.open('rb') as testfile:
            binary_data = BinaryFileData(
                name='Die-Bremer-Stadtmusikanten.txt',
                data=testfile.read(),
            )
        new_display_name = 'Test update sentences-to-binary'
        doc = DocumentDB(
            id=new_docdb.id,
            user_id=userdb.id,
            display_name=new_display_name,
            language_code='de',
            binary_data=binary_data,
            attrs={'msg': 'This is ignored when binary data is present'},
        )
        new_docdb2 = self.adapter.create_or_update(doc)

        self.assertEqual(new_docdb.id, new_docdb2.id)
        self.assertEqual(new_display_name, new_docdb2.display_name)
        self.assertEqual({}, new_docdb.attrs)
        self.assertEqual(54, len(new_docdb.sentences))
        self.assertIsNone(new_docdb.binary_data)

    def test_create_or_update_sentences_create_and_sentence_update(self):
        userdb = self.user_adapter.create(make_user_db())
        sentences = [make_sentence_db()]
        attrs = {'foo': 'bar'}
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test create sentences-to-sentences',
            language_code='de',
            attrs=attrs,
            sentences=sentences,
        )
        new_docdb = self.adapter.create_or_update(doc)

        self.assertIsNotNone(doc.id)
        self.assertEqual(1, len(new_docdb.sentences))
        self.assertEqual(attrs, new_docdb.attrs)

        new_sentences = [make_sentence_db() for i in range(3)]
        new_attrs = {'bar': 'foo'}
        new_display_name = 'Test update sentences-to-sentences'
        doc = DocumentDB(
            id=new_docdb.id,
            user_id=userdb.id,
            display_name=new_display_name,
            language_code='de',
            attrs=new_attrs,
            sentences=new_sentences,
        )
        new_docdb2 = self.adapter.create_or_update(doc)

        self.assertEqual(new_docdb.id, new_docdb2.id)
        self.assertEqual(new_display_name, new_docdb2.display_name)
        self.assertEqual(new_attrs, new_docdb2.attrs)
        self.assertEqual(3, len(new_docdb.sentences))

    def test_create_or_update_document_with_id_missing(self):
        userdb = self.user_adapter.create(make_user_db())
        doc = DocumentDB(
            id=uuid.uuid4(),
            user_id=userdb.id,
            display_name='Test create sentences-to-sentences',
            language_code='de',
        )
        with self.assertRaises(ObjectNotFoundError):
            self.adapter.create_or_update(doc)

    def test_get(self):
        userdb = self.user_adapter.create(make_user_db())
        expected_attrs = {'foo': 'bar'}
        expected_sentences = [make_sentence_db(
            user_id=userdb.id,
            language_code='hy',
        )]
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test get',
            language_code='hy',
            attrs=expected_attrs,
            sentences=expected_sentences,
        )

        expected = self.adapter.create_or_update(doc)
        returned = self.adapter.get(expected.id, userdb.id)
        # Unique on user_id, display_name, and language_code
        self.assertEqual(expected, returned)
        self.assertEqual(expected_attrs, returned.attrs)
        self.assertEqual(expected_sentences, returned.sentences)

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
                sentences=[
                    make_sentence_db(
                        user_id=userdb.id,
                        language_code=lang,
                    )
                    for i in range(2)
                ]
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
            self.assertEqual(2, len(doc.sentences))

        expected2 = set(filter(lambda x: x.user_id == userdb2.id, docdbs))
        returned2 = set(self.adapter.get_all(userdb2.id))
        self.assertEqual(expected2, returned2)
        for doc in returned2:
            self.assertEqual({}, doc.attrs)

    def test_get_all_no_documents(self):
        expected = []
        returned = self.adapter.get_all(uuid.uuid4())
        self.assertEqual(expected, returned)
