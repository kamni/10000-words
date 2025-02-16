"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from nicegui import ElementFilter, app, events, ui
from nicegui.elements.label import Label

from common.models.documents import DocumentDB, DocumentUI, DocumentUIMinimal
from common.models.files import BinaryFileData
from common.stores.adapter import AdapterStore
from common.utils.languages import language_code_choices

from .base import BaseWidget


class EditComponent(BaseWidget):
    """
    Useful properties for all parts of the EditWidget
    """
    @property
    def current_document(self) -> DocumentUI:
        document_dict = app.storage.client['documents']['current_document']
        if document_dict is not None:
            document = DocumentUI(**document_dict)
            return document
        return None

    @current_document.setter
    def current_document(self, doc: DocumentUI):
        app.storage.client['documents']['current_document'] = doc.model_dump()

    @property
    def documents(self):
        doc_dicts = app.storage.client['documents']['all_documents']
        docs = [DocumentUI(**doc) for doc in doc_dicts]
        return docs


# TODO: update when no longer prototyping
class WordLabel(Label):
    """
    Displays an individual word.
    """

    def __init__(self, display_text_obj, sentence_obj):
        self.display_text = display_text_obj
        self.sentence = sentence_obj
        self.word = display_text_obj['word']

        super().__init__(text=self.display_text['text'])


class EditArea(EditComponent):
    """
    Area for editing documents
    """

    CSS = '''
        .text-gap {
            gap: 0 !important;
        }
    '''

    # TODO: this is ugly.
    # When we have it in a non-prototype space, fix this
    @property
    def WordStatus(self):
        from scripts.prototype_deleteme import WordStatus
        return WordStatus

    def get_status_classes(self, status: str):
        # TODO: define classes globally for the widget?
        # We can use SASS, apparently!
        return {
            self.WordStatus.not_set: ' bg-zinc-400 text-zinc-950',
            self.WordStatus.ignored: ' bg-zinc-50 text-zinc-950',
            self.WordStatus.to_learn: ' bg-violet-300 text-zinc-950',
            self.WordStatus.learning: ' bg-emerald-300 text-zinc-950',
            self.WordStatus.learned: ' bg-zinc-50 text-zinc-950',
        }[status]

    def context_menu(self, element):
        not_set = self.get_status_classes(self.WordStatus.not_set)
        ignored = self.get_status_classes(self.WordStatus.ignored)
        to_learn = self.get_status_classes(self.WordStatus.to_learn)
        learning = self.get_status_classes(self.WordStatus.learning)
        learned = self.get_status_classes(self.WordStatus.learned)

        with ui.context_menu().classes('bg-dark text-zinc-50'):
            ui.label('Set Status:').classes('p-2 text-center')
            ui.separator()

            ui.menu_item(
                'Ignored',
                lambda: self.set_word_status(element, self.WordStatus.ignored),
            ).classes(ignored)
            ui.menu_item(
                'To Learn',
                lambda: self.set_word_status(element, self.WordStatus.to_learn),
            ).classes(to_learn)
            ui.menu_item(
                'Learning',
                lambda: self.set_word_status(element, self.WordStatus.learning),
            ).classes(learning)
            ui.menu_item(
                'Learned',
                lambda: self.set_word_status(element, self.WordStatus.learned),
            ).classes(learned)

            ui.separator()
            ui.label('Multi-Word Actions:').classes('p-2 text-center')
            ui.separator()
            ui.menu_item('Combine Words', self.combine_words) \
                    .classes('bg-amber-400 text-zinc=950')

    # TODO: prototype
    def set_word_status(self, element, status):
        element.classes(remove='outline')
        classes = self.get_status_classes(status)
        element.classes(add=classes)

        # TODO: we actually need to update these elements in the backend
        for elem in ElementFilter(marker=element._markers[0]):
            elem.classes(remove='outline')
            elem.classes(add=classes)

    def clear_collected_words(self):
        for word_label in self._collected_words:
            word_label.classes(remove='!bg-amber-400')
        self._collected_words = []

    # TODO: temporary prototype
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
                'status': self.WordStatus.not_set,
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

    # TODO: Temporary prototype; add correct typing later
    def display_sentence(self, sentence):
        from scripts.prototype_deleteme import WordStatus
        with ui.row().classes('text-gap'):
            for display_text in sentence['word_display_text']:
                with WordLabel(display_text, sentence) as wl:
                    wl.mark(f'{wl.word['id']}')
                    classes = self.get_status_classes(wl.word['status'])
                    wl.classes(
                        'cursor-pointer text-lg px-2 py-2 rounded-lg' + classes
                    )
                    wl.on('click', self.collect_words)
                    self.context_menu(wl)

    def show_content(self):
        if not app.storage.client['documents']['all_documents']:
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
        doc_dicts = app.storage.client['documents']['all_documents']
        by_language = {}
        for doc in doc_dicts:
            doc_ui = DocumentUIMinimal(**doc)
            if doc_ui.language in by_language:
                by_language[doc_ui.language].append(doc_ui)
            else:
                by_language[doc_ui.language] = [doc_ui]
        return by_language

    def show_document(self, doc_id):
        def _on_click():
            # TODO: we'll have to fetch full doc ffom server
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

    def update_documents(self, document: DocumentDB):
        adapter = self.adapters.get('DocumentUIPort')
        doc_ui = adapter.get(document, self.user)
        app.storage.client['documents']['all_documents'].append(
            doc_ui.model_dump(),
        )
        self.current_document = doc_ui

    def create_document(self):
        if not self._upload_event:
            # TODO: add validation
            return
        adapter = self.adapters.get('DocumentDBPort')
        # TODO: add validation
        # TODO: check if document already exists and ask what to do
        document = DocumentDB(
            user_id=self.user.id,
            display_name=self.document_title_input.value,
            language_code=self.language_input.value,
            binary_data=BinaryFileData(
                name=self._upload_event.name,
                data=self._upload_event.content.read(),
            ),
        )
        new_doc = adapter.create_or_update(document)
        ui.notify('Document Saved')

        self.update_documents(new_doc)
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
                options=language_code_choices,
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


class EditWidget(BaseWidget):
    """
    Allows the user to upload and manage vocabulary documents.
    """

    CSS = '''
        body {
            background-color: var(--q-secondary) !important;
        }
    '''

    def display(self):
        with ui.row().classes('size-full flex'):
            document_sidebar()
            edit_area()
            upload_sidebar()
