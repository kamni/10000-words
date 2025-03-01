"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from unittest import TestCase

from common.adapters.ui.documents import DocumentUIAdapter
from common.adapters.ui.users import UserUIAdapter
from common.models.documents import DocumentDB, DocumentUI
from common.models.sentences import SentenceUI
from common.utils.languages import language_code_choices
from tests.utils.documents import make_document_db, make_sentence_db
from tests.utils.users import make_user_ui


class TestDocumentUIAdapter(TestCase):
    """
    Tests for common.adapters.ui.documents.DocumentUIAdapter
    """

    def setUp(self):
        self.adapter = DocumentUIAdapter()

    def test_get(self):
        user = make_user_ui()
        docdb = make_document_db(
            user_id=user.id,
            language_code='en',
        )

        expected_sentences = [
            SentenceUI(
                id=sentencedb.id,
                language='English',
                ordering=sentencedb.ordering,
                text=sentencedb.text,
                enabledForStudy=False,
            )
            for sentencedb in docdb.sentences
        ]
        expected = DocumentUI(
            id=docdb.id,
            user=user,
            displayName=docdb.display_name,
            language='English',
            sentences=expected_sentences,
        )
        returned = self.adapter.get(docdb, user)
        self.assertEqual(expected, returned)

    def test_get_with_attributes(self):
        user = make_user_ui()
        docdb = make_document_db(
            user_id=user.id,
            language='sp',
            attrs={
                'título': 'El Enano Saltarín',
                'autor': 'Un cuento de los hermanos Grimm',
            },
            sentences=[],
        )
        expected = DocumentUI(
            id=docdb.id,
            user=user,
            displayName=docdb.display_name,
            language='English',
            sentences=[],
            attrs=docdb.attrs,
        )
        returned = self.adapter.get(docdb, user)
        self.assertEqual(expected, returned)

    def test_get_all(self):
        lang_codes = ('fr', 'es', 'de')
        langs = ('French', 'Spanish', 'German')
        user = make_user_ui()
        docdbs = [
            make_document_db(language_code=lang, user_id=user.id)
            for lang in lang_codes
        ]

        expected_sentences = [
            SentenceUI(
                id=sentencedb.id,
                language=language_code_choices[docdb.language_code],
                ordering=sentencedb.ordering,
                text=sentencedb.text,
                enabledForStudy=False,
            )
            for docdb in docdbs
            for sentencedb in docdb.sentences
        ]
        expected = [
            DocumentUI(
                id=docdb.id,
                user=user,
                displayName=docdb.display_name,
                language=lang,
                sentences=[],
            ) for docdb, lang in zip(docdbs, langs)
        ]
        returned = self.adapter.get_all(docdbs, user)
        self.assertEqual(expected, returned)

    def test_get_all_with_attributes(self):
        lang_codes = ('fr', 'es', 'de')
        langs = ('French', 'Spanish', 'German')
        user = make_user_ui()
        docdbs = [
            make_document_db(
                language_code=lang,
                user_id=user.id,
                attrs={'attr1': 'value1'},
                sentences=[],
            )
            for lang in lang_codes
        ]
        expected = [
            DocumentUI(
                id=docdb.id,
                user=user,
                displayName=docdb.display_name,
                language=lang,
                sentences=[],
                attrs={'attr1': 'value1'},
            ) for docdb, lang in zip(docdbs, langs)
        ]
        returned = self.adapter.get_all(docdbs, user)
        self.assertEqual(expected, returned)

    def test_get_all_list_empty(self):
        user = make_user_ui()
        docdbs = []
        expected = docdbs
        returned = self.adapter.get_all(docdbs, user)
        self.assertEqual(expected, returned)
