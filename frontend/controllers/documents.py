"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Any, Dict, List

from nicegui import app

from common.models.documents import DocumentDB, DocumentUI
from common.models.files import BinaryFileData
from common.models.users import UserUI
from common.utils.languages import language_name_to_code
from frontend.controllers.base import BaseController


class DocumentController(BaseController):
    """
    Control document state in the application.
    """

    @property
    def backend_adapter(self):
        if not self._backend_adapter:
            self._backend_adapter = self.adapters.get('DocumentDBPort')
        return self._backend_adapter

    @property
    def frontend_adapter(self):
        if not self._frontend_adapter:
            self._frontend_adapter = self.adapters.get('DocumentUIPort')
        return self._frontend_adapter

    def create(self, document_dict: Dict[str, Any]):
        user = document_dict['user']
        document = DocumentDB(
            user_id=user.id,
            display_name=document_dict['display_name'],
            language_code=language_name_to_code[document_dict['language']],
            binary_data=BinaryFileData(
                name=document_dict['upload'].name,
                data=document_dict['upload'].content.read(),
            ),
        )
        new_doc = self.backend_adapter.create_or_update(document)

        doc_ui = self.frontend_adapter.get(new_doc, user)
        app.storage.client['documents']['all_documents'].append(
            doc_ui.model_dump(),
        )
        self.set_current_document(doc_ui)

    def get_all(self) -> List[DocumentUI]:
        doc_dicts = app.storage.client['documents']['all_documents']
        docs = [DocumentUI(**doc) for doc in doc_dicts]
        return docs

    def get_current_document(self) -> DocumentUI:
        document_dict = app.storage.client['documents']['current_document']
        if document_dict is not None:
            document = DocumentUI(**document_dict)
            return document
        return None

    def set(self, user):
        doc_dict = {
            'current_document': None,
            'all_documents': [],
        }

        if user:
            documents = self.backend_adapter.get_all(user.id)
            for doc in self.frontend_adapter.get_all(documents, user):
                doc_dict['all_documents'].append(doc.model_dump())

        app.storage.client['documents'] = doc_dict

    def set_current_document(self, document: DocumentUI):
        # TODO: fetch sentence data
        # TODO: update sentences, words
        app.storage.client['documents']['current_document'] = document.model_dump()

