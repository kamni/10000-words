"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import importlib
import os
from typing import Any, Dict, Optional

from ..models.settings import AppSettingsDB
from ..stores.config import ConfigStore
from ..utils.singleton import Singleton


class StoreInitializationError(Exception):
    """
    Indicates that a store failed to initialize.
    Raised during AppStore.initialize.
    """
    pass


class StoreNotFoundError(Exception):
    """
    Indicates that a store was not found.
    Raised during AppStore.get_store.
    """
    pass



class AppStore(metaclass=Singleton):
    """
    Initializes and provides access to all stores in the application.
    This should be one of the first things initialized while running the app.

    NOTE: Only initialize the AppStore.
          Except when testing, don't manually initialize other stores.
    """

    STORES = ['datastore', 'adapterstore']

    def __init__(
        self,
        config: Optional[str]=None,
        subsection: Optional[str]=None,
        wait_to_initialize: Optional[bool]=False,
    ):
        """
        :config: setup.cfg to use to create adapters
        :subsection: subsection of setup.cfg to use for settings
        :wait_to_initialize: the init will not call `initialize` if True.
            Sometimes we want to delay setup until first use.
            If True, won't initialize until `get` is called.
        """
        self._config_file = config
        self._subsection = subsection
        self._stores = {}
        self._config = None
        self._initialized = False

        if not wait_to_initialize:
            self.initialize()

    @property
    def stores(self):
        return self._stores

    def initialize(self, force: Optional[bool]=False):
        """
        Initialize the stores that will be used for the app.

        :force: initialize, even if it has already been initialized.
            If False, will skip the creation of already-initialized stores.
        """

        if self._initialized and not force:
            return

        if force:
            for store in self._stores.values():
                Singleton.destroy(store.__class__)
            self._stores = {}

        config_store = ConfigStore(
            config=self._config_file,
            subsection=self._subsection,
        )
        self._config = config_store
        self._stores['configstore'] = config_store

        init_script = self._config.get('', 'InitScript')
        if init_script:
            script = self._get_init_script(init_script)
            script()

        exceptions = {}
        for store in self.STORES:
            try:
                if not store in self._stores:
                    self._stores[store] = self._make_store(store)
            except Exception as exc:
                exceptions[store] = exc

        if exceptions:
            raise StoreInitializationError(str(exceptions))

        self._initialized=True

    @classmethod
    def destroy_all(cls):
        """
        Clear all stores.
        Wrapper around Singleton.destroy_all

        NOTE: If you only want to update a single store,
            just call store.initialize(force=True)
        """
        Singleton.destroy_all()

    def get(self, store_name: str):
        """
        Get a configured store
        """
        if not self._initialized:
            self.initialize()

        key = store_name.lower()
        try:
            store = self._stores[key]
        except KeyError:
            raise StoreNotFoundError(f'Store {store_name} not found')

        return store

    def _get_init_script(self, initialize_script: str):
        script_path, script_name = initialize_script.rsplit('.', 1)
        module = importlib.import_module(script_path)
        script = getattr(module, script_name)
        return script

    def _get_store_options(self, store_name: str) -> Dict[str, Any]:
        options = {}

        common_key = 'stores.common'
        general_opts = self._config.get(common_key, default=[])
        for key in general_opts:
            value = self._config.get(common_key, key)
            options[key] = value

        store_key = f'stores.{store_name}'
        store_opts = self._config.get(store_key, default=[])
        for key in store_opts:
            value = self._config.get(store_key, key)
            options[key] = value

        return options

    def _get_store_cls(self, store_name: str) -> Any:
        config_option = self._config.get('stores', store_name)
        try:
            module_name, cls_name = config_option.rsplit('.', 1)
        except :
            raise StoreNotFoundError(
                f'Configuration missing for store {store_name} '
                f'in subsection {config.subsection}'
            )
        module = importlib.import_module(module_name)
        StoreCls = getattr(module, cls_name)
        return StoreCls

    def _make_store(self, store_name: str) -> Any:
        StoreCls = self._get_store_cls(store_name)
        options = self._get_store_options(store_name)
        store = StoreCls(**options)
        return store
