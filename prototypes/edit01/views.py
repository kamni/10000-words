"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path

from common.utils.files import get_project_dir
from frontend.views.edit import EditView
from frontend.widgets.edit import EditWidget
from prototypes.edit01.controllers import DocumentParser


PROJECT_DIR = Path(get_project_dir())
DATA_DIR = PROJECT_DIR/ 'scripts' / 'data' / 'en'


class Edit01View(EditView):
    def set_storage(self):

        doc_dict = {
            'current_document': None,
            'all_documents': [],
        }
        word_dict = {}
        sentence_dict = {}

        for (file, title) in [
            ('Little-Red-Riding-Hood.txt', 'Little Red Riding Hood'),
            #('Rumpelstiltskin.txt', 'Rumpelstiltskin'),
            #('The-Bremen-town-musicians.txt', 'The Bremen Town Musicians'),
         ]:
            parser = DocumentParser((data_dir / file).as_posix(), title)
            database = parser.parse()
            doc_dict['all_documents'].append(database.document.model_dump())

            sentences = {
                'id': sentence_obj.model_dump()
                for id, sentence_obj in database.sentences.items()
            }
            sentence_dict.update(sentences)

            words = {
                'id': word_obj.model_dump()
                for id, word_obj in database.words.items()
            }
            word_dict.update(words)

        app.storage.client['documents'] = doc_dict
        app.storage.client['sentences'] = sentence_dict
        app.storage.client['words'] = word_dict

    def setup(self):
        self.page_content.append(Edit01Widget())


class Edit01Widget(EditWidget):
    pass
