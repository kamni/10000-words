"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import List, Tuple

from ...models.documents import DocumentDB, DocumentUI
from ...models.errors import ObjectNotFoundError
from ...models.users import UserDB
from ...ports.documents import DocumentDBPort
from ...stores.data.in_memory import InMemoryDBStore


class DocumentDBInMemoryAdapter(DocumentDBPort):
    """
    Represents a document in the in-memory store.
    """

    def __init__(self, **kwargs):
        # We ignore the kwargs.
        # This is just there for other ports that might need arguments
        super().__init__()
        self.store = InMemoryDBStore()

    def create_or_update(self, document: DocumentDB) -> DocumentDB:
        """
        Create a document in the database,
        or update it if it already exists.

        :document: Instance of a DocumentDB to save

        :return: DocumentDB that was created/updated
        :raises: ObjectNotFound error if user does not exist.
        """

        existing_doc = None
        try:
            documents = self.store.db.documents[str(document.user_id)]
            if document.id:
                existing_doc = list(filter(
                    lambda x: x.id == document.id,
                    documents,
                ))[0]
            else:
                existing_doc = list(filter(
                    lambda x: (
                        x.display_name == document.display_name
                        and x.language_code == document.language_code
                    ),
                    self.store.db.documents[str(document.user_id)],
                ))[0]
            doc = existing_doc

        except (IndexError, KeyError):
            doc = document
            doc.id = uuid.uuid4()

        if not existing_doc:
            user_id = str(doc.user_id)
            if user_id in self.store.db.documents:
                self.store.db.documents[user_id].append(doc)
            else:
                self.store.db.documents[user_id] = [doc]

        doc.display_name = document.display_name
        if document.binary_data:
            doc.attrs = self.parse_binary_data_attrs(document.binary_data)
        else:
            doc.attrs = document.attrs

        # The binary data does not get stored.
        doc.binary_data = None

        return doc

    def get(self, id: uuid.UUID, user_id: uuid.UUID) -> DocumentDB:
        """
        Get the specified document by id.

        :id: The id of the document
        :user_id: The user's id that owns the document

        :return: DocumentDB matching the id.
        :raises: ObjectNotFoundError if no matching document is found
            for the user
        """

        try:
            docdb = list(filter(
                lambda x: x.id == id and x.user_id == user_id,
                self.store.db.documents[str(user_id)],
            ))[0]
        except (IndexError, KeyError):
            raise ObjectNotFoundError(f'Unable to find document with ID {id}.')

        return docdb

    def get_all(self, user_id: uuid.UUID) -> List[DocumentDB]:
        """
        Get all documents for the specified user.

        :user_id: The user's id who owns the documents

        :return: List of documents (may be empty)
        """

        try:
            docdbs = self.store.db.documents[str(user_id)]
        except KeyError:
            docdbs = []
        return docdbs
