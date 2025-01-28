"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid

from django.test import TestCase

from common.adapters.users import (
    UserDBDjangoORMAdapter,
    UserUIDjangoORMAdapter,
)
from common.models.errors import ObjectExistsError, ObjectNotFoundError
from common.models.users import UserDB, UserUI

from words.models.users import UserSettings


class TestUserDBDjangoORMAdapter(TestCase):
    """
    Tests for backend.words.adapters.users.UserDBDjangoORMAdapter
    """

    def test_create(self):
        user = UserDB(
            username='test_create_user',
            password='1234567',
            display_name='Test User',
        )
        adapter = UserDBDjangoORMAdapter()

        # Check the returned object
        new_user = adapter.create(user)
        self.assertIsNotNone(new_user.id)
        self.assertTrue(new_user.password)  # non-empty string
        self.assertEqual(user.username, new_user.username)
        self.assertEqual(user.display_name, new_user.display_name)
        self.assertNotEqual(user.password, new_user.password)

        # Verify the database object
        new_db_user = UserSettings.objects.get(id=new_user.id)
        self.assertEqual(new_user.username, new_db_user.username)
        self.assertEqual(new_user.password, new_db_user.password)
        self.assertEqual(new_user.display_name, new_db_user.display_name)

    def test_create_without_password(self):
        user = UserDB(
            username='test_create_user_no_password',
            display_name='Test User',
        )
        adapter = UserDBDjangoORMAdapter()

        # Check the returned object
        new_user = adapter.create(user)
        self.assertIsNotNone(new_user.id)
        self.assertFalse(new_user.password)  # empty string
        self.assertEqual(user.username, new_user.username)
        self.assertEqual(user.display_name, new_user.display_name)

        # Verify the database object
        new_db_user = UserSettings.objects.get(id=new_user.id)
        self.assertFalse(new_db_user.password)  # empty string
        self.assertEqual(new_user.username, new_db_user.username)
        self.assertEqual(new_user.display_name, new_db_user.display_name)

    def test_create_duplicate_user(self):
        user = UserDB(
            username='test_create_user_duplicate_django_user',
            password='1234567',
            display_name='Test User',
        )
        adapter = UserDBDjangoORMAdapter()
        adapter.create(user)

        with self.assertRaises(ObjectExistsError):
            adapter.create(user)

    def test_get(self):
        user = UserDB(
            username='test_get',
            password='1234567',
            display_name='Test User',
        )
        adapter = UserDBDjangoORMAdapter()
        new_user = adapter.create(user)

        new_user_db = adapter.get(new_user.id)
        self.assertEqual(new_user, new_user_db)

    def test_get_user_settings_does_not_exist(self):
        user_id = uuid.uuid4()
        adapter = UserDBDjangoORMAdapter()

        with self.assertRaises(ObjectNotFoundError):
            adapter.get(user_id)

    def test_get_by_username(self):
        username = 'test_get_by_username'
        user = UserDB(
            username=username,
            password='1234567',
            display_name='Test User',
        )
        adapter = UserDBDjangoORMAdapter()

        new_user = adapter.create(user)
        new_user_db = adapter.get_by_username(username)
        self.assertEqual(new_user, new_user_db)

    def test_get_by_username_settings_does_not_exist(self):
        username = 'nonexistent_username'
        adapter = UserDBDjangoORMAdapter()

        with self.assertRaises(ObjectNotFoundError):
            adapter.get_by_username(username)


class TestUserUIDjangoORMAdapter(TestCase):
    """
    Tests for backend.words.adapters.users.UserUIDjangoORMAdapter
    """

    def test_get(self):
        user_db = UserDB(
            username='test_get',
            password='1234567',
            display_name='Test User',
        )
        db_adapter = UserDBDjangoORMAdapter()
        new_user_db = db_adapter.create(user_db)

        adapter = UserUIDjangoORMAdapter()
        expected = UserUI(
            id=new_user_db.id,
            username=new_user_db.username,
            displayName=new_user_db.display_name,
        )
        returned = adapter.get(new_user_db)
        self.assertEqual(expected, returned)

    def test_get_with_no_display_name(self):
        user_db = UserDB(
            username='test_get_no_display_name',
            password='1234567',
        )
        db_adapter = UserDBDjangoORMAdapter()
        new_user_db = db_adapter.create(user_db)

        adapter = UserUIDjangoORMAdapter()
        expected = UserUI(
            id=new_user_db.id,
            username=new_user_db.username,
            displayName=new_user_db.username,
        )
        returned = adapter.get(new_user_db)
        self.assertEqual(expected, returned)

