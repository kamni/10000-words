"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Union

from common.models.users import UserDB, UserUI


class UserDBPort(ABC):
    """
    Handles CRUD for users in the database
    """

    @abstractmethod
    def create(self, user: UserDB, ignore_errors: Optional[bool]=False) -> UserDB:
        """
        Create a new user in the database.

        :user: New user to add to the database.
        :ignore_errors: Whether to ignore errors that the object exists.
            Not useful in prod, but useful for testing.

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
    def get_first(self) -> Union[UserDB, None]:
        """
        Get the first user in the database.
        Useful as a default when not using a multi-user system

        :return: First user in the database; None if there are no users.
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

    @abstractmethod
    def get_all(self) -> List[UserDB]:
        """
        Get all users from the database.

        :return: List of user objects (may be empty)
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

    @abstractmethod
    def get_all(self, users: List[UserDB]) -> List[UserUI]:
        """
        Convert all database users to users for the UI.

        :users: List of database representations of users.

        :return: List of UI representations of the users.
        """
        pass
