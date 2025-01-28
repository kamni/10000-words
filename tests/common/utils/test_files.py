"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
from unittest import TestCase

from pydantic import BaseModel

from common.models.documents import DocumentBase
from common.utils.files import document_upload_path


class FooUser(BaseModel):
    id: str


class FooDocument(DocumentBase, BaseModel):
    id: str
    user: FooUser
    language_code: str


class TestDocumentUploadPath(TestCase):
    """
    Tests for common.utils.files.document_upload_path
    """

    def test_document_upload_path(self):
        instance = FooDocument(
            id='foo',
            user=FooUser(id='foo'),
            language_code='en',
        )
        filename = 'bar.txt'

        expected_path = os.path.join(
            instance.user.id,
            instance.language_code,
            'docs',
            filename,
        )
        returned_path = document_upload_path(instance, filename)
        self.assertEqual(expected_path, returned_path)

