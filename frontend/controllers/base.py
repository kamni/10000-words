"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import logging

from common.stores.adapter import AdapterStore


class BaseController:
    """
    Control the state of the application
    """

    def __init__(self):
        self.adapters = AdapterStore()
        self.logger = logging.getLogger(__name__)
        self._backend_adapter = None
        self._frontend_adapter = None

    @property
    def backend_adapter(self):
        """
        Access the primary backend adapter for a controller
        """
        raise NotImplementedError('BaseController.backend_adapter not implemented')

    @property
    def frontend_adapter(self):
        """
        Access the primary frontend adapter for a controller
        """
        raise NotImplementedError('BaseController.frontend_adapter not implemented')
