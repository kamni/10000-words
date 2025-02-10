"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from pathlib import Path
from typing import List

from django.contrib.auth.models import User
from django.core.files import File
from django.db.utils import IntegrityError

from words.models import Document

from ...models.documents import DocumentDB
from ...models.errors import ObjectExistsError, ObjectNotFoundError
from ...ports.documents import DocumentDBPort, DocumentUIPort


class DocumentDBDjangoORMAdapter(DocumentDBPort):
    """
    Represents a document in the system
    """

    def create(self, document: DocumentDB) -> DocumentDB:
        """
        Create a document in the database.

        :document: Instance of a DocumentDB to save

        :return: DocumentDB that was created
        :raises: ObjectNotFound error if user does not exist
        :raises: ObjectExistsError when document with the same user
            and file_path exists
        """

        try:
            user = User.objects.get(username=document.user.username)
        except User.DoesNotExist as exc:
            raise ObjectNotFoundError(exc)

        try:
            doc = Document.objects.create(
                user=user,
                display_name=document.display_name,
                language_code=document.language_code,
            )
        except IntegrityError as exc:
            raise ObjectExistsError(exc)

        if document.file_path:
            file_path = Path(document.file_path)
            with file_path.open(mode='rb') as file:
                doc.file = File(file, name=file_path.name)
                doc.save()

    def get(self, id: uuid.UUID, user_id: uuid.UUID) -> DocumentDB:
        """
        Get the specified document by id.

        :id: The id of the document
        :user_id: The user's id that owns the document

        :return: DocumentDB matching the id.
        :raises: ObjectNotFoundError if no matching document is found
            for the user
        """
        pass

    def get_all(self, user_id: uuid.UUID) -> List[DocumentDB]:
        """
        Get all documents for the specified user.

        :user_id: The user's id who owns the documents

        :return: List of documents (may be empty)
        """
        pass
