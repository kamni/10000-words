"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path
from typing import List

from nicegui import ElementFilter, app, events, ui
from nicegui.elements.label import Label

from common.models.documents import DocumentDB, DocumentUI
from common.models.files import BinaryFileData
from common.stores.adapter import AdapterStore
from common.utils.files import get_project_dir
from common.utils.languages import language_choices
from frontend.views.edit import EditView
from frontend.widgets.base import BaseWidget
from frontend.widgets.edit import EditWidget
from prototypes.edit01.controllers import (
    EditViewController,
    EditComponentController,
)
from prototypes.edit01.models import Document, Sentence, WordStatus


PROJECT_DIR = get_project_dir()
DATA_DIR = PROJECT_DIR/ 'scripts' / 'data' / 'en'


class Edit01View(EditView):
    @property
    def controller(self):
        if not hasattr(self, '_controller') or self._controller is None:
            self._controller = EditViewController()
        return self._controller

    def set_store(self):
        # TODO: rename to set_storage()
        app.storage.client['documents'] = self.controller.get_documents()
        app.storage.client['sentences'] = self.controller.get_sentences()
        app.storage.client['words'] = self.controller.get_words()

    def setup(self):
        self.page_content.append(Edit01Widget())


class EditComponent(BaseWidget):
    """
    Useful properties for all parts of the EditWidget
    """
    @property
    def controller(self):
        if not hasattr(self, '_controller') or self._controller is None:
            self._controller = EditComponentController()
        return self._controller

    @property
    def current_document(self) -> Document:
        return self.controller.get_current_document(
            app.storage.client['documents']['current_document'],
        )

    @current_document.setter
    def current_document(self, doc: Document):
        app.storage.client['documents']['current_document'] = \
                self.controller.get_current_document_dict(doc)

    @property
    def documents(self) -> List[Document]:
        return self.controller.get_documents(
            app.storage.client['documents']['all_documents'],
        )


class DisplayTextLabel(Label):
    """
    Displays an individual word's display text.
    """

    def __init__(self, display_text_obj, sentence_obj):
        # TODO: can we do a hover that shows the word?
        self.display_text = display_text_obj
        self.sentence = sentence_obj
        self.word = display_text_obj.word

        super().__init__(text=self.display_text.text)

    def get_marker(self):
        return str(self.word.id)


