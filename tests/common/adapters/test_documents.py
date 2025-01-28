"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import random
import uuid
from unittest import TestCase

from common.adapters.documents import DocumentJSONFileAdapter
from common.models.documents import DocumentUIMinimal
from common.models.users import UserDB, UserUI

from ...utils_for_tests.documents import create_document_db
from ...utils_for_tests.users import create_user_db


class TestDocumentJSONFileAdapter(TestCase):
    """
    Tests for common.adapters.documents.DocumentJSONFileAdapter
    """

    @classmethod
    def setUpClass(cls):
        cls.document_adapter = DocumentJSONFileAdapter(
            datadir='tests/data',
            databasefile='database',
        )

    def setUp(self):
        self.document_adapter.read_db(force_reread=True)
        self.document_adapter._database.users = [
            create_user_db() for i in range(2)
        ]

    def tearDown(self):
        self.document_adapter.read_db(force_reread=True)

    def test_read_all_for_user(self):
        user1 = self.document_adapter._database.users[0]
        expected_documents = [
            create_document_db(
                user_id=user1.id,
                language_code='en',
            )
            for i in range(3)
        ]
        expected_documents.extend([
            create_document_db(
                user_id=user1.id,
                language_code='es',
            )
            for i in range(3)
        ])
        self.document_adapter._database.documents.extend(expected_documents)

        user2 = self.document_adapter._database.users[1]
        self.document_adapter._database.documents.extend([
            create_document_db(
                user_id=user2.id,
            )
            for i in range(3)
        ])

        returned_documents = self.document_adapter.get_all(user1.id)
        self.assertEqual(
            set(expected_documents),
            set(returned_documents),
        )

    def test_read_all_for_user_with_language_code(self):
        pass

    def test_invalid_user_returns_empty_list(self):
        pass

    def test_invalid_language_code_returns_empty_list(self):
        pass
