"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from nicegui import app

from common.models.users import UserUI
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

    def set(self, user: UserUI):
        doc_dict = {
            'current_document': None,
            'all_documents': [],
        }

        documents = self.backend_adapter.get_all(user.id)
        for doc in self.frontend_adapter.get_all_minimal(documents, user):
            doc_dict['all_documents'].append(doc.model_dump())

        app.storage.client['documents'] = doc_dict
