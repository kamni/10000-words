"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import uuid
from typing import Optional

from .base import GlobalBaseModel, HashableMixin


class UserDB(HashableMixin, GlobalBaseModel):
    """
    Representation of a user in the database.
    """

    id: Optional[uuid.UUID] = None
    username: str
    password: Optional[str] = None
    display_name: Optional[str] = None
    is_admin: Optional[bool] = False

    @property
    def unique_fields(self):
        return ['username']


class UserUI(HashableMixin, GlobalBaseModel):
    """
    Representation of a logged-in user in the UI.
    NOTE: use camel-cased attributes for easier handling with javascript
    """

    id: uuid.UUID
    username: str
    displayName: Optional[str] = None
    isAdmin: Optional[bool] = False
    authenticated: Optional[bool] = False
