"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from nicegui import app, events, ui

from common.models.documents import DocumentDB, DocumentUI
from common.stores.adapter import AdapterStore
from common.utils.languages import language_choices

from frontend.controllers.documents import DocumentController
from frontend.widgets.base import BaseWidget


class EditComponent(BaseWidget):
    """
    Useful properties for all parts of the EditWidget
    """

    @property
    def current_document(self) -> DocumentUI:
        return self.document_controller.get_current_document()

    @current_document.setter
    def current_document(self, doc: DocumentUI):
        self.document_controller.set_current_document(doc)

    @property
    def documents(self):
        return self.document_controller.get_all()

    def set_controllers(self):
        self.document_controller = DocumentController()


class EditArea(EditComponent):
    """
    Area for editing documents
    """
    def show_content(self):
        if not self.documents:
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
        all_docs = self.document_controller.get_all()
        by_language = {}
        for doc in all_docs:
            if doc.language in by_language:
                by_language[doc.language].append(doc)
            else:
                by_language[doc.language] = [doc]
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
                on_upload=self._hold_onto_document,
                on_rejected=lambda: ui.notify('File too large (max 1MB)'),
                max_file_size=1_000_000,
            ).props('accept=.txt')

            ui.separator()
            with ui.row().classes('w-full'):
                ui.button('Cancel', on_click=self.cancel).classes('bg-warning')
                ui.space()
                ui.button('Save', on_click=self._create_document)

    def _create_document(self):
        if not self._upload_event:
            # TODO: add validation
            return

        self.document_controller.create({
            'user': self.user,
            'display_name': self.document_title_input.value,
            'language': self.language_input.value,
            'upload': self._upload_event,
        })
        ui.notify('Document Saved')

        document_sidebar.refresh()
        edit_area.refresh()
        self.cancel()

    def _hold_onto_document(self, event: events.UploadEventArguments):
        """
        Hold on to the event that just marked the file upload.
        We still need to save the rest of the form.
        """
        self._upload_event = event


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
