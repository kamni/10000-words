"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import List, Optional, Tuple

from pydantic import BaseModel

from ...models.database import Database
from ...models.documents import DocumentDB
from ...models.settings import AppSettingsDB
from ...models.users import UserDB
from ..config import ConfigStore

from .base import BaseDataStore


class InMemoryDBStore(BaseDataStore):
    """
    An in-memory database for testing and development.
    """

    def _get_blank_database(self) -> Database:
        return Database(users=[], documents=[])

    def get_config(self) -> Tuple[str, str]:
        config = ConfigStore().config
        subsection = 'dev.in_memory'
        return config, subsection

    def setup(self):
        """
        Perform any necessary steps to connect to or configure the database.
        """
        self.db = self._get_blank_database()

    def drop(self):
        """
        Drop all data in the database.
        """
        self.db = self._get_blank_database()
