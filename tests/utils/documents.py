"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import string

from common.models.documents import DocumentDB
from common.utils.languages import LanguageCode

from common.models.documents import DocumentDB
from tests.utils.random_data import (
    random_file_path,
    random_language_code,
    random_string,
    random_uuid,
)
from tests.utils.sentences import create_sentence_db_minimal


def create_document_db(**kwargs):
    """
    Create a DocumentDB object.
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
        'sentences': [create_sentence_db_minimal(document_id=doc_id)],
        'translations': [],
    }
    random_data.update(kwargs)

    document = DocumentDB(**random_data)
    return document
