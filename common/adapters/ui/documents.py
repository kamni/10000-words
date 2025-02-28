"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import List, Tuple

from ...models.documents import DocumentDB, DocumentUI, SentenceUI
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
        # This should always be the same for all objects
        # that belong to a document.
        # We only store it on the child models for easy filtering.
        language=language_code_choices.get(
            document.language_code,
            'Unknown',
        )

        sentences = [
            SentenceUI(
                id=sentencedb.id,
                language=language,
                ordering=sentencedb.ordering,
                text=sentencedb.text,
                enabledForStudy=sentencedb.enabled_for_study,
                translations=sentencedb.translations,
                displayText=sentencedb.display_text,
            )
            for sentencedb in document.sentences
        ]

        docui = DocumentUI(
            id=document.id,
            user=user,
            displayName=document.display_name,
            language=language,
            attrs=document.attrs,
            sentences=sentences,
        )
        return docui

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
        docuis = [self.get(docdb, user) for docdb in documents]
        return docuis
