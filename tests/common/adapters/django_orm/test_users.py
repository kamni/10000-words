"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid

from django.contrib.auth.models import User
from django.test import TestCase

from common.adapters.django_orm.users import UserDBDjangoORMAdapter
from common.models.errors import (
    ObjectExistsError,
    ObjectNotFoundError,
    ObjectValidationError,
)
from common.models.users import UserDB, UserUI
from common.stores.app import AppStore
from users.models.profile import UserProfile
from tests.utils.users import create_user_db, make_user_db


class TestUserDBDjangoORMAdapter(TestCase):
    """
    Tests for backend.words.adapters.django_orm.users.UserDBDjangoORMAdapter
    """

    @classmethod
    def setUpClass(cls):
        AppStore.destroy_all()
        super().setUpClass()

    def setUp(self):
        app = AppStore(subsection='dev.django')
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
        self.assertNotEqual(user.password, new_user.password)

        # Verify the database object
        new_db_user = UserProfile.objects.get(id=new_user.id)
        self.assertTrue(new_db_user.password)
        self.assertEqual(new_user.username, new_db_user.username)
        self.assertEqual(new_user.display_name, new_db_user.display_name)

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
        new_db_user = UserProfile.objects.get(id=new_user.id)
        self.assertFalse(new_db_user.password)  # empty string
        self.assertEqual(new_user.username, new_db_user.username)
        self.assertEqual(new_user.display_name, new_db_user.display_name)

    def test_create_admin(self):
        user = UserDB(
            username='test_create_admin',
            password='fakepass390',
            display_name='Test User',
            is_admin=True,
        )
        userdb = self.adapter.create(user)

        new_user = UserProfile.objects.get(id=userdb.id)
        django_user = User.objects.get(id=new_user.user.id)
        self.assertTrue(new_user.is_admin)
        self.assertTrue(django_user.is_superuser)

    def test_create_duplicate_user(self):
        user = UserDB(
            username='test_create_user_duplicate_django_user',
            password='fakepass390',
            display_name='Test User',
        )
        self.adapter.create(user)

        with self.assertRaises(ObjectExistsError):
            self.adapter.create(user)

    def test_create_invalid_password(self):
        for badpass in ['12345678', 'abcdefgh', 'password']:
            user = UserDB(
                username=f'test_create_invalid_password_{badpass}',
                password=badpass,
            )
            with self.assertRaises(ObjectValidationError):
                self.adapter.create(user)

            # The adapter should have validated the password
            # before trying to create the object
            expected_count = 0
            returned_count = User.objects.filter(username=user.username).count()
            self.assertEqual(expected_count, returned_count)

    def test_create_user_has_id(self):
        userdb = make_user_db(id=uuid.uuid4())
        with self.assertRaises(ObjectValidationError):
            self.adapter.create(userdb)

    def test_create_ignore_errors(self):
        userdb = make_user_db()
        userdb.id = None
        new_userdb1 = self.adapter.create(userdb, ignore_errors=True)
        new_userdb2 = self.adapter.create(userdb, ignore_errors=True)
        self.assertEqual(new_userdb1, new_userdb2)
        self.assertEqual(new_userdb1.id, new_userdb2.id)

    def test_create_ignore_errors_password_invalid(self):
        userdb = make_user_db()
        userdb.id = None
        userdb.password = 'invalid'
        # We only care that this doesn't error
        try:
            new_userdb = self.adapter.create(userdb, ignore_errors=True)
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False, 'UserDB create threw unexpected error')

    def test_create_ignore_errors_has_multiple_matching_profiles(self):
        userdb1 = create_user_db()
        userdb2 = create_user_db()
        userdb3 = make_user_db(id=userdb1.id, username=userdb2.username)
        with self.assertRaises(ObjectExistsError):
            self.adapter.create(userdb3, ignore_errors=True)

    def test_create_ignore_errors_django_user_exists(self):
        user = User.objects.create(username='django_user_exists')
        self.assertFalse(user.password)  # depending on DB, '' or None
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        userdb = make_user_db(
            username=user.username,
            password='invalid',
            is_admin=True,
        )
        new_userdb = self.adapter.create(userdb, ignore_errors=True)
        user.refresh_from_db()

        self.assertIsNotNone(user.password)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_ignore_errors_user_profile_exists(self):
        userdb1 = create_user_db()
        userdb2 = make_user_db(
            id=userdb1.id,
            username=userdb1.username,
        )
        new_userdb = self.adapter.create(userdb2, ignore_errors=True)
        self.assertEqual(userdb1, new_userdb)

    def test_get(self):
        user = UserDB(
            username='test_get',
            password='fakepass390',
            display_name='Test User',
        )
        new_user = self.adapter.create(user)

        new_user_db = self.adapter.get(new_user.id)
        self.assertEqual(new_user, new_user_db)

    def test_get_user_profile_does_not_exist(self):
        user_id = uuid.uuid4()

        with self.assertRaises(ObjectNotFoundError):
            self.adapter.get(user_id)

    def test_get_user_is_active_false(self):
        user = UserDB(
            username='test_get_inactive',
            password='fakepass390',
            display_name='Test User',
        )
        userdb = self.adapter.create(user)
        profile = UserProfile.objects.get(id=userdb.id)
        profile.user.is_active = False
        profile.user.save()

        with self.assertRaises(ObjectNotFoundError):
            self.adapter.get(userdb.id)

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

    def test_get_first_is_active_false(self):
        user = UserDB(
            username='test_get_first_inactive',
            password='fakepass390',
            display_name='Test User',
        )
        userdb = self.adapter.create(user)

        expected = userdb
        returned = self.adapter.get_first()
        self.assertEqual(expected, returned)

        profile = UserProfile.objects.get(id=userdb.id)
        profile.user.is_active = False
        profile.user.save()

        self.assertIsNone(self.adapter.get_first())

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

    def test_get_by_username_profile_does_not_exist(self):
        username = 'nonexistent_username'

        with self.assertRaises(ObjectNotFoundError):
            self.adapter.get_by_username(username)

    def test_get_by_username_user_inactive(self):
        user = UserDB(
            username='test_get_username_inactive',
            password='fakepass390',
            display_name='Test User',
        )
        userdb = self.adapter.create(user)

        profile = UserProfile.objects.get(id=userdb.id)
        profile.user.is_active = False
        profile.user.save()

        with self.assertRaises(ObjectNotFoundError):
            self.assertIsNone(self.adapter.get_by_username(userdb.username))

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

        # ignore this user
        user3 = UserDB(
            username='test_get_all3',
            password='fakepass390',
            display_name='Test User',
        )
        userdb3 = self.adapter.create(user3)
        profile = UserProfile.objects.get(id=userdb3.id)
        profile.user.is_active = False
        profile.user.save()

        expected = [user1, user2]
        returned = self.adapter.get_all()
        self.assertEqual(expected, returned)

    def test_get_all_table_empty(self):
        expected = []
        returned = self.adapter.get_all()
        self.assertEqual(expected, returned)

    def test_update(self):
        userdb = UserDB(
            username='test_update',
            password='fakepass390',
            display_name='Test User',
        )
        new_userdb = self.adapter.create(userdb)
        old_password = UserProfile.objects.get(id=new_userdb.id).password

        new_userdb.is_admin = True
        new_userdb.display_name = 'New Test User'
        new_userdb.password = 'foo'
        new_userdb.username = 'Should not change!'

        final_userdb = self.adapter.update(new_userdb)
        new_password = UserProfile.objects.get(id=new_userdb.id).password
        self.assertNotEqual(old_password, new_password)
        self.assertEqual(new_userdb.display_name, final_userdb.display_name)
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
