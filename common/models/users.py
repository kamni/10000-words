"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import time
import uuid
from typing import Any, Optional

from pydantic import BaseModel

from .base import HashableMixin


class UserBase(HashableMixin):
    """
    Shared base class for both Pydantic and Django models for the database.

    Must implement the following fields:

    * id
    * user (with user.id)
    * language_code
    """
    pass


class UserDB(UserBase, BaseModel):
    """
    Representation of a user in the database.
    """

    id: Optional[str] = None
    username: str
    password: Optional[str] = None
    email: Optional[str] = None
    display_name: str

    @property
    def unique_fields(self):
        return ['username']


class UserUI(UserBase, BaseModel):
    """
    Representation of a logged-in user in the UI.
    NOTE: use camel-cased attributes for easier handling with javascript
    """

    id: str  # UUID
    username: str
    displayName: Optional[str] = None

    @classmethod
    def from_db(cls, user: UserDB) -> 'UserUI':
        """
        Convert a database user into a UI-friendly user object.

        :user: User object from the database
        :return: UserDisplay for the UI.
        """

        user_ui = cls(
            id=user.id,
            username=user.username,
            displayName=user.display_name or user.username,
        )
        return user_ui
