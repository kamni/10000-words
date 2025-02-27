"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from unittest import TestCase, mock

from nicegui.observables import ObservableDict

from common.models.settings import AppSettingsDB, AppSettingsUI
from common.stores.app import AppStore
from frontend.controllers.settings import SettingsController


class TestSettingsController(TestCase):
    """
    Tests for frontend.controllers.settings.SettingsController
    """

    @classmethod
    def setUpClass(cls):
        AppStore.destroy_all()
        super().setUpClass()

    def setUp(self):
        apps = AppStore(subsection='dev.in_memory')
        adapters = apps.get('AdapterStore')
        self.backend_adapter = adapters.get('AppSettingsDBPort')
        self.frontend_adapter = adapters.get('AppSettingsUIPort')
        self.controller = SettingsController()

    def tearDown(self):
        AppStore.destroy_all()

    def test_get(self):
        settings_db = AppSettingsDB(multiuser_mode=True)

        expected_settings_ui = self.frontend_adapter.get(settings_db)
        with mock.patch('frontend.controllers.settings.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.client = {
                'settings': expected_settings_ui.model_dump(),
            }
            returned_settings_ui = self.controller.get()

        self.assertEqual(expected_settings_ui, returned_settings_ui)

    def test_get_settings_not_created_yet(self):
        expected_settings_ui = AppSettingsUI()
        with mock.patch('frontend.controllers.settings.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.client = ObservableDict()
            returned_settings_ui = self.controller.get()

        self.assertEqual(expected_settings_ui, returned_settings_ui)

    def test_get_db(self):
        settings_db = AppSettingsDB(passwordless_login=True)
        expected_settings_db = self.backend_adapter.create_or_update(settings_db)
        returned_settings_db = self.controller.get_db()
        self.assertEqual(expected_settings_db, returned_settings_db)

    def test_get_db_settings_not_created_yet(self):
        expected_settings_db = AppSettingsDB()
        returned_settings_db = self.controller.get_db()
        self.assertEqual(expected_settings_db, returned_settings_db)

    def test_set(self):
        settings_db = AppSettingsDB(multiuser_mode=True)
        new_settings_db = self.backend_adapter.create_or_update(settings_db)

        expected_dict = self.frontend_adapter.get(new_settings_db).model_dump()
        with mock.patch('frontend.controllers.settings.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.client = ObservableDict()

            self.controller.set()
            returned_dict = mock_app.storage.client['settings']

        self.assertEqual(expected_dict, returned_dict)

    def test_set_settings_not_created_yet(self):
        expected_dict = AppSettingsUI().model_dump()
        with mock.patch('frontend.controllers.settings.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.client = ObservableDict()

            self.controller.set()
            returned_dict = mock_app.storage.client['settings']

        self.assertEqual(expected_dict, returned_dict)

    def test_update(self):
        expected_settings_db = AppSettingsDB(
            multiuser_mode=True,
            passwordless_login=True,
            show_users_on_login_screen=True,
        )
        expected_dict = self.frontend_adapter.get(expected_settings_db).model_dump()
        with mock.patch('frontend.controllers.settings.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.client = ObservableDict()

            self.controller.update({
                'multiuser_mode': True,
                'passwordless_login': True,
                'show_users_on_login_screen': True,
            })
            returned_dict = mock_app.storage.client['settings']
            returned_settings_db = self.backend_adapter.get()

        self.assertEqual(expected_settings_db, returned_settings_db)
        self.assertEqual(expected_dict, returned_dict)

        expected_settings_db = AppSettingsDB()
        expected_dict = self.frontend_adapter.get(expected_settings_db).model_dump()
        with mock.patch('frontend.controllers.settings.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.client = ObservableDict()

            self.controller.update({
                'multiuser_mode': False,
                'passwordless_login': False,
                'show_users_on_login_screen': False,
            })
            returned_dict = mock_app.storage.client['settings']
            returned_settings_db = self.backend_adapter.get()

        self.assertEqual(expected_settings_db, returned_settings_db)
        self.assertEqual(expected_dict, returned_dict)
