"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from django.contrib.auth.models import User
from django.db.utils import IntegrityError

from words.models.users import UserSettings

from ..models.errors import ObjectExistsError, ObjectNotFoundError
from ..models.users import UserDB, UserUI
from ..ports.users import UserDBPort, UserUIPort


class UserDBDjangoORMAdapter(UserDBPort):
    """
    Handles CRUD for users in the database
    """

    def __init__(self, **kwargs):
        # Ignore any kwargs configuration.
        # This uses the django settings.
        super().__init__()

    def _django_to_pydantic(self, user: UserSettings) -> UserDB:
        pydantic_user = UserDB(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            password=user.password,
        )
        return pydantic_user

    def create(self, user: UserDB) -> UserDB:
        """
        Create a new user in the database.

        :user: New user to add to the database.

        :return: Created user object.
        :raises: ObjectExistsError if the object already exists.
        """

        try:
            new_user = User.objects.create(username=user.username)
        except IntegrityError as exc:
            raise ObjectExistsError(exc)

        if user.password:
            new_user.set_password(user.password)
            new_user.save()

        # The user is unique on a UserSettings model.
        # We don't have to worry about a duplicate user,
        # because it would have failed in the previous try-except block.
        new_settings = UserSettings.objects.create(
            user=new_user,
            display_name=user.display_name,
        )

        new_user_db = self._django_to_pydantic(new_settings)
        return new_user_db

    def get(self, id: str) -> UserDB:
        """
        Get a user from the database using an ID.

        :id: User's UUID.

        :return: Found user object.
        :raises: ObjectNotFoundError if the user does not exist.
        """

        try:
            settings = UserSettings.objects.get(id=id)
        except UserSettings.DoesNotExist as exc:
            raise ObjectNotFoundError(exc)

        user = self._django_to_pydantic(settings)
        return user

    def get_by_username(self, username: str) -> UserDB:
        """
        Get a user from the database using a username.

        :username: User's username

        :return: Found user object.
        :raises: ObjectNotFoundError
        """

        try:
            settings = UserSettings.objects.get(user__username=username)
        except UserSettings.DoesNotExist as exc:
            raise ObjectNotFoundError(exc)

        user = self._django_to_pydantic(settings)
        return user


class UserUIDjangoORMAdapter(UserUIPort):
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

