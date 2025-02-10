"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import List, Optional

from pydantic import BaseModel

from common.models.app import AppSettingsDB
from common.models.users import UserDB
from common.utils.singleton import Singleton


class Database(BaseModel):
    """
    Representation of an in-memory database
    """

    app_settings: Optional[AppSettingsDB] = None
    users: List[UserDB]


class InMemoryDBStore(metaclass=Singleton):
    """
    An in-memory database for testing and development.
    """

    def __init__(self):
        self.db = Database(users=[])

    def drop(self):
        """
        Drop all data in the database.
        """
        self.db = Database(users=[])
