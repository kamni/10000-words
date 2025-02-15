"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import List, Optional

from pydantic import BaseModel

from .documents import DocumentDB
from .settings import AppSettingsDB
from .users import UserDB


class Database(BaseModel):
    """
    Representation of a database as a pydantic model.
    Used by the DataLoader and the InMemoryDatabase.
    """

    app_settings: Optional[AppSettingsDB] = None
    users: List[UserDB]
    documents: List[DocumentDB]
