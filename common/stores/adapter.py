"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import configparser
import importlib
import os
import sys
from typing import Any, Dict, Optional

from common.stores.config import ConfigStore
from common.utils.singleton import Singleton


class AdapterInitializationError(Exception):
    """
    Indicates that an adapter failed to initialize.
    Raised during Adapteradapter.initialize.
    """
    pass


class AdapterNotFoundError(Exception):
    """
    Indicates that an adapter was not found.
    Raised during Adapteradapter.get.
    """
    pass


class AdapterStore(metaclass=Singleton):
    """
    Singleton that instantiates all adapters using the specified config
    """

    def __init__(self):
        self._adapters = {}
        self._config = ConfigStore()
        self.initialize()

    def initialize(self, force: bool=False):
        """
        Initialize adapters for use in the app.

        This is done as a separate step from __init__
        so we can troubleshoot individual adapter initializations.

        :force: Re-import the adapters.
            If false, ignores build if adapters already exist.
        """

        if force:
            self._adapters = {}

        ports = self._config.get('ports', default=[])
        port_exceptions = {}
        for port in ports:
            # Don't override existing adapters
            if port in self._adapters:
                continue

            try:
                adapter = self._make_adapter(port)
                self._adapters[port] = adapter
            except Exception as exc:
                port_exceptions[port] = exc

        if port_exceptions:
            raise AdapterInitializationError(str(port_exceptions))

    def get(self, port_name: str) -> Any:
        """
        Return the expected adapter base

        :port_name: name of the port class (e.g., 'AuthnPort')

        :return: the configured adapter for the port
        :raise: AdapterNotFoundError, if port is not configured
        """

        try:
            adapter = self._adapters[port_name.lower()]
        except KeyError:
            raise AdapterNotFoundError(f'Unable to find adapter for {port_name}.')

        return adapter

    def _get_adapter_options(self, adapter_name: str) -> Dict[str, Any]:
        options = {}

        common_key = 'adapters.common'
        general_opts = self._config.get(common_key, default=[])
        for key in general_opts:
            value = self._config.get(common_key, key)
            options[key] = value

        adapter_key = f'adapters.{adapter_name}'
        adapter_opts = self._config.get(adapter_key, default=[])
        for key in adapter_opts:
            value = self._config.get(adapter_key, key)
            options[key] = value

        return options

    def _get_adapter_cls(self, adapter_name: str) -> Any:
        config_option = self._config.get('ports', adapter_name)
        module_name, cls_name = config_option.rsplit('.', 1)
        module = importlib.import_module(module_name)
        AdapterCls = getattr(module, cls_name)
        return AdapterCls

    def _make_adapter(self, adapter_name: str):
        AdapterCls = self._get_adapter_cls(adapter_name)
        options = self._get_adapter_options(adapter_name)
        adapter = AdapterCls(**options)
        return adapter
