"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path
import uuid

from django.contrib.auth.models import User
from django.test import TestCase

from common.models.errors import (
    ObjectExistsError,
    ObjectNotFoundError,
    ObjectValidationError,
)
from common.models.users import UserDB, UserUI
from common.stores.app import AppStore


TEST_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent.parent
TEST_CONFIG = TEST_CONFIG_DIR / 'setup.cfg'


class TestUserDBInMemoryAdapter(TestCase):
    """
    Tests for common.adapters.in_memory.users.UserDBInMemoryAdapter
    """

    @classmethod
    def setUpClass(cls):
        AppStore.destroy_all()
        super().setUpClass()

    def setUp(self):
        app = AppStore(config=TEST_CONFIG, subsection='dev.in_memory')
        adapters = app.get('AdapterStore')
        self.adapter = adapters.get('UserDBPort')

    def tearDown(self):
        AppStore.destroy_all()

    def test_create(self):
        user = UserDB(
            username='test_create_user',
            password='fakepass390',
            display_name='Test User',
        )

        # Check the returned object
        new_user = self.adapter.create(user)
        self.assertIsNotNone(new_user.id)
        self.assertFalse(new_user.password)  # We don't return passwords
        self.assertEqual(user.username, new_user.username)
        self.assertEqual(user.display_name, new_user.display_name)
        self.assertIsNone(new_user.password) # Shouldn't return password

        # Verify the database object
        new_userdb = self.adapter.get(new_user.id)
        expected = new_user.username
        returned = new_userdb.username
        self.assertEqual(expected, returned)

    def test_create_without_password(self):
        user = UserDB(
            username='test_create_user_no_password',
            display_name='Test User',
        )

        # Check the returned object
        new_user = self.adapter.create(user)
        self.assertIsNotNone(new_user.id)
        self.assertFalse(new_user.password)  # empty string
        self.assertEqual(user.username, new_user.username)
        self.assertEqual(user.display_name, new_user.display_name)

        # Verify the database object
        new_userdb = self.adapter.get(new_user.id)
        self.assertIsNone(new_userdb.password)  # empty string
        self.assertEqual(new_user.username, new_userdb.username)
        self.assertEqual(new_user.display_name, new_userdb.display_name)

    def test_create_admin(self):
        user = UserDB(
            username='test_create_admin',
            password='fakepass390',
            display_name='Test User',
            is_admin=True,
        )
        userdb = self.adapter.create(user)

        new_userdb = self.adapter.get(userdb.id)
        self.assertTrue(new_userdb.is_admin)

    def test_create_duplicate_user(self):
        user = UserDB(
            username='test_create_user_duplicate_django_user',
            password='fakepass390',
            display_name='Test User',
        )
        self.adapter.create(user)

        with self.assertRaises(ObjectExistsError):
            self.adapter.create(user)

    def test_create_duplicate_user_ignore_errors(self):
        userdb = UserDB(
            username='test_duplicate_user_ignore_errors',
            password='fakepass390',
            display_name='Test User',
            is_admin=False,
        )
        new_userdb1 = self.adapter.create(userdb)

        # We expect these to be updated
        userdb.password = 'fakepass772'
        userdb.display_name = 'Test User 2'
        userdb.is_admin = True
        new_userdb2 = self.adapter.create(userdb, ignore_errors=True)

        self.assertEqual(new_userdb1.id, new_userdb2.id)
        self.assertEqual('Test User 2', new_userdb2.display_name)
        self.assertTrue(new_userdb2.is_admin)

    def test_get(self):
        user = UserDB(
            username='test_get',
            password='fakepass390',
            display_name='Test User',
        )
        new_user = self.adapter.create(user)

        new_user_db = self.adapter.get(new_user.id)
        self.assertEqual(new_user, new_user_db)

    def test_get_user_does_not_exist(self):
        user_id = uuid.uuid4()

        with self.assertRaises(ObjectNotFoundError):
            self.adapter.get(user_id)

    def test_get_first(self):
        user = UserDB(
            username='test_get_first',
            password='fakepass390',
            display_name='Test User',
        )
        self.adapter.create(user)

        expected = user
        returned = self.adapter.get_first()
        self.assertEqual(expected, returned)

    def test_get_first_database_empty(self):
        self.assertIsNone(self.adapter.get_first())

    def test_get_first_more_than_one(self):
        user1 = UserDB(
            username='test_get_first_more_than_one1',
            password='fakepass390',
            display_name='Test User',
        )
        self.adapter.create(user1)

        user2 = UserDB(
            username='test_get_first_more_than_one2',
            password='fakepass390',
            display_name='Test User',
        )
        self.adapter.create(user2)

        expected = user1
        returned = self.adapter.get_first()
        self.assertEqual(expected, returned)

    def test_get_by_username(self):
        username = 'test_get_by_username'
        user = UserDB(
            username=username,
            password='fakepass390',
            display_name='Test User',
        )

        new_user = self.adapter.create(user)
        new_user_db = self.adapter.get_by_username(username)
        self.assertEqual(new_user, new_user_db)

    def test_get_by_username_settings_does_not_exist(self):
        username = 'nonexistent_username'

        with self.assertRaises(ObjectNotFoundError):
            self.adapter.get_by_username(username)

    def test_get_all(self):
        user1 = UserDB(
            username='test_get_all1',
            password='fakepass390',
            display_name='Test User',
        )
        self.adapter.create(user1)

        user2 = UserDB(
            username='test_get_all2',
            password='fakepass390',
            display_name='Test User',
        )
        self.adapter.create(user2)

        expected = [user1, user2]
        returned = self.adapter.get_all()
        self.assertEqual(expected, returned)

    def test_get_all_table_empty(self):
        expected = []
        returned = self.adapter.get_all()
        self.assertEqual(expected, returned)

    def test_get_password(self):
        user = UserDB(
            username='foo',
            password='bar',
        )
        userdb = self.adapter.create(user)

        expected = user.password
        returned = self.adapter.get_password(userdb.id)
        self.assertEqual(expected, returned)

    def test_get_password_user_does_not_exist(self):
        fake_uuid = uuid.uuid4()
        with self.assertRaises(ObjectNotFoundError):
            self.adapter.get_password(fake_uuid)

    def test_update(self):
        userdb = UserDB(
            username='test_update',
            password='fakepass390',
            display_name='Test User',
        )
        new_userdb = self.adapter.create(userdb)
        old_password = 'fakepass390'

        new_userdb.is_admin = True
        new_userdb.display_name = 'New Test User'
        new_userdb.password = 'foo'
        new_userdb.username = 'Should not change!'

        final_userdb = self.adapter.update(new_userdb)
        new_password = self.adapter.store.db.users[0].password
        self.assertEqual(new_password, 'foo')
        self.assertEqual(final_userdb.display_name, 'New Test User')
        self.assertEqual(userdb.username, final_userdb.username)
        self.assertTrue(final_userdb.is_admin)

    def test_update_does_not_exist(self):
        userdb = UserDB(
            id=uuid.uuid4(),
            username='test_update_not_exists',
            password='fakepass390',
            display_name='Test User',
        )
        with self.assertRaises(ObjectNotFoundError):
            self.adapter.update(userdb)
