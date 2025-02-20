"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from nicegui import app

from frontend.views.base import BaseView

from ..widgets.edit import EditWidget


class EditView(BaseView):
    """
    Add and edit text to practice with
    """

    def set_store(self):
        """
        Set data needed by the widgets.
        This will be available to all widgets.
        """
        document_db = self.adapters.get('DocumentDBPort')
        document_ui = self.adapters.get('DocumentUIPort')
        doc_dict = {
            'current_document': None,
            'all_documents': [],
        }

        documents = document_db.get_all(self.user.id)
        for doc in document_ui.get_all_minimal(documents, self.user):
            doc_dict['all_documents'].append(doc.model_dump())

        app.storage.client['documents'] = doc_dict

    def setup(self):
        self.page_content.append(EditWidget())
