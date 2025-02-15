"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from nicegui import app, ui

from common.models.settings import AppSettingsUI
from common.models.users import UserUI
from common.stores.adapter import AdapterStore


class BaseWidget(ABC):
    """
    Base for reusable page components

    Implement a `display` method.
    """

    CSS = ''

    def __init__(self):
        self.adapters = AdapterStore()

        self.set_style()
        self.set_storage()

    @property
    def user(self):
        user_dict = app.storage.user
        user = UserUI(**user_dict)
        return user

    @user.setter
    def user(self, user: UserUI):
        app.storage.user.update(user.model_dump())
        app.storage.user['authenticated'] = True

    @property
    def settings(self):
        settings_dict = app.storage.client.get('settings', {})
        settings = AppSettingsUI(**settings_dict)
        return settings

    @settings.setter
    def settings(self, settings: AppSettingsUI):
        app.storage.client['settings'] = settings.model_dump()

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

