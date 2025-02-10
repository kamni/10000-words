"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from fastapi.responses import RedirectResponse
from nicegui import app, ui

from common.models.users import UserUI
from frontend.views.base import BaseView
from frontend.widgets.login import LoginWidget


class LoginView(BaseView):
    """
    A combination login and signup view
    """

    def _get_next_url(self) -> str:
        next_url = app.storage.user.get('referrer_path', '/edit')
        if '_nicegui' in next_url:
            # Fix bug where we sometimes get redirected to static JS
            next_url = '/edit'
        return next_url

    def setup(self):
        if not self._app_settings.is_configured:
            self._redirect = '/configure'
            return False

        self._userdb_adapter = self._adapters.get('UserDBPort')
        self._userui_adapter = self._adapters.get('UserUIPort')

        userdb = self._userdb_adapter.get_first()
        if userdb:
            # Automatic login, if user exists
            if self._app_settings.automatic_login:
                userui = self._userui_adapter.get(userdb)
                app.storage.user.update(userui.model_dump())
                app.storage.user['authenticated'] = True
                self._redirect = self._get_next_url()
                return True
        # We need at least one user in the system
        else:
            self._redirect = '/register'
            return False

        # User already has a session
        if app.storage.user.get('authenticated', False):
            self._redirect = '/edit'
            return True

        self._login_widget = LoginWidget()
        self._page_content.append(self._login_widget)
        return True

    def navigate_back(self):
        # We don't need to handle a 'back' request,
        # because you can't cancel the login.
        self.navigate_next()

    def navigate_next(self):
        next_url = self._get_next_url()
        ui.navigate.to(next_url)
