"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from asgiref.sync import sync_to_async
from collections.abc import Callable
from typing import Any, List, Optional

from fastapi.responses import RedirectResponse
from nicegui import ui

from common.stores.adapter import AdapterStore
from common.stores.app import AppSettingsStore
from frontend.widgets.header import Header


class BaseView:
    """
    Base for all views in the app
    """

    def __init__(self):
        self._adapters = AdapterStore()
        self._app_settings = AppSettingsStore()

        self._page_content = []
        self._redirect = None
        self._next_url = None

    def set_style(self):
        ui.add_css('''
            body {
                --q-primary: #6387cd !important;
                --q-secondary: oklch(.932 .032 255.585) !important;
                --q-accent: #ac6cb0 !important;
                --q-dark: #1d1d1d !important;
                --q-dark-page: #121212 !important;
                --q-positive: oklch(.627 .194 149.214) !important;
                --q-negative: oklch(.769 .188 70.08) !important;
                --q-info: #c07b80 !important;
                --q-warning: oklch(.852 .199 91.936) !important;
            }
        ''')

    async def display(self) -> Any:
        """
        Show the content of the view.
        Redirect if setup determines user should be somewhere else.
        """

        self.set_style()
        self.setup()

        if self._redirect:
            return RedirectResponse(self._redirect)

        ui.on('done', self.navigate_next)
        ui.on('cancel', self.navigate_back)

        Header().display()
        for content in self._page_content:
            content.display()

    def navigate_back(self):
        """
        When a user cancels, return to the previous page
        """
        ui.navigate.back()

    def navigate_next(self):
        """
        When a user is done, navigate to the next logical url.
        """
        if self._next_url:
            ui.navigate.to(self._next_url)
        else:
            ui.navigate.back()

    def setup(self):
        """
        Set the widgets or other content to be displayed.
        All content must implement a `display` function.
        """
        pass
