"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path
from typing import Optional

from ...models.database import Database
from ...ports.data import DataPort
from ...stores.data.in_memory import InMemoryDBStore
from ...utils.files import get_project_dir


class DataInMemoryAdapter(DataPort):
    """
    Handle data in the InMemoryDBStore.
    """

    def __init__(self, **kwargs):
        self.data_file = self.get_filepath(kwargs.get('datafile'))
        self.store = InMemoryDBStore()

    def load(self, data_file: Optional[Path]=None):
        """
        Load data from a TOML file into the database.

        :data_file: Path to the file that should be loaded.
            If not specified, defaults to
            `dev.in_memory.stores.datastore.DataFile` in `setup.cfg`.
        """
        db = self.get_data(data_file or self.data_file)
        self.store.db = db

    def export(self, data_file: Optional[Path]=None):
        """
        Export data to a TOML file from the database.

        :data_file: Path to the file to write the data to.
            If not specified, defaults to
            `dev.in_memory.stores.datastore.DataFile` in `setup.cfg`.
        """
        self.write_data(self.store.db, data_file or self.data_file)
