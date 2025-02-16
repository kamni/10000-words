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

    '''
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
    '''

    # Temporary for prototyping purposes
    def set_store(self):
        from pathlib import Path
        from common.utils.files import get_project_dir
        from scripts.prototype_deleteme import DocumentParser

        doc_dict = {
            'current_document': None,
            'all_documents': [],
        }
        word_dict = {}

        project_dir = Path(get_project_dir())
        data_dir = project_dir / 'scripts' / 'data' / 'en'
        for (file, title) in [
            ('Little-Red-Riding-Hood.txt', 'Little Red Riding Hood'),
            #('Rumpelstiltskin.txt', 'Rumpelstiltskin'),
            #('The-Bremen-town-musicians.txt', 'The Bremen Town Musicians'),
         ]:
            parser = DocumentParser((data_dir / file).as_posix(), title)
            database = parser.parse()
            doc_dict['all_documents'].append(database.document.model_dump())

            words = {
                word: word_obj.model_dump()
                for word, word_obj in database.words.items()
            }
            word_dict.update(words)

        app.storage.client['documents'] = doc_dict
        app.storage.client['words'] = word_dict

    def setup(self):
        self.page_content.append(EditWidget())
