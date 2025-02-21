"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from unittest import TestCase, mock

from nicegui.observables import ObservableDict

from common.models.users import UserDB, UserUI
from common.stores.app import AppStore
from frontend.controllers.users import UserController
from tests.utils.users import create_user_db, make_user_ui


class TestUserController(TestCase):
    """
    Tests for frontend.controllers.users.UserController
    """

    @classmethod
    def setUpClass(cls):
        AppStore.destroy_all()
        super().setUpClass()

    def setUp(self):
        apps = AppStore(subsection='dev.in_memory')
        adapters = apps.get('AdapterStore')
        self.backend_adapter = adapters.get('UserDBPort')
        self.frontend_adapter = adapters.get('UserUIPort')
        self.controller = UserController()

    def tearDown(self):
        AppStore.destroy_all()

    def test_get(self):
        expected_user = make_user_ui(id=uuid.uuid4(), authenticated=True)
        with mock.patch('frontend.controllers.users.app') as mock_app:
            mock_app.storage = mock.MagicMock()
            mock_app.storage.user = expected_user.model_dump()
            returned_user = self.controller.get()

        self.assertEqual(expected_user, returned_user)

    def test_get_user_not_set(self):
        with mock.patch('frontend.controllers.users.app') as mock_app:
            mock_app.storage = mock.MagicMock()
            mock_app.storage.user = {}
            returned_user = self.controller.get()

        self.assertIsNone(returned_user)

    def test_get_all(self):
        usersdb = [create_user_db() for i in range(3)]
        expected_users = self.frontend_adapter.get_all(usersdb)
        returned_users = self.controller.get_all()
        self.assertEqual(expected_users, returned_users)

    def test_get_all_no_users(self):
        expected_users = []
        returned_users = self.controller.get_all()
        self.assertEqual(expected_users, returned_users)

    def test_get_first(self):
        usersdb = [create_user_db() for i in range(3)]
        expected_user = self.frontend_adapter.get(usersdb[0])
        returned_user = self.controller.get_first()
        self.assertEqual(expected_user, returned_user)

    def test_get_first_no_users(self):
        returned_user = self.controller.get_first()
        self.assertIsNone(returned_user)

    def test_reset(self):
        user = make_user_ui(id=uuid.uuid4())
        with mock.patch('frontend.controllers.users.app') as mock_app:
            mock_app.storage = mock.MagicMock()
            mock_app.storage.user = ObservableDict()
            mock_app.storage.user.update(user.model_dump())
            self.assertEqual(user, self.controller.get())

            self.controller.reset()
            self.assertIsNone(self.controller.get())

    def test_reset_no_user(self):
        with mock.patch('frontend.controllers.users.app') as mock_app:
            mock_app.storage = mock.Mock()
            mock_app.storage.user = ObservableDict()

            self.controller.reset()
            self.assertIsNone(self.controller.get())
'''
    def reset(self):
        app.storage.user.clear()

    def set(self, user: UserUI):
        if not user.authenticated:
            user.authenticated = True
        app.storage.user.update(user.model_dump())

    def update(self, user_dict: Dict[str, Any]):
        user = UserDB(
            display_name=user_dict.get('display_name'),
            username=user_dict.get('username'),
            password=user_dict.get('password'),
            is_admin=user_dict.get('is_admin'),
        )
        self.backend_adapter.create(user)
'''
