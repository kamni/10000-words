"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from pathlib import Path
from typing import Optional, Tuple

from common.stores.adapter import AdapterStore
from common.utils.config import str_to_bool
from common.utils.singleton import Singleton


class BaseDataStore(metaclass=Singleton):
    """
    Handles mangement of the database
    """

    def __init__(self, **kwargs):
        self._initialized = False
        self._data_is_loaded = False
        self._adapter = None

        self.should_load_data = str_to_bool(kwargs.get('loadtestdata'))
        self.initialize()

    @property
    def is_loaded(self):
        return self._data_is_loaded

    @property
    def adapter(self):
        if not self._adapter:
            self._adapter = AdapterStore().get('DataPort')
        return self._adapter

    def initialize(self, force: bool=False):
        if self._initialized and not force:
            return

        self.setup()
        self._initialized = True

    def load_data(self, db_file: Optional[str]=None, force: Optional[bool]=False):
        """
        Load test data into the database, if configured in setup.cfg

        This is function is not intended to be used in production,
        because it uses unsafe/plaintext data.

        :db_file: Path to database file to load, as string.
            If not specified, defaults to DataFile in setup.cfg.
        :force: If True, forces the data to load regardless of config settings.
        """
        if self._data_is_loaded and not force:
            return

        if self.should_load_data or force:
            if db_file:
                db_file = Path(db_file).resolve()

            self.adapter.load(data_file=db_file)
            self._data_is_loaded = True

    def setup(self):
        """
        Perform any necessary steps to connect to or configure the database.
        """
        raise NotImplementedError('BaseDataStore.setup is not implemented')

    def drop(self):
        """
        Clear data in the database
        """
        raise NotImplementedError('BaseDataStore.drop is not implemented')
