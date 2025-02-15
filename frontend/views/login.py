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
        if not self.settings.is_configured:
            self.redirect = '/configure'
            return False

        userdb_adapter = self.adapters.get('UserDBPort')
        userui_adapter = self.adapters.get('UserUIPort')

        userdb = userdb_adapter.get_first()
        if userdb:
            # Automatic login, if user exists
            if self.settings.automatic_login:
                userui = userui_adapter.get(userdb)
                self.user = userui
                self.redirect = self._get_next_url()
                return True
        # We need at least one user in the system
        else:
            self.redirect = '/register'
            return False

        # User already has a session
        if app.storage.user.get('authenticated', False):
            self.redirect = '/edit'
            return True

        self.page_content.append(LoginWidget())
        return True

    def navigate_back(self):
        # We don't need to handle a 'back' request,
        # because you can't cancel the login.
        self.navigate_next()

    def navigate_next(self):
        next_url = self._get_next_url()
        ui.navigate.to(next_url)
