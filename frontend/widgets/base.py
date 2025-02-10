"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from abc import ABC, abstractmethod

from nicegui import ui

from common.stores.adapter import AdapterStore
from common.stores.app import AppSettingsStore


class BaseWidget(ABC):
    """
    Base for reusable page components

    Implement a `display` method.
    """

    def __init__(self):
        self._adapters = AdapterStore()
        self._app_settings = AppSettingsStore()
        # This can be used to pass objects back to the parent view.
        self._instance = None

    @property
    def instance(self):
        return self._instance

    @abstractmethod
    def display(self):
        """
        Display the content of the widget.
        """
        pass

    def emit_cancel(self):
        """
        Emit an event to the parent view that the user canceled.
        The parent should navigate back to the previous view.
        """
        ui.run_javascript('emitEvent("cancel")')

    def emit_done(self):
        """
        Emit an event to the parent view that the user is done.
        The parent should navigate to the next view in a series of views.
        """
        ui.run_javascript('emitEvent("done")')
