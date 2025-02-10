"""
Copyright (C) J Leadbetter <j@jleadbetter.com>
Affero GPL v3
"""

from nicegui import app

from frontend.views.base import BaseView
from frontend.widgets.register import RegistrationWidget


class RegisterView(BaseView):
    """
    Register a new user.
    """

    def setup(self) -> bool:
        if (
            not self._app_settings.show_registration
            or app.storage.user.get('authenticated', False)
        ):
            self._redirect = '/'
            return False

        self._next_url = '/'
        self._page_content.append(RegistrationWidget())
        return True
