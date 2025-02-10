"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import List

from ...models.documents import DocumentDB, DocumentUI, DocumentUIMinimal
from ...ports.documents import DocumentUIPort


class DocumentUIAdapter(DocumentUIPort):
    """
    Represents documents to the UI
    """

    def get(self, document: DocumentDB) -> DocumentUI:
        """
        Gets a full representation of the document,
        including child sentences and conjugations.

        :document: Database representation of the document.

        :return: Document instance ready for display in the UI.
        """
        pass

    def get_all_minimal(
        self,
        documents: List[DocumentDB],
    ) -> List[DocumentUIMinimal]:
        """
        Convert a list of database documents into a list of minimal UI objects.

        :documents: DocumentDB instances.
        :return: List of DocumentUIMinimal objects.
        """
        pass
