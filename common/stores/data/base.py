"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from typing import Optional, Tuple

from common.utils.config import str_to_bool
from common.utils.data import DataLoader
from common.utils.singleton import Singleton


class BaseDataStore(metaclass=Singleton):
    """
    Handles mangement of the database
    """

    def __init__(self, **kwargs):
        self.setup()
        self.should_load_data = str_to_bool(kwargs.get('loadtestdata'))
        self._data_is_loaded = False

    @property
    def is_loaded(self):
        return self._data_is_loaded

    def load_data(self, force: Optional[bool]=False):
        """
        Load test data into the database, if configured in setup.cfg

        This is function is not intended to be used in production,
        because it uses unsafe/plaintext data.

        :force: If True, forces the data to load regardless of config settings.
            WARNING: This can override AppStore configuration in a live system.
        """
        if self._data_is_loaded and not force:
            return

        if self.should_load_data or force:
            config, subsection = self.get_config()
            DataLoader(config, subsection, force).load()
            self._data_is_loaded = True

    def get_config(self) -> Tuple[str, str]:
        """
        Get the configuration that is used by this data store.
        """
        raise NotImplementedError('BaseDataStore.get_config is not Implemented')

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
