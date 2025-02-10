"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from nicegui import app, ui

from common.stores.adapter import AdapterStore
from frontend.views.base import BaseView
from frontend.widgets.configure import ConfigureWidget


class ConfigureView(BaseView):
    """
    Configure the app.

    This view has two modes.
    The first time the app is configured, no login is necessary.
    However, subsequent access requires an admin user.
    """

    def setup(self):
        if self._app_settings.is_configured:
            if not app.storage.user.get('isAdmin', False):
                self._redirect = '/'
                return False
        else:
            existing_user = AdapterStore().get('UserDBPort').get_first()
            # The first time the app is configured,
            # we also want to give the chance to create a new user.
            if not existing_user:
                self._next_url = '/register'

        self._page_content.append(ConfigureWidget())
        return True

