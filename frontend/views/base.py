"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

import logging
from asgiref.sync import sync_to_async
from collections.abc import Callable
from typing import Any, Dict, List, Optional

from fastapi.responses import RedirectResponse
from nicegui import app, ui

from common.models.settings import AppSettingsUI
from common.models.users import UserUI
from common.stores.adapter import AdapterStore
from frontend.controllers.settings import SettingsController
from frontend.controllers.users import UserController
from frontend.widgets.header import Header


class BaseView:
    """
    Base for all views in the app
    """

    CSS = ''

    def __init__(self):
        self.settings_controller = SettingsController()
        self.user_controller = UserController()
        self.logger = logging.getLogger(__name__)

        self.page_content = []
        self.redirect = None
        self.next_url = None

    @property
    def settings(self):
        return self.settings_controller.get()

    @property
    def user(self):
        return self.user_controller.get()

    def set_style(self):
        """
        Add custom styles to the page.

        NOTE: Widgets also have their own styles,
              so this should rarely be overridden.
        """
        ui.add_css('''
            body {
                --q-primary: #6387cd !important;
                --q-secondary: oklch(.932 .032 255.585) !important;
                --q-accent: rgb(23 37 84 / var(--tw-text-opacity)) !important;
                --q-dark: #1d1d1d !important;
                --q-dark-page: #121212 !important;
                --q-positive: oklch(.627 .194 149.214) !important;
                --q-negative: oklch(.769 .188 70.08) !important;
                --q-info: #c07b80 !important;
                --q-warning: oklch(.852 .199 91.936) !important;
            }
        ''')
        ui.add_css(self.CSS)

    def set_settings(self):
        """
        Put the app settings in an accessible location for the widgets.
        """
        self.settings_controller.set()

    def set_storage(self):
        """
        Set data needed by the widgets.
        This will be available to all widgets.
        """
        pass

    async def display(self) -> Any:
        """
        Show the content of the view.
        Redirect if setup determines user should be somewhere else.
        """
        self.set_settings()
        self.set_storage()
        self.setup()
        self.set_style()

        if self.redirect:
            return RedirectResponse(self.redirect)

        # Allows widgets to signal that they're done with a task,
        # so further actions can be taken by the parent.
        ui.on('done', self.on_done)
        # Allows widgets to signal that the user canceled the task,
        # so that further actions can be taken by the parent.
        ui.on('cancel', self.on_cancel)

        Header().display()
        for content in self.page_content:
            content.display()

    def log_console(self, msg: str):
        """
        Log to the javascript console.

        :msg: What should be logged to the console.
        """
        ui.run_javascript(f'console.log("{msg}")')

    def on_cancel(self):
        """
        Actions to take when a child widget emits a 'cancel' signal.
        By default, this sends the user back to the previous page.
        """
        self.navigate_back()

    def on_done(self):
        """
        Actions to take when a child widget emits a 'done' signal.
        By default, this sends the user to the url defined by self.next_url
        """
        self.navigate_next()

    def navigate_back(self):
        """
        When a user cancels, return to the previous page
        """
        ui.navigate.back()

    def navigate_next(self):
        """
        When a user is done, navigate to the next logical url.
        """
        if self.next_url:
            ui.navigate.to(self.next_url)
        else:
            ui.navigate.back()

    def setup(self):
        """
        Set the widgets or other content to be displayed.
        All content must implement a `display` function.
        """
        pass
