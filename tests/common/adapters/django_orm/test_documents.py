"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import shutil
import uuid
from pathlib import Path

from django.test import TestCase

from common.models.documents import DocumentDB
from common.models.errors import ObjectNotFoundError
from common.stores.app import AppStore
from words.models.documents import Document
from tests.utils.users import make_user_db


class TestDocumentDBDjangoORMAdapter(TestCase):
    """
    Tests for common.adapters.django_orm.documents.DocumentDBDjangoORMAdapter
    """

    @classmethod
    def setUpClass(cls):
        AppStore.destroy_all()
        super().setUpClass()

    def setUp(self):
        app = AppStore(subsection='dev.django')
        adapters = app.get('AdapterStore')
        self.adapter = adapters.get('DocumentDBPort')
        self.user_adapter = adapters.get('UserDBPort')

    def tearDown(self):
        AppStore.destroy_all()

    def test_create_or_update_first_creation(self):
        userdb = self.user_adapter.create(make_user_db())
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test create',
            language_code='nl',
        )
        new_docdb = self.adapter.create_or_update(doc)
        self.assertIsNotNone(new_docdb.id)

        docdb = Document.objects.get(id=new_docdb.id)
        self.assertEqual(userdb.id, docdb.user.id)
        self.assertEqual(doc.display_name, docdb.display_name)
        self.assertEqual(doc.language_code, docdb.language_code)

    def test_create_or_update_with_update(self):
        userdb = self.user_adapter.create(make_user_db())
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test create with update',
            language_code='nl',
        )
        docdb1 = self.adapter.create_or_update(doc)
        docdb2 = self.adapter.create_or_update(doc)
        # This shouldn't change anything right now.
        # Later we'll update translations and sentences.
        self.assertEqual(docdb1, docdb2)

    def test_get(self):
        userdb = self.user_adapter.create(make_user_db())
        doc = DocumentDB(
            user_id=userdb.id,
            display_name='Test get',
            language_code='hy',
        )

        expected = self.adapter.create_or_update(doc)
        returned = self.adapter.get(expected.id, userdb.id)
        # Unique on user_id, display_name, and language_code
        self.assertEqual(expected, returned)

    def test_get_does_not_exist(self):
        with self.assertRaises(ObjectNotFoundError):
            self.adapter.get(uuid.uuid4(), uuid.uuid4())

    def test_get_all(self):
        userdb = self.user_adapter.create(make_user_db())
        userdb2 = self.user_adapter.create(make_user_db())
        lang_codes = ['de', 'es', 'fr']

        docs = [
            DocumentDB(
                user_id=userdb.id,
                display_name='Some document',
                language_code=lang,
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

        expected2 = set(filter(lambda x: x.user_id == userdb2.id, docdbs))
        returned2 = set(self.adapter.get_all(userdb2.id))
        self.assertEqual(expected2, returned2)

    def test_get_all_no_documents(self):
        expected = []
        returned = self.adapter.get_all(uuid.uuid4())
        self.assertEqual(expected, returned)
