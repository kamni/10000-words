"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from typing import List, Optional, Union

from ...models.errors import (
    ObjectExistsError,
    ObjectNotFoundError,
    ObjectValidationError,
)
from ...models.users import UserDB
from ...ports.users import UserDBPort
from ...stores.data.in_memory import InMemoryDBStore


class UserDBInMemoryAdapter(UserDBPort):
    """
    Handles CRUD for users in the database

    NOTE: do not use in production!!!
        This stores user data in plaintext in memory.
    """

    def __init__(self, **kwargs):
        # Ignore any kwargs configuration.
        super().__init__()
        self.store = InMemoryDBStore(subsection='dev.in_memory')

    def _user_to_return_value(self, user: UserDB) -> UserDB:
        # Don't return the password
        userdb = UserDB(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            is_admin=user.is_admin,
        )
        return userdb

    def create(self, user: UserDB, ignore_errors: Optional[bool]=False) -> UserDB:
        """
        Create a new user in the database.

        :user: New user to add to the database.
        :ignore_errors: Whether to ignore errors that the object exists.
            Not useful in prod, but useful for testing.

        :return: Created user object.
        :raises: ObjectExistsError if the object already exists.
        """

        existing_user_filter = list(
            filter(lambda x: x.username == user.username, self.store.db.users),
        )
        if existing_user_filter:
            if not ignore_errors:
                raise ObjectExistsError('User already exists.')
            else:
                new_user = existing_user_filter[0]
        else:
            new_user = user

        if existing_user_filter:
            # Update it
            new_user.password = user.password
            new_user.display_name = user.display_name
            new_user.is_admin = user.is_admin
            new_user.id = user.id
        else:
            new_user.id = uuid.uuid4()
            self.store.db.users.append(new_user)

        # Don't return the password
        userdb = self._user_to_return_value(new_user)
        return userdb

    def get(self, id: str) -> UserDB:
        """
        Get a user from the database using an ID.

        :id: User's UUID.

        :return: Found user object.
        :raises: ObjectNotFoundError if the user does not exist.
        """

        try:
            user = list(filter(lambda x: x.id == id, self.store.db.users))[0]
        except IndexError:
            raise ObjectNotFoundError('User not found')

        userdb = self._user_to_return_value(user)
        return userdb

    def get_first(self) -> Union[UserDB, None]:
        """
        Get the first user in the database.
        Useful as a default when not using a multi-user system

        :return: First user in the database; None if there are no users.
        """

        try:
            user = self.store.db.users[0]
        except IndexError:
            return None

        userdb = self._user_to_return_value(user)
        return userdb

    def get_by_username(self, username: str) -> UserDB:
        """
        Get a user from the database using a username.

        :username: User's username

        :return: Found user object.
        :raises: ObjectNotFoundError
        """

        try:
            user = list(filter(
                lambda x: x.username == username, self.store.db.users,
            ))[0]
        except IndexError:
            raise ObjectNotFoundError('User not found')

        userdb = self._user_to_return_value(user)
        return userdb

    def get_all(self) -> List[UserDB]:
        """
        Get all users from the database.

        :return: List of user objects (may be empty)
        """
        users = self.store.db.users
        usersdb = [
            self._user_to_return_value(user)
            for user in users
        ]
        return usersdb

    def get_password(self, id: uuid.UUID) -> str:
        """
        Get the password of a user.

        NOTE: This is a special method that does not exist on the port,
              and is only applicable to the InMemoryDBStore,
              where we intentionally store passwords in plaintext.
              This method facilitates the in-memory auth adapter.
              Reminder: don't use this in production!!
        """
        try:
            user = list(filter(
                lambda x: x.id == id, self.store.db.users,
            ))[0]
        except IndexError:
            raise ObjectNotFoundError('User not found')
        pass

        return user.password

    def update(self, user: UserDB) -> UserDB:
        """
        Update an existing user.

        Not all fields are editable.
        Here's what you can edit:

        * display_name
        * password
        * is_admin

        :user: UserDB instance to update.
            Must have id.

        :return: Updated UserDB object
        :raises: ObjectNotFoundError
        """

        try:
            userdb = list(filter(
                lambda x: x.id == user.id, self.store.db.users,
            ))[0]
        except IndexError:
            raise ObjectNotFoundError('User not found')

        userdb.display_name = user.display_name
        userdb.is_admin = user.is_admin
        if user.password:
            userdb.password = user.password

        updated_userdb = self._user_to_return_value(userdb)
        return updated_userdb
