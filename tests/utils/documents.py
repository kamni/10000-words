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


def make_document_db(**kwargs):
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
