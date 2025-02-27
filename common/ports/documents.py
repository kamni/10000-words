"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import os
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

from ..models.documents import DocumentDB, DocumentUI
from ..models.files import BinaryFileData
from ..models.users import UserUI


class DocumentDBPort(ABC):
    """
    Represents a document in the system
    """

    @abstractmethod
    def create_or_update(self, document: DocumentDB) -> DocumentDB:
        """
        Create a document in the database,
        or update it if it already exists.

        :document: Instance of a DocumentDB to save

        :return: DocumentDB that was created/updated
        :raises: ObjectNotFound error if user does not exist
        :raises: FileNotFoundError if file doesn't exist.
        """
        pass

    @abstractmethod
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

    @abstractmethod
    def get_all(self, user_id: uuid.UUID) -> List[DocumentDB]:
        """
        Get all documents for the specified user.

        :user_id: The user's id who owns the documents

        :return: List of documents (may be empty)
        """
        pass

    def parse_binary_data_attrs(
        self,
        binary_data: BinaryFileData,
    ) -> Dict[str, str]:
        """
        Parse the data from a binary file into a dict of attributes.

        The attributes must be at the start of the document
        and be delineated with colons on both side of the tag.
        For example:

            :Some Attr: some string value

        :binary_data: The data to parse.
        :return: dictionary of attr-to-values
        """
        attrs = {}
        data = binary_data.data.decode('utf-8')
        text = data.split(os.linesep)
        for line in text:
            line = line.strip()
            if not line.startswith(':'):
                return attrs
            key, value = line.split(':', 2)[1:]
            attrs[key.strip()] = value.strip()
        return attrs


class DocumentUIPort(ABC):
    """
    Represents documents to the UI
    """

    @abstractmethod
    def get(self, document: DocumentDB, user: UserUI) -> DocumentUI:
        """
        Gets a full representation of the document,
        including child sentences and conjugations.

        :document: Database representation of the document.
        :user: UI representation of the user who owns the document.

        :return: Document instance ready for display in the UI.
        """
        pass

    @abstractmethod
    def get_all(
        self,
        documents: List[DocumentDB],
        user: UserUI,
    ) -> List[DocumentUI]:
        """
        Convert a list of database documents into a list of UI objects.

        :documents: DocumentDB instances
        :user: UserUI instances
        :return: List of DocumentUI objects.
        """
        pass
