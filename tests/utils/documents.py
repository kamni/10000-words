"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import string

from common.models.documents import DocumentDB, DocumentUI
from common.models.sentences import SentenceDB
from common.stores.adapter import AdapterStore
from tests.utils.random_data import (
    random_language,
    random_language_code,
    random_string,
    random_uuid,
)
from tests.utils.users import create_user_db, make_user_ui


def make_document_db(**kwargs) -> DocumentDB:
    """
    Make a DocumentDB object.
    Not written to database.

    :kwargs: arguments that will be passed to DocumentDB during creation.
    """
    doc_id = kwargs.get('id', random_uuid())
    language_code = kwargs.get('language_code', random_language_code())
    user_id = kwargs.get('user_id', random_uuid())

    sentences = [
        make_sentence_db(
            user_id=user_id,
            document_id=doc_id,
            language_code=language_code,
            ordering=idx + 1,
        )
        for idx in range(3)
    ]

    random_data = {
        'id': doc_id,
        'user_id': user_id,
        'display_name': random_string().title(),
        'language_code': language_code,
        'sentences': sentences,
    }
    random_data.update(kwargs)

    document = DocumentDB(**random_data)
    return document


def make_sentence_db(**kwargs) -> SentenceDB:
    """
    Make a SentenceDB object.
    Not written to database.

    :kwargs: arguments passed to create the SentenceUI
    """
    sentence_id = random_uuid()
    random_data = {
        'id': sentence_id,
        'user_id': random_uuid(),
        'document_id': random_uuid(),
        'ordering': 1,
        'language': random_language,
        'text': random_string(min_size=100, max_size=200),
    }
    random_data.update(kwargs)

    sentence = SentenceDB(**random_data)
    return sentence


def create_document_db(**kwargs) -> DocumentDB:
    """
    Create a DocumentDB in the database.

    :kwargs: arguments to the DocumentDB instance
    """
    if not 'user_id' in kwargs:
        user = create_user_db()
        kwargs['user_id'] = user.id

    adapters = AdapterStore()
    db_adapter = adapters.get('DocumentDBPort')

    docdb = make_document_db(**kwargs)
    new_doc = db_adapter.create_or_update(docdb)
    return new_doc


def make_document_ui(**kwargs) -> DocumentUI:
    """
    Make a DocumentUI object.
    Not written to database.

    :kwargs: arguments for the DocumentUI instance
    """
    language = kwargs.get('language', random_language())

    sentences = [
        make_sentence_ui(ordering=idx + 1, language=language)
        for idx in range(3)
    ]
    random_data = {
        'id': random_uuid(),
        'user': make_user_ui(),
        'displayName': random_string().title(),
        'language': language,
        'sentences': sentences,
    }
    random_data.update(kwargs)

    document = DocumentUI(**random_data)
    return document
