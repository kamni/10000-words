"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from abc import ABC, abstractmethod
from typing import List

from common.models.users import UserDB, UserUI


class UserDBPort(ABC):
    """
    Handles CRUD for users in the database
    """

    @abstractmethod
    def create(self, user: UserDB) -> UserDB:
        """
        Create a new user in the database.

        :user: New user to add to the database.

        :return: Created user object.
        :raises: ObjectExistsError if the object already exists.
        """
        pass

    @abstractmethod
    def get(self, id: str) -> UserDB:
        """
        Get a user from the database using an ID.

        :id: User's UUID.

        :return: Found user object.
        :raises: ObjectNotFoundError if the user does not exist.
        """
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> UserDB:
        """
        Get a user from the database using a username.

        :username: User's username

        :return: Found user object.
        :raises: ObjectNotFoundError
        """
        pass


class UserUIPort(ABC):
    """
    Works with user objects for the UI
    """

    @abstractmethod
    def get(self, user: UserDB) -> UserUI:
        """
        Convert a database user into a UI user.

        :user: Database representation of a user.

        :return: UI representation of a user.
        """
        pass