class EditArea(EditComponent):
    """
    Area for editing documents
    """

    CSS = '''
        .text-gap {
            gap: 0 !important;
        }
    '''

    def get_status_classes(self, status: str):
        # TODO: make this SASS and add SASS to class
        return {
            WordStatus.not_set: ' bg-zinc-400 text-zinc-950',
            WordStatus.ignored: ' bg-zinc-50 text-zinc-950',
            WordStatus.to_learn: ' bg-violet-300 text-zinc-950',
            WordStatus.learning: ' bg-emerald-300 text-zinc-950',
            WordStatus.learned: ' bg-zinc-50 text-zinc-950',
        }[status]

    def context_menu(self, element):
        not_set = self.get_status_classes(WordStatus.not_set)
        ignored = self.get_status_classes(WordStatus.ignored)
        to_learn = self.get_status_classes(WordStatus.to_learn)
        learning = self.get_status_classes(WordStatus.learning)
        learned = self.get_status_classes(WordStatus.learned)

        with ui.context_menu().classes('bg-dark text-zinc-50'):
            ui.label('Set Status:').classes('p-2 text-center')
            ui.separator()

            ui.menu_item(
                'Ignored',
                lambda: self.set_word_status(element, WordStatus.ignored),
            ).classes(ignored)
            ui.menu_item(
                'To Learn',
                lambda: self.set_word_status(element, WordStatus.to_learn),
            ).classes(to_learn)
            ui.menu_item(
                'Learning',
                lambda: self.set_word_status(element, WordStatus.learning),
            ).classes(learning)
            ui.menu_item(
                'Learned',
                lambda: self.set_word_status(element, WordStatus.learned),
            ).classes(learned)

            # TODO: handle combining
            # TODO: add option to change base word
            '''
            ui.separator()
            ui.label('Multi-Word Actions:').classes('p-2 text-center')
            ui.separator()
            ui.menu_item('Combine Words', self.combine_words) \
                    .classes('bg-amber-400 text-zinc=950')
            '''

    def set_word_status(self, element, status):
        self.controller.set_word_status(element.word.id, status, app.storage.client)
        # TODO: we should probably re-load storage

        marker = element.get_marker()
        current_classes = self.get_status_classes(element.word.status)
        new_classes = self.get_status_classes(status)
        for elem in ElementFilter(marker=marker):
            elem.classes(remove='outline' + current_classes)
            elem.classes(add=new_classes)

    '''
    def clear_collected_words(self):
        # TODO: this should be handled by a sentence class
        for word_label in self._collected_words:
            word_label.classes(remove='!bg-amber-400')
        self._collected_words = []

    def combine_words(self):
        if not hasattr(self, '_collected_words') or not self._collected_words:
            ui.notify('No words to combine')
            return

        is_same_sentence = len(list(set([
            word_label.sentence['id'] for word_label in self._collected_words
        ]))) == 1
        if not is_same_sentence:
            ui.notify('You can only combine words in the same sentence')
            self.clear_collected_words()
            return

        new_word_text = ' '.join([
            word_label.display_text['text'].lower()
            for word_label in self._collected_words
        ])
        sentence = self._collected_words[0].sentence
        sentence_id = str(sentence['id'])

        existing_word = list(filter(
            lambda x: x['case_insensitive_text'] == new_word_text,
            app.storage.client['words'].values(),
        ))
        # TODO: pop up a modal to edit word, taking into account existing word,
        # *before*  we write to either storage or backend
        if existing_word:
            existing_word[0]['sentences'].append(
                app.storage.client['sentences'][sentence_id],
            )
            new_word = existing_word
        else:
            # TODO: we'll write to the database and get a UUID
            import uuid
            new_word = {
                'id': uuid.uuid4(),
                'case_insensitive_text': new_word_text,
                'status': WordStatus.not_set,
                'sentences': [sentence],
            }
            app.storage.client['words'][new_word['id']] = new_word

        def words_are_sequential():
            last_num_seen = None
            for word_label in self._collected_words:
                ordering = word_label.display_text['ordering']
                if last_num_seen is None:
                    last_num_seen = ordering
                    continue
                if (ordering - last_num_seen) != 1:
                    return False
            return True

        self._collected_words.sort(key=lambda x: x.display_text['ordering'])
        # TODO: remove `and False`: this is just until we implement the merge
        if words_are_sequential() and False:
            # TODO: combine the visual representation
            # TODO: update the whole document?
            pass
        else:
            for word_label in self._collected_words:
                word_label.word = new_word
                self.set_word_status(word_label, new_word['status'])
                word_label._markers = [new_word['id']]
                word_label.classes(add='outline')

        self.clear_collected_words()

    def collect_words(self, event: events.GenericEventArguments):
        element = event.sender
        if not hasattr(self, '_collected_words'):
            self._collected_words = []

        if element in self._collected_words:
            self._collected_words.pop(self._collected_words.index(element))
            element.classes(remove='!bg-amber-400')
        else:
            self._collected_words.append(element)
            element.classes(add='!bg-amber-400')
    '''

    def display_sentence(self, sentence):
        with ui.row().classes('text-gap'):
            for display_text in sentence.word_display_text:
                with DisplayTextLabel(display_text, sentence) as dl:
                    dl.mark(f'{dl.get_marker()}')
                    classes = self.get_status_classes(dl.word.status)
                    dl.classes(
                        'cursor-pointer text-lg px-2 py-2 rounded-lg' + classes
                    )
                    # TODO: combine word changes
                    #dl.on('click', self.collect_words)
                    self.context_menu(dl)

    def show_content(self):
        documents = self.documents
        if not documents:
            ui.label('Welcome to 10,000 Words!').classes('text-2xl')
            with ui.row():
                ui.label('''
                    To get started, upload a document using the 'Upload' button.
                ''').classes('text-xl')
                ui.icon('arrow_forward').classes('text-2xl')
            return

        document = self.current_document
        if document:
            ui.label(document.displayName).classes('text-3xl bold text-blue-950')
            for sentence in document.sentences:
                self.display_sentence(sentence)
        else:
            with ui.row():
                ui.icon('arrow_back').classes('text-2xl')
                ui.label('''
                    Choose an uploaded document to set up your vocabulary lessons.
                ''').classes('text-xl')

    def display(self):
        with ui.card().classes('h-screen !w-2/3'):
            with ui.scroll_area().classes('size-full'):
                self.show_content()


@ui.refreshable
def edit_area():
    EditArea().display()


