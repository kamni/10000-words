"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from nicegui import app, ui

from common.models.users import UserUI
from frontend.controllers.settings import SettingsController
from frontend.controllers.users import UserController


class BaseWidget(ABC):
    """
    Base for reusable page components

    Implement a `display` method.
    """

    CSS = ''

    def __init__(self):
        self.settings_controller = SettingsController()
        self.user_controller = UserController()
        self.logger = logging.getLogger(__name__)

        self.set_controllers()
        self.set_style()
        self.set_storage()

    @property
    def user(self):
        return self.user_controller.get()

    @property
    def settings(self):
        return self.settings_controller.get()

    @abstractmethod
    def display(self):
        """
        Display the content of the widget.
        """
        pass

    def get_storage(self):
        """
        Returns data from the widget's storage.
        """
        pass

    def set_controllers(self):
        """
        Set up controllers used by the widget.
        """
        pass

    def set_storage(self):
        """
        Sets the data required by the page.
        Called when the widget is first initialized.
        """
        pass

    def update_storage(self, instance: Optional[Any]=None):
        """
        Update the storage.
        Usually done after a new object is created.
        """
        pass

    def set_style(self):
        """
        Adds additional CSS from the self.CSS page.
        """
        ui.add_css(self.CSS)

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

    def log_console(self, msg: str):
        """
        Log to the javascript console.

        :msg: What should be logged to the console.
        """
        ui.run_javascript(f'console.log("{msg}")')

