"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import List, Optional, Union

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.utils import IntegrityError

from users.models.profile import UserProfile

from ...models.errors import (
    ObjectExistsError,
    ObjectNotFoundError,
    ObjectValidationError,
)
from ...models.users import UserDB
from ...ports.users import UserDBPort


class UserDBDjangoORMAdapter(UserDBPort):
    """
    Handles CRUD for users in the database
    """

    def __init__(self, **kwargs):
        # Ignore any kwargs configuration.
        # This uses the django profile.
        super().__init__()

    def _django_to_pydantic(self, user: UserProfile) -> UserDB:
        # We don't return the password here,
        # because the hash is relatively useless to us.
        pydantic_user = UserDB(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            is_admin=user.is_admin,
        )
        return pydantic_user

    def create(self, user: UserDB, ignore_errors: Optional[bool]=False) -> UserDB:
        """
        Create a new user in the database.

        :user: New user to add to the database.
        :ignore_errors: Whether to ignore errors that the object exists.
            Not useful in prod, but useful for testing.

        :return: Created user object.
        :raises: ObjectExistsError if the object already exists.
        """

        # We should validate the password *before* we try to create it
        if user.password and not ignore_errors:
            try:
                validate_password(user.password)
            except ValidationError as exc:
                raise ObjectValidationError(exc.messages)

        if user.id and not ignore_errors:
            raise ObjectValidationError(
                'New users should not have an id. '
                'This will be generated by the database.'
            )

        try:
            existing_user = User.objects.get(username=user.username)
        except User.DoesNotExist:
            existing_user = None

        new_user = None
        if existing_user:
            if not ignore_errors:
                raise ObjectExistsError('User already exists')
            else:
                new_user = existing_user
        if not new_user:
            new_user = User.objects.create(username=user.username)

        if user.password:
            new_user.set_password(user.password)

        if user.is_admin:
            new_user.is_staff = True
            new_user.is_superuser = True

        new_user.save()

        existing_profiles = UserProfile.objects.filter(
            Q(id=user.id) | Q(user__username=user.username)
        )
        if not existing_profiles.count():
            existing_profile = None
        elif existing_profiles.count() > 1:
            raise ObjectExistsError(
                'Duplicate user profiles exist. '
                'Contact the admin.'
            )
        else:
            existing_profile = existing_profiles.first()

        new_profile = None
        if existing_profile:
            if not ignore_errors:
                raise ObjectExistsError('User profile already exists')
            else:
                new_profile = existing_profile
        if not new_profile:
            new_profile = UserProfile.objects.create(
                user=new_user,
                display_name=user.display_name,
            )

        if ignore_errors and user.id:
            # Let's make sure the existing profile is up to date
            new_profile.display_name = user.display_name
            new_profile.save()

        new_user_db = self._django_to_pydantic(new_profile)
        return new_user_db

    def get(self, id: str) -> UserDB:
        """
        Get a user from the database using an ID.

        :id: User's UUID.

        :return: Found user object.
        :raises: ObjectNotFoundError if the user does not exist.
        """

        try:
            profile = UserProfile.objects.get(
                id=id,
                user__is_active=True,
            )
        except UserProfile.DoesNotExist as exc:
            raise ObjectNotFoundError(exc)

        user = self._django_to_pydantic(profile)
        return user

    def get_first(self) -> Union[UserDB, None]:
        """
        Get the first user in the database.
        Useful as a default when not using a multi-user system

        :return: First user in the database; None if there are no users.
        """

        user = UserProfile.objects.filter(
            user__is_active=True,
        ).first()
        userdb = self._django_to_pydantic(user) if user else None
        return userdb

    def get_by_username(self, username: str) -> UserDB:
        """
        Get a user from the database using a username.

        :username: User's username

        :return: Found user object.
        :raises: ObjectNotFoundError
        """

        try:
            profile = UserProfile.objects.get(
                user__username=username,
                user__is_active=True,
            )
        except UserProfile.DoesNotExist as exc:
            raise ObjectNotFoundError(exc)

        user = self._django_to_pydantic(profile)
        return user

    def get_all(self) -> List[UserDB]:
        """
        Get all users from the database.

        :return: List of user objects (may be empty)
        """
        users = UserProfile.objects.filter(user__is_active=True)
        usersdb = [self._django_to_pydantic(user) for user in users]
        return usersdb

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
            userdb = UserProfile.objects.get(id=user.id)
        except Exception as exc:
            raise ObjectNotFoundError(exc)

        userdb.display_name = user.display_name
        userdb.user.is_superuser = user.is_admin
        if user.password:
            userdb.user.set_password(user.password)

        userdb.user.save()
        userdb.save()

        updated_user = UserProfile.objects.get(id=user.id)
        updated_user_db = self._django_to_pydantic(updated_user)
        return updated_user_db
