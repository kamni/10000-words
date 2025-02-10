"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from django.test import TestCase

from common.adapters.ui.users import UserUIAdapter
from common.models.users import UserDB, UserUI


class TestUserUIAdapter(TestCase):
    """
    Tests for common.adapters.ui.users.UserUIAdapter
    """

    @classmethod
    def setUpClass(cls):
        adapters = AdapterStore(subsection='dev.django')
        cls.adapter = adapters.get('UserUIPort')
        super().setUpClass()

    def test_get(self):
        user_db = UserDB(
            username='test_get',
            password='1234567',
            display_name='Test User',
        )
        db_adapter = UserDBDjangoORMAdapter()
        new_user_db = db_adapter.create(user_db)

        expected = UserUI(
            id=new_user_db.id,
            username=new_user_db.username,
            displayName=new_user_db.display_name,
        )
        returned = self.adapter.get(new_user_db)
        self.assertEqual(expected, returned)

    def test_get_with_no_display_name(self):
        user_db = UserDB(
            username='test_get_no_display_name',
            password='1234567',
        )
        db_adapter = UserDBDjangoORMAdapter()
        new_user_db = db_adapter.create(user_db)

        expected = UserUI(
            id=new_user_db.id,
            username=new_user_db.username,
            displayName=new_user_db.username,
        )
        returned = self.adapter.get(new_user_db)
        self.assertEqual(expected, returned)

    def test_get_all(self):
        user_db1 = UserDB(
            id=uuid.uuid4(),
            username='test_get_all1',
            password='1234567',
            display_name='Test User'
        )
        user_db2 = UserDB(
            id=uuid.uuid4(),
            username='test_get_all2',
            password='1234567',
        )

        expected = [
            UserUI(
                id=user_db1.id,
                username=user_db1.username,
                displayName=user_db1.display_name,
            ),
            UserUI(
                id=user_db2.id,
                username=user_db2.username,
                displayName=user_db2.username,
            ),
        ]
        returned = self.adapter.get_all([user_db1, user_db2])
        self.assertEqual(expected, returned)

    def test_get_all_empty_list(self):
        expected = []
        returned = self.adapter.get_all([])
        self.assertEqual(expected, returned)
