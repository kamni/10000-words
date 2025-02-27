"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from pathlib import Path
from unittest import TestCase, mock

from nicegui.observables import ObservableDict

from common.models.documents import DocumentDB, DocumentUI
from common.stores.app import AppStore
from common.utils.files import get_project_dir
from frontend.controllers.documents import DocumentController
from tests.utils.documents import create_document_db, make_document_ui
from tests.utils.users import create_user_db, make_user_ui


DATA_DIR = get_project_dir() / 'scripts' / 'data' / 'en'
DATA_FILE = DATA_DIR / 'Little-Red-Riding-Hood.txt'


class TestDocumentController(TestCase):
    """
    Tests for frontend.controllers.document.DocumentController
    """

    @classmethod
    def setUpClass(cls):
        AppStore.destroy_all()
        super().setUpClass()

    def setUp(self):
        apps = AppStore(subsection='dev.in_memory')
        adapters = apps.get('AdapterStore')
        self.backend_adapter = adapters.get('DocumentDBPort')
        self.frontend_adapter = adapters.get('DocumentUIPort')
        self.userui_adapter = adapters.get('UserUIPort')
        self.controller = DocumentController()

    def tearDown(self):
        AppStore.destroy_all()

    def test_create(self):
        userdb = create_user_db()
        user = self.userui_adapter.get(userdb)

        with open(DATA_FILE, 'rb') as datafile:
            mock_upload = mock.Mock()
            mock_upload.name = 'foo.txt'
            mock_upload.content = datafile
            document_dict = {
                'user': user,
                'display_name': 'Test Create',
                'language': 'Spanish',
                'upload': mock_upload,
            }

            expected_docui = DocumentUI(
                id=uuid.uuid4(),  # Not the real UUID after creation
                user=user,
                displayName='Test Create',
                language='Spanish',
                sentences=[],
            )
            with mock.patch('frontend.controllers.documents.app') as mock_app:
                mock_app.storage = mock.Mock()
                mock_app.storage.client = ObservableDict()
                mock_app.storage.client.update({
                    'documents': {
                        'current_document': None,
                        'all_documents': [],
                    },
                })
                self.controller.create(document_dict)
                returned_docui = self.controller.get_current_document()
                for attr in ('user', 'displayName', 'language'):
                    expected = getattr(expected_docui, attr)
                    returned = getattr(returned_docui, attr)
                    self.assertEqual(expected, returned)

        returned_docdb = self.backend_adapter.get(returned_docui.id, user.id)
        self.assertEqual('Test Create', returned_docdb.display_name)
        self.assertEqual('es', returned_docdb.language_code)

    def test_get_all(self):
        userui = make_user_ui()
        expected_docsui = [make_document_ui(user=userui) for i in range(3)]
        with mock.patch('frontend.controllers.documents.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.client = ObservableDict()
            mock_app.storage.client.update({
                'documents': {
                    'current_document': None,
                    'all_documents': [doc.model_dump() for doc in expected_docsui],
                },
            })
            returned_docsui = self.controller.get_all()
            self.assertEqual(expected_docsui, returned_docsui)

    def test_get_all_no_documents(self):
        with mock.patch('frontend.controllers.documents.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.client = ObservableDict()
            mock_app.storage.client.update({
                'documents': {
                    'current_document': None,
                    'all_documents': [],
                },
            })
            returned_docsui = self.controller.get_all()
            self.assertEqual([], returned_docsui)

    def test_get_current_document(self):
        expected_docui = make_document_ui()
        with mock.patch('frontend.controllers.documents.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.client = ObservableDict()
            mock_app.storage.client.update({
                'documents': {
                    'current_document': expected_docui.model_dump(),
                    'all_documents': [expected_docui.model_dump()],
                },
            })
            returned_docui = self.controller.get_current_document()
            self.assertEqual(expected_docui, returned_docui)

    def test_get_current_document_no_document(self):
        with mock.patch('frontend.controllers.documents.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.client = ObservableDict()
            mock_app.storage.client.update({
                'documents': {
                    'current_document': None,
                    'all_documents': [],
                },
            })
            returned_docui = self.controller.get_current_document()
            self.assertIsNone(returned_docui)

    def test_set(self):
        userdb = create_user_db()
        user = self.userui_adapter.get(userdb)
        docdbs = [create_document_db(user_id=userdb.id) for i in range(3)]
        docs = self.frontend_adapter.get_all(docdbs, user)

        expected_data = {
            'current_document': None,
            'all_documents': [doc.model_dump() for doc in docs],
        }
        with mock.patch('frontend.controllers.documents.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.client = ObservableDict()
            self.controller.set(user)

            returned_data = mock_app.storage.client.get('documents')
            self.assertEqual(expected_data, returned_data)

    def test_set_no_documents(self):
        userdb = create_user_db()
        user = self.userui_adapter.get(userdb)

        expected_data = {
            'current_document': None,
            'all_documents': [],
        }
        with mock.patch('frontend.controllers.documents.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.client = ObservableDict()
            self.controller.set(user)

            returned_data = mock_app.storage.client.get('documents')
            self.assertEqual(expected_data, returned_data)

    def test_set_current_document(self):
        document = make_document_ui()

        with mock.patch('frontend.controllers.documents.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.client = ObservableDict()
            mock_app.storage.client.update({
                'documents': {
                    'current_document': None,
                    'all_documents': [],
                },
            })
            self.controller.set_current_document(document)
            returned = self.controller.get_current_document()
            self.assertEqual(document, returned)
