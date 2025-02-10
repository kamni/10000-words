"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import List

from ...models.users import UserDB, UserUI
from ...ports.users import UserUIPort


class UserUIAdapter(UserUIPort):
    """
    Works with user objects for the UI
    """

    def __init__(self, **kwargs):
        # Ignore any kwargs configuration.
        # This uses the django settings.
        super().__init__()

    def _db_to_ui(self, user: UserDB) -> UserUI:
        user_ui = UserUI(
            id=user.id,
            username=user.username,
            displayName=user.display_name or user.username,
            isAdmin=user.is_admin,
        )
        return user_ui

    def get(self, user: UserDB) -> UserUI:
        """
        Convert a database user into a UI user.

        :user: Database representation of a user.

        :return: UI representation of a user.
        """
        user_ui = self._db_to_ui(user)
        return user_ui

    def get_all(self, users: List[UserDB]) -> List[UserUI]:
        """
        Convert all database users to users for the UI.

        :users: List of database representations of users.

        :return: List of UI representations of the users.
        """

        usersui = [self._db_to_ui(user) for user in users]
        return usersui
