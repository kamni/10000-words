"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from django.test import TestCase

from common.models.users import UserDB, UserUI

from words.adapters.users import (
    UserDBDjangoORMAdapter,
    UserUIDjangoORMAdapter,
)
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
        self.assertIsNotNone(new_user.password)
        self.assertEqual(user.username, new_user.username)
        self.assertEqual(user.display_name, new_user.display_name)
        self.assertNotEqual(user.password, new_user.password)

        # Verify the database object
        new_db_user = UserSettings.objects.get(id=new_user.id)
        self.assertEqual(new_user.username, new_db_user.username)
        self.assertEqual(new_user.password, new_db_user.password)
        self.assertEqual(new_user.display_name, new_db_user.display_name)

    def test_create_without_password(self):
        pass

    def test_create_duplicate_user(self):
        pass

    def test_create_duplicate_user_settings(self):
        pass

    def test_get(self):
        pass

    def test_get_user_settings_does_not_exist(self):
        pass

    def test_get_by_username(self):
        pass

    def test_get_by_username_settings_does_not_exist(self):
        pass


class TestUserUIDjangoORMAdapter(TestCase):
    """
    Tests for backend.words.adapters.users.UserUIDjangoORMAdapter
    """

    def test_get(self):
        pass
