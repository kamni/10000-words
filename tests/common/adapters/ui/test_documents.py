"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from unittest import TestCase

from common.adapters.ui.documents import DocumentUIAdapter
from common.adapters.ui.users import UserUIAdapter
from common.models.documents import DocumentDB, DocumentUI, DocumentUIMinimal
from tests.utils.documents import make_document_db
from tests.utils.users import make_user_ui


class TestDocumentUIAdapter(TestCase):
    """
    Tests for common.adapters.ui.documents.DocumentUIAdapter
    """

    def setUp(self):
        self.adapter = DocumentUIAdapter()

    def test_get(self):
        user = make_user_ui()
        docdb = make_document_db(user_id=user.id, language='en')
        expected = DocumentUI(
            id=docdb.id,
            user=user,
            displayName=docdb.display_name,
            language='English',
        )
        returned = self.adapter.get(docdb, user)
        self.assertEqual(expected, returned)

    def test_get_all_minimal(self):
        lang_codes = ('fr', 'es', 'de')
        langs = ('French', 'Spanish', 'German')
        user = make_user_ui()
        docdbs = [
            make_document_db(language_code=lang, user_id=user.id)
            for lang in lang_codes
        ]
        expected = [
            DocumentUIMinimal(
                id=docdb.id,
                user=user,
                displayName=docdb.display_name,
                language=lang,
            ) for docdb, lang in zip(docdbs, langs)
        ]
        returned = self.adapter.get_all_minimal(docdbs, user)
        self.assertEqual(expected, returned)

    def test_get_all_minimal_list_empty(self):
        user = make_user_ui()
        docdbs = []
        expected = docdbs
        returned = self.adapter.get_all_minimal(docdbs, user)
        self.assertEqual(expected, returned)