class DocumentSidebar(EditComponent):
    """
    Sidebar that lists all uploaded documents.
    """

    # Overriding some baked-in styles
    CSS = '''
        .uploads {
            width: 315px !important;
        }
        .uploads .q-scrollarea__content {
            padding: 0 !important;
        }
        .upload-drawer button span {
            text-align: left !important;
        }
    '''

    @property
    def documents_by_language(self):
        by_language = {}
        for doc in self.documents:
            if doc.language in by_language:
                by_language[doc.language].append(doc)
            else:
                by_language[doc.language] = [doc]
        return by_language

    def show_document(self, doc_id):
        def _on_click():
            # TODO: we'll have to fetch full doc from server
            doc = list(filter(lambda x: x.id == doc_id, self.documents))[0]
            self.current_document = doc
            edit_area.refresh()
            upload_sidebar.refresh()
        return _on_click

    def display(self):
        with ui.card().classes('h-screen uploads'):
            ui.label('Uploads').classes('text-xl font-bold')

            with ui.scroll_area().classes('w-full h-full'):
                for language, doc_list in self.documents_by_language.items():
                    with ui.expansion(language, icon='folder') \
                            .classes('w-full text-lg text-zinc-950'):
                        for doc in doc_list:
                            ui.button(
                                doc.displayName,
                                on_click=self.show_document(doc.id),
                            ).classes('!normal-case !text-left !text-blue-950') \
                                    .style('text-align: left !important') \
                                    .props('flat')

@ui.refreshable
def document_sidebar():
    DocumentSidebar().display()


class UploadForm(EditComponent):
    """
    Upload a new document
    """

    CSS = '''
        .q-input {
            width: 100% !important;
        }
        .q-select {
            width: 100% !important;
        }
    '''

    def create_document(self):
        docdb = self.controller.create_document(
            user=self.user,
            displayName=self.document_title_input.value,
            language=self.language_input.value,
            binaryData=BinaryFileData(
                name=self._upload_event.name,
                data=self._upload_event.content.read(),
            ),
        )
        app.storage.client['documents']['all_documents'].append(docdb['document'])
        app.storage.client['documents']['current_document'] = docdb['document']
        app.storage.client['sentences'].update(docdb['sentences'])
        app.storage.client['words'].update(docdb['words'])

        ui.notify('Document Saved')
        document_sidebar.refresh()
        edit_area.refresh()
        self.cancel()

    def hold_onto_document(self, event: events.UploadEventArguments):
        """
        Hold on to the event that just marked the file upload.
        We still need to save the rest of the form.
        """
        self._upload_event = event

    def cancel(self):
        """
        Cancel the user form
        """
        self.hide_modal()
        # TODO: how do I reload?

    def hide_modal(self):
        """
        Hide the modal form.
        """
        self.modal_form.classes(add='hidden')
        self.modal_background.classes(add='hidden')

    def show_modal(self):
        """
        Show the modal form.
        """
        self.modal_form.classes(remove='hidden')
        self.modal_background.classes(remove='hidden')

    def display(self):
        self._upload_event = None

        with ui.card().classes(
            'absolute-center size-full bg-zinc-900/75 hidden',
        ) as self.modal_background:
            ui.label('')

        with ui.card().classes(
            'absolute-center upload-form hidden',
        ) as self.modal_form:
            ui.label('Upload a Document').classes('text-2xl')
            ui.separator()

            self.document_title_input = ui.input('Document Title')
            self.language_input = ui.select(
                label='Language',
                options=language_choices,
                with_input=True,
            )
            with ui.row():
                ui.label('Click the upload button before hitting Save') \
                        .classes('bold text-blue-950')
                ui.icon('arrow_downward').classes('bold text-lg text-blue-950')
            self.upload = ui.upload(
                on_upload=self.hold_onto_document,
                on_rejected=lambda: ui.notify('File too large (max 1MB)'),
                max_file_size=1_000_000,
            ).props('accept=.txt')

            ui.separator()
            with ui.row().classes('w-full'):
                ui.button('Cancel', on_click=self.cancel).classes('bg-warning')
                ui.space()
                ui.button('Save', on_click=self.create_document)


class UploadSidebar(EditComponent):
    """
    Area for uploads
    """
    def display(self):
        upload_form = UploadForm()

        with ui.card().classes('h-screen bg-secondary').style('flex-grow:100'):
            ui.button('Upload', on_click=upload_form.show_modal).classes('w-full')

            current_document = self.current_document
            if current_document:
                # TODO: set up translations
                #ui.button('Upload Translation').classes('w-full')
                pass

        upload_form.display()


@ui.refreshable
def upload_sidebar():
    UploadSidebar().display()


class Edit01Widget(EditWidget):
    """
    Allows the user to upload and manage vocabulary documents.
    """

    def display(self):
        with ui.row().classes('size-full flex'):
            document_sidebar()
            edit_area()
            upload_sidebar()
