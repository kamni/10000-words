"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import string

from common.models.documents import DocumentDB, DocumentUI
from common.stores.adapter import AdapterStore
from tests.utils.random_data import (
    random_file_path,
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

    doc_id = random_uuid()
    random_data = {
        'id': doc_id,
        'user_id': random_uuid(),
        'display_name': random_string().title(),
        'language_code': random_language_code(),
        'doc_file': random_file_path(),
        'translations': [],
    }
    random_data.update(kwargs)

    document = DocumentDB(**random_data)
    return document


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

    :kwargs: arguments
    """
    random_data = {
        'id': random_uuid(),
        'user': make_user_ui(),
        'displayName': random_string().title(),
        'language': random_language(),
        'sentences': [],
    }
    random_data.update(kwargs)

    document = DocumentUI(**random_data)
    return document
