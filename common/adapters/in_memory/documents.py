"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import List, Tuple

from ...models.documents import DocumentDB, DocumentUI, DocumentUIMinimal
from ...models.errors import ObjectNotFoundError
from ...models.users import UserDB
from ...ports.documents import DocumentDBPort
from ...stores.data.in_memory import InMemoryDBStore
from ...utils.files import (
    document_upload_path,
    get_project_dir,
    get_upload_dir,
)


class DocumentDBInMemoryAdapter(DocumentDBPort):
    """
    Represents a document in the in-memory store.
    """

    def __init__(self, **kwargs):
        # We ignore the kwargs.
        # This is just there for other ports that might need arguments
        super().__init__()
        self.store = InMemoryDBStore(subsection='dev.in_memory')

    def create_or_update(self, document: DocumentDB) -> DocumentDB:
        """
        Create a document in the database,
        or update it if it already exists.

        :document: Instance of a DocumentDB to save

        :return: DocumentDB that was created/updated
        :raises: ObjectNotFound error if user does not exist.
        :raises: FileNotFoundError if file doesn't exist.
        """

        existing_doc = None
        try:
            existing_doc = list(filter(
                lambda x: (
                    x.user_id == document.user_id
                    and x.display_name == document.display_name
                    and x.language_code == document.language_code
                ),
                self.store.db.documents,
            ))[0]
            doc = existing_doc
        except IndexError:
            doc = document
            doc.id = uuid.uuid4()

        if document.file_path:
            if document.file_path.startswith('/'):
                doc_path = Path(document.file_path).resolve()
            else:
                doc_path = Path(get_project_dir()).resolve() / document.file_path

            if not doc_path.is_file():
                raise FileNotFoundError(
                    f'The file {document.file_path} does not exist.',
                )

            # 'Upload' the file
            filename = doc_path.as_posix().rsplit(os.sep, 1)[1]
            upload_relative_path = document_upload_path(doc, filename)
            upload_path = os.sep.join([get_upload_dir(), upload_relative_path])
            upload_path_dir = upload_path.rsplit(os.sep, 1)[0]
            Path(upload_path_dir).mkdir(parents=True, exist_ok=True)

            if doc_path.as_posix() != upload_path:
                shutil.copy(doc_path, upload_path)
            doc.file_path = upload_path

        if not existing_doc:
            self.store.db.documents.append(doc)

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
                self.store.db.documents,
            ))[0]
        except IndexError:
            raise ObjectNotFoundError(f'Unable to find document with ID {id}.')

        return docdb

    def get_all(self, user_id: uuid.UUID) -> List[DocumentDB]:
        """
        Get all documents for the specified user.

        :user_id: The user's id who owns the documents

        :return: List of documents (may be empty)
        """

        docdbs = list(filter(
            lambda x: x.user_id == user_id,
            self.store.db.documents,
        ))
        return docdbs
