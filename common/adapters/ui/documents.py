"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import List, Tuple

from ...models.documents import DocumentDB, DocumentUI, DocumentUIMinimal
from ...models.users import UserUI
from ...ports.documents import DocumentUIPort
from ...stores.adapter import AdapterStore
from ...utils.languages import language_code_choices


class DocumentUIAdapter(DocumentUIPort):
    """
    Represents documents to the UI
    """

    def __init__(self, **kwargs):
        # We catch and ignore the kwargs passed,
        # because this doesn't need any more setup.
        super().__init__()

    def get(self, document: DocumentDB, user: UserUI) -> DocumentUI:
        """
        Gets a full representation of the document,
        including child sentences and conjugations.

        :document: UI representation of the document.
        :user: Database representation of the user who owns the document.

        :return: Document instance ready for display in the UI.
        """
        # TODO: complete this when the model is more defined
        docui = DocumentUI(
            id=document.id,
            user=user,
            displayName=document.display_name,
            language=language_code_choices.get(
                document.language_code,
                'Unknown',
            ),
        )
        return docui

    def get_all_minimal(
        self,
        documents: List[DocumentDB],
        user: UserUI,
    ) -> List[DocumentUIMinimal]:
        """
        Convert a list of database documents into a list of minimal UI objects.

        :documents: DocumentDB instances
        :user: UserUI instances
        :return: List of DocumentUIMinimal objects.
        """
        docuis = [
            DocumentUIMinimal(
                id=docdb.id,
                user=user,
                displayName=docdb.display_name,
                language=language_code_choices.get(
                    docdb.language_code,
                    'Unknown',
                ),
            ) for docdb in documents
        ]
        return docuis
