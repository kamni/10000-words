"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from pathlib import Path
from typing import List

from django.core.files import File
from django.db.utils import IntegrityError

from users.models import UserProfile
from words.models import Document

from ...models.documents import DocumentDB
from ...models.errors import ObjectNotFoundError
from ...ports.documents import DocumentDBPort, DocumentUIPort


class DocumentDBDjangoORMAdapter(DocumentDBPort):
    """
    Represents a document in the system
    """

    def __init__(self, **kwargs):
        # Ignore kwargs, as they're not needed
        super().__init__()

    def _django_to_pydantic(self, document: Document) -> DocumentDB:
        docdb = DocumentDB(
            id=document.id,
            user_id=document.user.id,
            display_name=document.display_name,
            language_code=document.language_code,
        )
        return docdb

    def create_or_update(self, document: DocumentDB) -> DocumentDB:
        """
        Create a document in the database,
        or update it if it already exists.

        :document: Instance of a DocumentDB to save

        :return: DocumentDB that was created/updated
        :raises: ObjectNotFound error if user does not exist
        """

        # This raises an ObjectNotFound error.
        # We won't trap it in a try-except block.
        user = UserProfile.objects.get(id=document.user_id)

        existing_doc = Document.objects.filter(
            user__id=document.user_id,
            display_name=document.display_name,
            language_code=document.language_code,
        ).first()

        if existing_doc:
            # Currently, nothing so we won't do anything here.
            # TODO: a direct `update` function that changes display_name
            doc = existing_doc
        else:
            doc = Document.objects.create(
                user=user,
                display_name=document.display_name,
                language_code=document.language_code,
            )

        # TODO: handle translations
        # TODO: handle new sentence uploads

        docdb = self._django_to_pydantic(doc)
        return docdb

    def get(self, id: uuid.UUID, user_id: uuid.UUID) -> DocumentDB:
        """
        Get the specified document by id.
        Both the id and user id are supplied
        to make sure we don't return a document that the user doesn't own.

        :id: The id of the document
        :user_id: The user's id that owns the document

        :return: DocumentDB matching the id.
        :raises: ObjectNotFoundError if no matching document is found
            for the user
        """

        try:
            doc = Document.objects.get(id=id, user__id=user_id)
        except Document.DoesNotExist as exc:
            raise ObjectNotFoundError(exc)

        docdb = self._django_to_pydantic(doc)
        return docdb

    def get_all(self, user_id: uuid.UUID) -> List[DocumentDB]:
        """
        Get all documents for the specified user.

        :user_id: The user's id who owns the documents

        :return: List of documents (may be empty)
        """
        docs = Document.objects.filter(user__id=user_id).all()
        docdbs = [self._django_to_pydantic(doc) for doc in docs]
        return docdbs

