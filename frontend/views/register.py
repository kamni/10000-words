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
            not self.settings.show_registration
            or app.storage.user.get('authenticated', False)
        ):
            self.log_console('foo')
            self.redirect = '/'
            return False

        self.next_url = '/'
        self.page_content.append(RegistrationWidget())
        return True
